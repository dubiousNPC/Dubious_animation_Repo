"""Rewrites the Lua `goto continue` idiom into Luau-compatible control flow.

Why
---
OpenMW's default build runs LuaJIT, where `goto` and `::label::` are Lua 5.2 features that
work. A Luau build has neither, and rejects the file with

    Lua error: [string "<file>"]:N: Incomplete statement: expected assignment or a function call

because `goto` parses as a plain identifier, `continue` follows it, and the result is an
expression statement that is neither a call nor an assignment. The message never names
`goto`, and it points at the `goto` line rather than at anything that looks wrong, which is
why this is hard to find by reading the error.

The script does not just fail to parse - it never starts. In the 2026-10-14 log that took
out ReAnimation's API, SkillFramework, LuaPhysics, MercyCAO and Pursuit, and the ~130
downstream `attempt to index nil` errors are mods that depended on them.

The transform
-------------
Only one shape is rewritten, the "continue" idiom: a label as the final statement of a loop
body, with every `goto` to it inside that same body.

    for ... do                      for ... do
        if a then goto continue end     repeat
        work()                              if a then break end
        ::continue::                        work()
    end                                 until true
                                    end

`repeat ... until true` executes once, so `break` inside it lands exactly where the label
was. This is the standard pre-5.2 Lua idiom and is behaviour-preserving for this shape:
`return` still returns from the function, and an outer `break` would change meaning - which
is why one in the body makes the tool refuse.

Anything else is refused rather than guessed at, and the reason is printed:

  * a label that is not the last statement of its loop body (a backward jump, a retry loop)
  * a `goto` whose label is outside the loop body it sits in
  * more than one label in the same loop body
  * a `break` already in that body at the loop's own nesting level
  * a label not inside any loop at all

Usage
    python3 -I degoto.py <file-or-dir> ... [--write] [--backup]

Without --write it prints what it would do and changes nothing. Validate the result with
luacheck.py (liblua5.4 via ctypes), and re-run find_goto.py to confirm nothing is left.
"""
import argparse
import os
import re
import sys

KEYWORD = re.compile(r"(?<![\w.:])(do|then|end|function|if|while|for|repeat|until|break|else|elseif|return|goto)(?![\w])")
LABEL = re.compile(r"::\s*([A-Za-z_]\w*)\s*::")
GOTO = re.compile(r"(?<![\w.:])goto\s+([A-Za-z_]\w*)")


def strip_noise(text):
    """Blank comments and string literals, preserving offsets and newlines."""
    out = list(text)
    length = len(text)
    index = 0

    def blank(start, stop):
        for position in range(start, min(stop, length)):
            if out[position] != "\n":
                out[position] = " "

    while index < length:
        char = text[index]
        if char == "-" and text.startswith("--", index):
            long_form = re.match(r"--\[(=*)\[", text[index:])
            if long_form:
                closer = "]" + long_form.group(1) + "]"
                end = text.find(closer, index)
                end = length if end < 0 else end + len(closer)
            else:
                end = text.find("\n", index)
                end = length if end < 0 else end
            blank(index, end)
            index = end
            continue
        if char == "[":
            long_string = re.match(r"\[(=*)\[", text[index:])
            if long_string:
                closer = "]" + long_string.group(1) + "]"
                end = text.find(closer, index)
                end = length if end < 0 else end + len(closer)
                blank(index, end)
                index = end
                continue
        if char in "\"'":
            cursor = index + 1
            while cursor < length:
                if text[cursor] == "\\":
                    cursor += 2
                    continue
                if text[cursor] == char or text[cursor] == "\n":
                    cursor += 1
                    break
                cursor += 1
            blank(index, cursor)
            index = cursor
            continue
        index += 1
    return "".join(out)


class Loop:
    """A loop body: where it opens, where it closes, and its nesting depth."""

    def __init__(self, kind, body_start, open_token_start):
        self.kind = kind                  # 'for' | 'while' | 'repeat'
        self.body_start = body_start      # first offset inside the body
        self.open_token_start = open_token_start
        self.body_end = None              # offset of the closing 'end' / 'until'
        self.breaks = []                  # break offsets at this loop's own level


def find_loops(clean):
    """Every loop body in the file, with its extent and its own-level `break`s.

    Blocks are tracked with a stack of (kind, loop-or-None). `do`/`then`/`function` open a
    block that `end` closes; `repeat` is closed by `until`. A `for`/`while` header's `do` is
    what opens its body, so the pending loop keyword is remembered until that `do` arrives.
    """
    stack = []
    loops = []
    pending = None  # 'for' or 'while' seen, waiting for its 'do'

    for match in KEYWORD.finditer(clean):
        word = match.group(1)
        start, end = match.span()

        if word in ("for", "while"):
            pending = word
        elif word == "do":
            if pending:
                loop = Loop(pending, end, start)
                loops.append(loop)
                stack.append(("loop", loop))
                pending = None
            else:
                stack.append(("do", None))
        elif word == "repeat":
            loop = Loop("repeat", end, start)
            loops.append(loop)
            stack.append(("loop", loop))
        elif word in ("then", "function"):
            stack.append((word, None))
        elif word == "elseif":
            # `elseif` closes the previous `then` block and a new `then` opens the next.
            if stack and stack[-1][0] == "then":
                stack.pop()
        elif word in ("end", "until"):
            if not stack:
                continue
            kind, loop = stack.pop()
            if loop is not None:
                loop.body_end = start
        elif word == "break":
            for kind, loop in reversed(stack):
                if kind == "function":
                    break           # a break inside a nested function is not ours
                if kind == "loop":
                    loop.breaks.append(start)
                    break

    return [loop for loop in loops if loop.body_end is not None]


def line_of(clean, offset):
    return clean.count("\n", 0, offset) + 1


def plan(path):
    """Returns (source, [edits], [refusals]). Each edit is (start, stop, replacement)."""
    source = open(path, encoding="utf-8", errors="replace").read()
    clean = strip_noise(source)

    labels = [(m.start(), m.end(), m.group(1)) for m in LABEL.finditer(clean)]
    gotos = [(m.start(), m.end(), m.group(1)) for m in GOTO.finditer(clean)]
    if not labels and not gotos:
        return source, [], []

    loops = find_loops(clean)
    edits = []
    refusals = []

    def enclosing(offset):
        """Loops containing `offset`, innermost first."""
        containing = [l for l in loops if l.body_start <= offset < l.body_end]
        return sorted(containing, key=lambda l: -l.body_start)

    # A loop's "end label" is a label that is the final statement of its body. Lua scopes
    # labels per block, so a `goto` binds to the nearest enclosing one of that name - which
    # is what lets several functions in one file each have their own `::continue::`.
    end_label = {}
    for label_start, label_end, name in labels:
        chain = enclosing(label_start)
        if not chain:
            refusals.append("line %d: ::%s:: is not inside a loop"
                            % (line_of(clean, label_start), name))
            continue
        loop = chain[0]
        if clean[label_end:loop.body_end].strip():
            refusals.append("line %d: ::%s:: is not the last statement of its loop body "
                            "(code follows it)" % (line_of(clean, label_start), name))
            continue
        if loop in end_label:
            refusals.append("line %d: ::%s:: shares its loop body with another end label"
                            % (line_of(clean, label_start), name))
            continue
        end_label[loop] = (label_start, label_end, name)

    def owner_of(goto_start, name):
        """The loop whose end label this goto binds to, or None."""
        for loop in enclosing(goto_start):
            labelled = end_label.get(loop)
            if labelled and labelled[2] == name:
                return loop
        return None

    bound = {}
    for goto_start, goto_end, name in gotos:
        loop = owner_of(goto_start, name)
        if loop is not None:
            bound.setdefault(loop, []).append((goto_start, goto_end, name))

    handled_gotos = set()
    for loop, (label_start, label_end, name) in sorted(end_label.items(),
                                                       key=lambda kv: kv[0].body_start):
        inside = bound.get(loop, [])
        if not inside:
            refusals.append("line %d: ::%s:: has no goto bound to it"
                            % (line_of(clean, label_start), name))
            continue

        siblings = [l for l in labels
                    if l[0] != label_start and loop.body_start <= l[0] < loop.body_end]
        if siblings:
            refusals.append("line %d: ::%s:: shares its loop body with %d other label(s)"
                            % (line_of(clean, label_start), name, len(siblings)))
            continue

        if loop.breaks:
            refusals.append("line %d: ::%s:: - the loop body already contains break at line(s) %s, "
                            "which would bind to the inserted repeat"
                            % (line_of(clean, label_start), name,
                               ", ".join(str(line_of(clean, b)) for b in loop.breaks)))
            continue

        # Indentation for the inserted keywords, taken from the label's own line.
        label_line_start = clean.rfind("\n", 0, label_start) + 1
        indent = re.match(r"[ \t]*", source[label_line_start:]).group(0)

        edits.append((loop.body_start, loop.body_start, "\n" + indent + "repeat"))
        for goto_start, goto_end, _ in inside:
            edits.append((goto_start, goto_end, "break"))
            handled_gotos.add(goto_start)
        # Replace the label itself, plus the run of whitespace before it, with `until true`.
        edits.append((label_line_start, label_end, indent + "until true"))

    for goto_start, goto_end, name in gotos:
        if goto_start in handled_gotos:
            continue
        if owner_of(goto_start, name) is None:
            refusals.append("line %d: goto %s binds to no end-of-loop label"
                            % (line_of(clean, goto_start), name))
        else:
            refusals.append("line %d: goto %s left in place because its loop was refused"
                            % (line_of(clean, goto_start), name))

    return source, edits, refusals


def apply_edits(source, edits):
    for start, stop, replacement in sorted(edits, key=lambda e: e[0], reverse=True):
        source = source[:start] + replacement + source[stop:]
    return source


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--write", action="store_true", help="modify files in place")
    parser.add_argument("--backup", action="store_true", help="keep <file>.orig next to each rewrite")
    args = parser.parse_args()

    files = []
    for path in args.paths:
        if os.path.isdir(path):
            for dirpath, _, names in os.walk(path):
                files += [os.path.join(dirpath, n) for n in sorted(names) if n.lower().endswith(".lua")]
        else:
            files.append(path)

    rewritten = refused = 0
    for path in files:
        source, edits, refusals = plan(path)
        if not edits and not refusals:
            continue
        print(path)
        if edits:
            loops = sum(1 for e in edits if e[2].endswith("repeat"))
            breaks = sum(1 for e in edits if e[2] == "break")
            print("    rewrite %d loop(s), %d goto -> break" % (loops, breaks))
        for reason in refusals:
            print("    REFUSED %s" % reason)
        if refusals:
            refused += 1
        if edits and args.write:
            if args.backup:
                with open(path + ".orig", "w", encoding="utf-8") as handle:
                    handle.write(source)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(apply_edits(source, edits))
            rewritten += 1

    print("\n%d file(s) %s, %d with refusals"
          % (rewritten, "rewritten" if args.write else "would be rewritten", refused))
    return 0


if __name__ == "__main__":
    sys.exit(main())

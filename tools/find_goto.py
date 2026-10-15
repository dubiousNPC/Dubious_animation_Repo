"""Finds Lua `goto` statements and `::label::` definitions.

Luau has neither. OpenMW's default build runs LuaJIT, where `goto` is a 5.2 extension that
works, so a mod using it loads fine there and fails to parse on a Luau build with:

    Lua error: [string "<file>"]:N: Incomplete statement: expected assignment or a function call

`goto` is parsed as a plain identifier, `continue` follows it, and the result is an
expression statement that is neither a call nor an assignment - hence the wording, which
points at the line but never names `goto`.

Strings and comments are blanked before matching so a `goto` inside either is not reported.
"""
import os, re, sys

GOTO = re.compile(r'(?<![\w.:])goto\s+([A-Za-z_]\w*)')
LABEL = re.compile(r'::\s*([A-Za-z_]\w*)\s*::')

def strip_noise(text):
    """Blank long/short comments and string literals, keeping byte offsets and newlines."""
    out = list(text)
    i = 0
    n = len(text)
    def blank(a, b):
        for k in range(a, min(b, n)):
            if out[k] != '\n':
                out[k] = ' '
    while i < n:
        c = text[i]
        if c == '-' and text.startswith('--', i):
            m = re.match(r'--\[(=*)\[', text[i:])
            if m:
                close = ']' + m.group(1) + ']'
                end = text.find(close, i)
                end = n if end < 0 else end + len(close)
            else:
                end = text.find('\n', i)
                end = n if end < 0 else end
            blank(i, end); i = end; continue
        if c == '[':
            m = re.match(r'\[(=*)\[', text[i:])
            if m:
                close = ']' + m.group(1) + ']'
                end = text.find(close, i)
                end = n if end < 0 else end + len(close)
                blank(i, end); i = end; continue
        if c in '"\'':
            j = i + 1
            while j < n:
                if text[j] == '\\':
                    j += 2; continue
                if text[j] == c or text[j] == '\n':
                    j += 1; break
                j += 1
            blank(i, j); i = j; continue
        i += 1
    return ''.join(out)

total_files = 0
hits = []
for base in sys.argv[1:]:
    for dirpath, _, files in os.walk(base):
        for f in sorted(files):
            if not f.lower().endswith('.lua'):
                continue
            path = os.path.join(dirpath, f)
            try:
                raw = open(path, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            total_files += 1
            clean = strip_noise(raw)
            gotos = [(clean[:m.start()].count('\n') + 1, m.group(1)) for m in GOTO.finditer(clean)]
            labels = [(clean[:m.start()].count('\n') + 1, m.group(1)) for m in LABEL.finditer(clean)]
            if gotos or labels:
                hits.append((path, gotos, labels))

for path, gotos, labels in hits:
    print('  %s' % path)
    for line, name in gotos:
        print('      line %-5d goto %s' % (line, name))
    for line, name in labels:
        print('      line %-5d ::%s::' % (line, name))
print('\n%d lua files scanned, %d using goto/labels' % (total_files, len(hits)))

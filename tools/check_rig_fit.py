"""Checks each .kf against what its target skeleton actually has.

The per-skeleton missing sets are read off an openmw log, not guessed: a bone is absent
from a rig only when the engine says so for that rig. Derived from the 2026-10-14 log
(OpenMW 0.52, 94,411 lines, 89,544 bone warnings):

  xbase_anim, xbase_anim_female (3rd person human) lack the 18 extended Biped finger
      joints, Bip01 L/R Toe0, and Bip01 Tail/Tail1-3
  xbase_animkna (3rd person beast)                lack the 18 extended finger joints only
                                                  - it HAS Toe0 and the tail bones
  every *.1st rig                                 lack nothing; no .1st skeleton appears
                                                  anywhere in the log

So the same bone name is a defect in one folder and correct in the next. Folders are
matched by name; an unrecognised folder is reported, not guessed at.
"""
import os, sys
sys.path.insert(0, os.environ['FBACOMPAT_TOOLS'])
import nifkf

EXT_FINGERS = {'bip01 %s finger%s' % (s, j)
               for s in ('l', 'r') for j in ('02','12','22','3','31','32','4','41','42')}
TOES = {'bip01 l toe0', 'bip01 r toe0'}
TAIL = {'bip01 tail', 'bip01 tail1', 'bip01 tail2', 'bip01 tail3'}

# animation folder -> bones its skeleton(s) do not have
ABSENT = {
    'xbase_anim':         EXT_FINGERS | TOES | TAIL,
    'xbase_anim_female':  EXT_FINGERS | TOES | TAIL,
    'xbase_animkna':      EXT_FINGERS,
    'base_anim':          EXT_FINGERS | TOES | TAIL,
    'base_anim_female':   EXT_FINGERS | TOES | TAIL,
    'base_animkna':       EXT_FINGERS,
    'xbase_anim.1st':         set(),
    'xbase_anim_female.1st':  set(),
    'xbase_animkna.1st':      set(),
    'base_anim.1st':          set(),
    'base_anim_female.1st':   set(),
    'base_animkna.1st':       set(),
}

def rig_bone(name):
    """Entry 0 names a real rig bone rather than a stray armature object."""
    low = name.strip().lower()
    return low == 'bip01' or low.startswith('bip01 ')

bad = 0
checked = 0
unknown_folders = set()
for base in sys.argv[1:]:
    for dirpath, _, files in os.walk(base):
        folder = os.path.basename(dirpath)
        kfs = sorted(f for f in files if f.lower().endswith('.kf'))
        if not kfs:
            continue
        if folder not in ABSENT:
            unknown_folders.add(dirpath)
            continue
        absent = ABSENT[folder]
        for f in kfs:
            path = os.path.join(dirpath, f)
            try:
                kf = nifkf.KF.load(path)
            except Exception as error:
                print('  %-34s UNREADABLE: %s' % (f, error))
                bad += 1
                continue
            checked += 1
            names = [p['value'] for t, p in kf.blocks if t == 'NiStringExtraData']
            offending = sorted(b for b in kf.bone_data if b.strip().lower() in absent)
            root = names[0] if names else '(none)'
            problems = []
            if offending:
                problems.append('%d bone(s) the %s rig lacks: %s'
                                % (len(offending), folder,
                                   ', '.join(b.replace('Bip01 ', '') for b in offending)))
            if not rig_bone(root):
                problems.append('root entry 0 is %r, not a rig bone' % root)
            if problems:
                bad += 1
                print('  %-20s %-34s %s' % (folder, f, problems[0]))
                for extra in problems[1:]:
                    print('  %-20s %-34s %s' % ('', '', extra))

for d in sorted(unknown_folders):
    print('  (skipped, no skeleton known for folder) %s' % d)
print('\n%d kf checked, %d with problems' % (checked, bad))

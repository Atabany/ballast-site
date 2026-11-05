#!/usr/bin/env python3
"""Prove the RELEASE_STATE switch works, without touching the working tree.

    python3 _ops/test_states.py [baseline-ref]      # baseline defaults to rebuild/next

1. live: flipping the switch and building reproduces the baseline's served files. Every
   difference is printed, and any not listed in INTENDED fails.
2. back: flipping to prelaunch reproduces this tree's served files, byte for byte.
3. teeth: each unshipped claim, planted in each kind of output, makes the validator fail.
"""
from pathlib import Path
import filecmp, json, re, shutil, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = sys.argv[1] if len(sys.argv) > 1 else 'rebuild/next'
# Intentional differences between the live build and the baseline.
INTENDED = {
    'quittr-left-the-app-store.html',   # The recheck and rewording apply to both states.
    'llms-full.txt',                    # Carries that page's updated date.
    'sitemap.xml',                      # Same.
}
KEY = re.compile(r'[0-9a-f]{32}\.txt')  # The IndexNow key file is new and belongs in both states.
NOT_SERVED = ('_ops/', '_config.yml', 'README.md', '.gitignore', '.git')
CLAIMS = [
    'Shield turns on the filter.', 'Turn on the commitment lock.', 'Pick your app shields.', 'See your Voyage.', 'Your clear days stay.',
    'Backup and restore are free.', 'Add sites you add to the list.', 'Ballast filters adult websites for you.', 'A one-tap filter is included.',
    'Keep a file and restore your entries from it.',
]
fails = []


def served(folder):
    out = {}
    for f in Path(folder).rglob('*'):
        rel = f.relative_to(folder).as_posix()
        if f.is_file() and not rel.startswith(NOT_SERVED) and '__pycache__' not in rel:
            out[rel] = f
    return out


def copy_of_tree(tmp, name):
    dest = Path(tmp) / name
    shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns('.git', '__pycache__'))
    return dest


def set_state(tree, state):
    conf = tree / '_ops/discovery.json'
    raw = json.loads(conf.read_text())
    raw['RELEASE_STATE'] = state
    conf.write_text(json.dumps(raw, indent=2, ensure_ascii=False) + '\n')
    subprocess.run([sys.executable, str(tree / '_ops/build.py')], check=True, capture_output=True)


def diff(a, b):
    sa, sb = served(a), served(b)
    return sorted(k for k in sa.keys() | sb.keys() if k not in sa or k not in sb or not filecmp.cmp(sa[k], sb[k], shallow=False))


def validator_fails_on_claim(tree):
    run = subprocess.run([sys.executable, str(tree / '_ops/validate.py')], text=True, capture_output=True)
    return run.returncode != 0 and 'unshipped claim' in run.stdout


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    base = tmp / 'baseline'
    base.mkdir()
    archive = subprocess.run(['git', '-C', str(ROOT), 'archive', BASE], check=True, capture_output=True).stdout
    subprocess.run(['tar', '-x', '-C', str(base)], input=archive, check=True)

    tree = copy_of_tree(tmp, 'flip')
    set_state(tree, 'live')
    changed = diff(tree, base)
    print(f'1. live vs {BASE}: {len(changed)} served files differ')
    for name in changed:
        known = name in INTENDED or KEY.fullmatch(name)
        print(('   intended  ' if known else '   UNEXPECTED ') + name)
        if not known:
            fails.append('live differs from baseline: ' + name)

    set_state(tree, 'prelaunch')
    back = diff(tree, ROOT)
    print(f'2. back to prelaunch vs this tree: {len(back)} served files differ')
    fails += ['round trip differs: ' + n for n in back]

    print(f'3. planted claims: {len(CLAIMS)} in a page, plus FAQ JSON-LD, meta description and llms-full')
    for claim in CLAIMS:
        t = copy_of_tree(tmp, 'plant')
        page = t / '_ops/prelaunch/pages/support.html'
        page.write_text(page.read_text() + f'<p>{claim}</p>\n')
        set_state(t, 'prelaunch')
        if not validator_fails_on_claim(t):
            fails.append('page claim not caught: ' + claim)
        shutil.rmtree(t)
    plants = {
        'FAQ and JSON-LD': ('_ops/prelaunch/pages/index.html', '<h3>Is Ballast treatment?</h3>', '<h3>Is there a filter?</h3>\n<p>Yes, Ballast filters adult sites.</p>\n<h3>Is Ballast treatment?</h3>'),
        'meta and Open Graph': ('_ops/prelaunch/pages/index.html', 'streak tracking and slip support.', 'and Voyage.'),
        'llms-full.txt': ('_ops/prelaunch/llms-product.md', 'Who it may not suit:', 'Shield is included. Who it may not suit:'),
        'llms facts': ('_ops/discovery.json', 'a four-step urge flow,', 'a one-tap filter, a four-step urge flow,'),
    }
    for where, (rel, old, new) in plants.items():
        t = copy_of_tree(tmp, 'plant')
        f = t / rel
        assert old in f.read_text(), where
        f.write_text(f.read_text().replace(old, new))
        set_state(t, 'prelaunch')
        if not validator_fails_on_claim(t):
            fails.append('claim not caught in ' + where)
        shutil.rmtree(t)

if fails:
    print('\n'.join(fails))
    print(f'\nFAILED with {len(fails)} problem(s)')
    raise SystemExit(1)
print('OK: live matches the baseline apart from intended differences, the round trip is byte-identical, every planted claim was caught.')

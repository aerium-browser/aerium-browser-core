# Copyright 2026 Aerium Browser
# SPDX-License-Identifier: GPL-3.0-only

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

SKIP = ('*.grd', '*.grdp', '*.xtb')


def patch_files(dirs):
    out = []
    for d in dirs:
        if os.path.isdir(d):
            out += sorted(os.path.join(d, n) for n in os.listdir(d) if n.endswith('.patch'))
    return out


def touched(patches):
    seen, created = [], set()
    known = set()
    for p in patches:
        fresh = False
        cur = None
        with open(p, encoding='utf-8', errors='surrogateescape') as f:
            for line in f:
                if line.startswith('diff --git '):
                    cur = line.split()[2][2:]
                    fresh = cur not in known
                    if fresh:
                        known.add(cur)
                        seen.append(cur)
                elif cur and fresh and line.startswith('new file mode'):
                    created.add(cur)
    return seen, created


def skipped(path, extra):
    if path in extra:
        return True
    return any(path.endswith(s[1:]) for s in SKIP)


def same(a, b):
    if not os.path.isfile(a) or not os.path.isfile(b):
        return False
    if os.path.getsize(a) != os.path.getsize(b):
        return False
    with open(a, 'rb') as x, open(b, 'rb') as y:
        return x.read() == y.read()


def put(src, dst):
    os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
    shutil.copyfile(src, dst)
    shutil.copymode(src, dst)


def save(args):
    seen, created = touched(patch_files(args.patches))
    n = 0
    for path in seen:
        if path in created:
            continue
        src = os.path.join(args.src, path)
        if os.path.isfile(src):
            put(src, os.path.join(args.cache, path))
            n += 1
    print(f'[aerium] pristine copies kept: {n}')


def git_env(tmp):
    env = dict(os.environ, GIT_CEILING_DIRECTORIES=os.path.dirname(tmp))
    env.pop('GIT_DIR', None)
    env.pop('GIT_WORK_TREE', None)
    return env


def upstream_sources():
    out = []
    for source in (os.environ.get('CHROMIUM_SOURCE', ''), 'https://github.com/chromium/chromium'):
        if source and source not in out:
            out.append(source)
    return out


def fetch_upstream(src, paths, targets):
    got = set()
    if not paths:
        return got
    version = tree_version(src)
    tmp = tempfile.mkdtemp(prefix='aerium-pristine-')
    try:
        env = git_env(tmp)
        subprocess.run(['git', 'init', '-q'], cwd=tmp, check=True, env=env)
        ref = f'+refs/tags/{version}:refs/tags/{version}'
        fetched = False
        for index, source in enumerate(upstream_sources()):
            remote = f'source{index}'
            subprocess.run(['git', 'remote', 'add', remote, source], cwd=tmp, check=True, env=env)
            for _ in range(3):
                r = subprocess.run(['git', 'fetch', '-q', '--depth', '1', '--filter=blob:none',
                                    remote, ref], cwd=tmp, env=env)
                if r.returncode == 0:
                    fetched = True
                    break
            if fetched:
                break
        if not fetched:
            return got
        for path in paths:
            r = subprocess.run(['git', 'show', f'{version}:{path}'], cwd=tmp,
                               capture_output=True, env=env)
            if r.returncode:
                continue
            for target in targets:
                full = os.path.join(target, path)
                os.makedirs(os.path.dirname(full) or '.', exist_ok=True)
                with open(full, 'wb') as f:
                    f.write(r.stdout)
            got.add(path)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return got


def rebuild(args, missing, extra, tmp):
    if not args.base:
        print('[aerium] FATAL: no pristine copies and no base patches', file=sys.stderr)
        sys.exit(1)
    base = patch_files(args.base)
    bseen, _ = touched(base)
    bset = set(bseen)
    tb = tempfile.mkdtemp(prefix='aerium-base-')
    try:
        for path in bseen:
            if skipped(path, extra):
                continue
            src = os.path.join(args.src, path)
            if os.path.isfile(src):
                put(src, os.path.join(tb, path))
        includes = [f'--include={p}' for p in missing if p in bset]
        for p in reversed(base) if includes else []:
            r = subprocess.run(['git', 'apply', '-R', '--whitespace=nowarn', *includes, p],
                               cwd=tb, capture_output=True, text=True, env=git_env(tb))
            if r.returncode == 0:
                continue
            r = subprocess.run(['git', 'apply', '--check', '--whitespace=nowarn', *includes, p],
                               cwd=tb, capture_output=True, text=True, env=git_env(tb))
            if r.returncode:
                print(f'[aerium] FATAL: {os.path.basename(p)} did not reverse', file=sys.stderr)
                sys.exit(1)
            print(f'[aerium] {os.path.basename(p)} is new to this tree')
        for path in missing:
            orig = os.path.join(tb, path) if path in bset else os.path.join(args.src, path)
            if not os.path.isfile(orig):
                print('[aerium] FATAL: a pristine file could not be rebuilt', file=sys.stderr)
                sys.exit(1)
            put(orig, os.path.join(tmp, path))
            put(orig, os.path.join(args.cache, path))
        print(f'[aerium] pristine copies rebuilt: {len(missing)}')
    finally:
        shutil.rmtree(tb, ignore_errors=True)


def refresh(args):
    patches = patch_files(args.patches)
    seen, created = touched(patches)
    extra = set(args.skip or [])
    work = [p for p in seen if not skipped(p, extra)]
    need = [p for p in work if p not in created]
    tmp = tempfile.mkdtemp(prefix='aerium-refresh-')
    try:
        missing = []
        for path in need:
            cached = os.path.join(args.cache, path)
            if os.path.isfile(cached):
                put(cached, os.path.join(tmp, path))
            else:
                missing.append(path)
        if missing:
            got = fetch_upstream(args.src, missing, [tmp, args.cache])
            if got:
                print(f'[aerium] pristine copies fetched: {len(got)}')
            missing = [p for p in missing if p not in got]
        if missing:
            rebuild(args, missing, extra, tmp)
        excludes = [f'--exclude={s}' for s in SKIP] + [f'--exclude={p}' for p in extra]
        env = git_env(tmp)
        for p in patches:
            r = subprocess.run(['git', 'apply', '--whitespace=nowarn', *excludes, p],
                               cwd=tmp, capture_output=True, text=True, env=env)
            if r.returncode:
                print(f'[aerium] FATAL: {os.path.basename(p)} did not refresh', file=sys.stderr)
                sys.exit(1)
        for path in need:
            new = os.path.join(tmp, path)
            cached = os.path.join(args.cache, path)
            if os.path.isfile(new) and same(new, cached):
                print('[aerium] FATAL: patches were not applied during refresh', file=sys.stderr)
                sys.exit(1)
        for path in work:
            if path in created and not os.path.isfile(os.path.join(tmp, path)):
                print('[aerium] FATAL: patches were not applied during refresh', file=sys.stderr)
                sys.exit(1)
        n = 0
        for path in work:
            new = os.path.join(tmp, path)
            cur = os.path.join(args.src, path)
            if os.path.isfile(new) and not same(new, cur):
                put(new, cur)
                n += 1
        print(f'[aerium] patched files refreshed: {n} of {len(work)}')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def tree_version(src):
    parts = {}
    with open(os.path.join(src, 'chrome', 'VERSION')) as f:
        for line in f:
            key, _, value = line.strip().partition('=')
            parts[key] = value
    return '.'.join(parts[k] for k in ('MAJOR', 'MINOR', 'BUILD', 'PATCH'))


def git(args, cwd, **kw):
    return subprocess.run(['git', *args], cwd=cwd, check=True, **kw)


def upstream(args):
    current = tree_version(args.src)
    if current == args.version:
        print(f'[aerium] tree is at {current}')
        return
    tmp = tempfile.mkdtemp(prefix='aerium-upstream-')
    try:
        git(['init', '-q'], tmp)
        refs = [f'+refs/tags/{v}:refs/tags/{v}' for v in (current, args.version)]
        fetched = False
        for index, source in enumerate(args.source):
            remote = f'source{index}'
            git(['remote', 'add', remote, source], tmp)
            for _ in range(3):
                r = subprocess.run(['git', 'fetch', '-q', '--depth', '1', '--filter=blob:none',
                                    remote, *refs], cwd=tmp)
                if r.returncode == 0:
                    fetched = True
                    break
            if fetched:
                break
        if not fetched:
            print('[aerium] FATAL: upstream tags could not be fetched', file=sys.stderr)
            sys.exit(1)
        raw = git(['diff', '--raw', '--no-renames', current, args.version], tmp,
                  capture_output=True, text=True).stdout.splitlines()
        files = []
        for line in raw:
            meta, _, path = line.partition('\t')
            modes = meta.split()[:2]
            if '160000' in (modes[0].lstrip(':'), modes[1]) or path == 'DEPS':
                print(f'[aerium] FATAL: {current} to {args.version} moves {path}, '
                      'a fresh build is needed', file=sys.stderr)
                sys.exit(1)
            files.append(path)
        diff = os.path.join(tmp, 'upstream.diff')
        with open(diff, 'wb') as out:
            git(['diff', '--binary', '--no-renames', current, args.version], tmp, stdout=out)
        cache, tree = [], []
        for path in files:
            (cache if os.path.isfile(os.path.join(args.cache, path)) else tree).append(path)
        for root, paths in ((args.cache, cache), (args.src, tree)):
            if not paths:
                continue
            include = [f'--include={p}' for p in paths]
            r = subprocess.run(['git', 'apply', '--whitespace=nowarn', *include, diff],
                               cwd=root, capture_output=True, text=True, env=git_env(root))
            if r.returncode:
                print('[aerium] FATAL: upstream changes did not apply', file=sys.stderr)
                sys.exit(1)
        if tree_version(args.src) != args.version and 'chrome/VERSION' not in cache:
            print('[aerium] FATAL: the tree is not at the pinned version', file=sys.stderr)
            sys.exit(1)
        print(f'[aerium] tree moved from {current} to {args.version}: '
              f'{len(tree)} files, {len(cache)} pristine copies')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def copy(args):
    n = 0
    for root, _, names in os.walk(args.from_dir):
        for name in names:
            src = os.path.join(root, name)
            dst = os.path.join(args.to_dir, os.path.relpath(src, args.from_dir))
            if not same(src, dst):
                put(src, dst)
                n += 1
    print(f'[aerium] {args.label} refreshed: {n}')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('save')
    s.add_argument('--src', required=True)
    s.add_argument('--cache', required=True)
    s.add_argument('patches', nargs='+')
    r = sub.add_parser('refresh')
    r.add_argument('--src', required=True)
    r.add_argument('--cache', required=True)
    r.add_argument('--version', default='')
    r.add_argument('--base', action='append')
    r.add_argument('--skip', action='append')
    r.add_argument('patches', nargs='+')
    u = sub.add_parser('upstream')
    u.add_argument('--src', required=True)
    u.add_argument('--cache', required=True)
    u.add_argument('--version', required=True)
    u.add_argument('--source', action='append', required=True)
    c = sub.add_parser('copy')
    c.add_argument('--label', default='files')
    c.add_argument('from_dir')
    c.add_argument('to_dir')
    args = ap.parse_args()
    {'save': save, 'refresh': refresh, 'copy': copy, 'upstream': upstream}[args.cmd](args)


if __name__ == '__main__':
    main()

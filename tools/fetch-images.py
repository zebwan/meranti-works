#!/usr/bin/env python3
"""Download every photo in data/images.json into assets/img/<slot>.jpg.

Each slot has a width class (_widths) and an aspect class (_aspects). The source is
centre-cropped to the slot's aspect before resizing, so paired images (project
before/after) always come out identical and nothing is accidentally portrait.
Re-runnable: pass --force to rebuild files that already exist.
"""
import json, os, subprocess, concurrent.futures, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(f'{ROOT}/data/images.json'))
W, AR = M['_widths'], M['_aspects']
OUT = f'{ROOT}/assets/img'
FORCE = '--force' in sys.argv
os.makedirs(OUT, exist_ok=True)


def src_url(pid, w):
    # ask for 1.4x the target width so the aspect crop never upscales
    return (f'https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg'
            f'?auto=compress&cs=tinysrgb&w={int(w * 1.4)}')


def cover(im, tw, th):
    """Centre-crop to the target aspect, then resize to exactly tw x th."""
    scale = max(tw / im.width, th / im.height)
    im = im.resize((max(tw, round(im.width * scale)), max(th, round(im.height * scale))),
                   Image.LANCZOS)
    l, t = (im.width - tw) // 2, (im.height - th) // 2
    return im.crop((l, t, l + tw, t + th))


def one(item):
    slot, spec = item
    dest = f'{OUT}/{slot}.jpg'
    tw = W[spec['w']]
    th = round(tw / AR[spec.get('ar', 'wide')])
    if not FORCE and os.path.exists(dest):
        im = Image.open(dest)
        if im.size == (tw, th):
            return slot, 'cached', im.size

    tmp = f'{dest}.tmp'
    r = subprocess.run(['curl', '-s', '-L', '-A', 'Mozilla/5.0', src_url(spec['id'], tw),
                        '-o', tmp, '-w', '%{http_code}'], capture_output=True, text=True)
    if r.stdout.strip() != '200' or os.path.getsize(tmp) < 8000:
        os.path.exists(tmp) and os.remove(tmp)
        return slot, f'FAIL http={r.stdout.strip()}', None

    cover(Image.open(tmp).convert('RGB'), tw, th).save(
        dest, quality=82, optimize=True, progressive=True)
    os.remove(tmp)
    return slot, 'ok', (tw, th)


slots = [(k, v) for k, v in M.items() if not k.startswith('_')]
fails = []
with concurrent.futures.ThreadPoolExecutor(8) as ex:
    for slot, st, size in ex.map(one, slots):
        if st.startswith('FAIL'):
            fails.append(slot)
            print(f'  {slot:22s} {st}')

# paired images must match exactly or the comparison slider tears
for n in range(1, 5):
    a = Image.open(f'{OUT}/proj-{n}-before.jpg').size
    b = Image.open(f'{OUT}/proj-{n}-after.jpg').size
    assert a == b, f'project {n} before/after mismatch: {a} vs {b}'

total = sum(os.path.getsize(f'{OUT}/{s}.jpg') for s, _ in slots)
print(f'{len(slots)} slots, {len(fails)} failed. before/after pairs match. total {total/1e6:.1f} MB')
sys.exit(1 if fails else 0)

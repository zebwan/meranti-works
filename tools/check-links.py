#!/usr/bin/env python3
"""Crawl every generated page: check each one is reachable, that every internal
link resolves to a file that exists, and that every referenced asset is present."""
import os, re, sys
from urllib.parse import urljoin, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pages = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in {'_research', 'contact-sheet', 'tools', '.git'}]
    for f in filenames:
        if f.endswith('.html'):
            pages.append(os.path.relpath(os.path.join(dirpath, f), ROOT))

missing_links, missing_assets, no_title, ext = [], [], [], set()
ATTR = re.compile(r'(?:href|src)="([^"]+)"')

for page in sorted(pages):
    html = open(os.path.join(ROOT, page), encoding='utf-8').read()
    base = os.path.dirname(page)
    if '<title>' not in html:
        no_title.append(page)
    for ref in ATTR.findall(html):
        if ref.startswith(('#', 'mailto:', 'tel:', 'data:')):
            continue
        if urlparse(ref).scheme in ('http', 'https'):
            ext.add(ref)
            continue
        target = os.path.normpath(os.path.join(ROOT, base, ref.split('#')[0].split('?')[0]))
        if os.path.exists(target):
            continue
        (missing_assets if re.search(r'\.(jpg|png|svg|css|js|woff2?)$', ref) else missing_links).append(f'{page} -> {ref}')

print(f'pages:            {len(pages)}')
print(f'broken links:     {len(missing_links)}')
for m in missing_links[:20]:
    print('   ', m)
print(f'missing assets:   {len(missing_assets)}')
for m in missing_assets[:20]:
    print('   ', m)
print(f'pages w/o title:  {len(no_title)}')
print(f'external refs:    {len(ext)}  {sorted(ext)[:5]}')
sys.exit(1 if (missing_links or missing_assets or no_title) else 0)

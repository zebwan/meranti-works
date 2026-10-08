#!/usr/bin/env python3
"""Mirror the site to /tmp and serve it.

macOS blocks the preview server from reading anything under ~/Desktop, so the
site is copied out first. The server must be threaded or stylesheets and
modules intermittently fail to load.
"""
import http.server, socketserver, os, shutil, sys

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = '/tmp/meranti-site'
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9712
SKIP = {'_research', 'contact-sheet', 'tools', '.git', '.DS_Store'}


def sync():
    if os.path.isdir(DST):
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST, ignore=shutil.ignore_patterns(*SKIP))
    n = sum(len(f) for _, _, f in os.walk(DST))
    print(f'synced {n} files -> {DST}')


class Threaded(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DST, **kw)

    def send_head(self):
        # Re-copy this one file if the project copy is newer. Without it you
        # keep measuring the build that was current when the server started.
        rel = self.path.split('?')[0].lstrip('/')
        src, dst = os.path.join(SRC, rel), os.path.join(DST, rel)
        try:
            if os.path.isfile(src) and (not os.path.isfile(dst)
                                        or os.path.getmtime(src) > os.path.getmtime(dst)):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
        except OSError:
            pass
        return super().send_head()

    def end_headers(self):
        # Dev server: ES modules get cached hard otherwise, and you end up
        # measuring last build's JavaScript.
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, fmt, *args):
        code = args[1] if len(args) > 1 else ''
        if str(code) not in ('200', '304'):
            super().log_message(fmt, *args)


if __name__ == '__main__':
    sync()
    with Threaded(('127.0.0.1', PORT), Handler) as httpd:
        print(f'serving http://127.0.0.1:{PORT}/')
        httpd.serve_forever()

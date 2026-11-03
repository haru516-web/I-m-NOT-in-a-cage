from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os
os.chdir(Path(__file__).resolve().parent)
print('Open http://localhost:8765', flush=True)
ThreadingHTTPServer(('0.0.0.0', 8765), SimpleHTTPRequestHandler).serve_forever()

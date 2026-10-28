"""Restart only this project's current-user Django development server on 8000."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.request

root = Path(__file__).resolve().parents[1]
for entry in Path('/proc').iterdir():
    if not entry.name.isdigit():
        continue
    try:
        if entry.stat().st_uid != os.getuid():
            continue
        command = (entry/'cmdline').read_bytes().decode().split('\0')
        cwd = (entry/'cwd').resolve()
        if (cwd in (root, root/'server') and 'runserver' in command
                and '0.0.0.0:8000' in command
                and any(item.endswith('manage.py') for item in command)):
            os.kill(int(entry.name), signal.SIGTERM)
            print('Restarting owned Django process', entry.name, flush=True)
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        continue
time.sleep(1)
log = root/'evidence/django_server_refreshed.txt'
with log.open('w') as stream:
    process = subprocess.Popen(
        [sys.executable, str(root/'server/manage.py'), 'runserver',
         '0.0.0.0:8000', '--noreload'], cwd=root/'server', env=os.environ.copy(),
        stdin=subprocess.DEVNULL, stdout=stream, stderr=stream,
        start_new_session=True,
    )
(root/'.runtime/web.pid').write_text(str(process.pid))
for attempt in range(40):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8000/health/', timeout=2) as response:
            print('Updated application ready:', response.read().decode(), flush=True)
            break
    except OSError:
        time.sleep(.5)
else:
    raise RuntimeError('Updated web service did not start; inspect '+str(log))

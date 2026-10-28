"""Save real cURL command/output records; never substitute expected responses."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--web', default='http://127.0.0.1:8000')
parser.add_argument('--dealer', default='http://127.0.0.1:3030')
parser.add_argument('--sentiment', default='http://127.0.0.1:5050')
parser.add_argument('--output', default='evidence')
args = parser.parse_args()
project = Path(__file__).resolve().parents[1]
output = Path(args.output).resolve()
output.mkdir(exist_ok=True, parents=True)
private = project / '.capture'
private.mkdir(exist_ok=True)
settings = dict(line.split('=',1) for line in (project/'.env').read_text().splitlines() if '=' in line)
cookie = private/'cookies.txt'
config = private/'curl-auth.conf'
payload = private/'login.json'
payload.write_text(json.dumps({'userName':settings.get('DEMO_USERNAME','learner'),'password':settings['DEMO_PASSWORD']}))
payload.chmod(0o600)
base = ['curl','--fail-with-body','--silent','--show-error','--max-time','60']
subprocess.run(base+['--cookie-jar',str(cookie), args.web+'/'],capture_output=True,text=True,check=True)

def token_config():
    tokens = [line.split('\t')[-1] for line in cookie.read_text().splitlines()
        if line and not line.startswith('#') and '\tcsrftoken\t' in line]
    if not tokens:
        raise RuntimeError('The application did not issue a CSRF cookie.')
    config.write_text('header = "Content-Type: application/json"\nheader = "Origin: '+args.web+'"\nheader = "X-CSRFToken: '+tokens[-1]+'"\n')
    config.chmod(0o600)

def capture(name, arguments):
    command=base+arguments
    result=subprocess.run(command,capture_output=True,text=True)
    record=f'Working directory: {project}\n\n$ {shlex.join(command)}\n\n'
    try:
        record+=json.dumps(json.loads(result.stdout),indent=2)
    except json.JSONDecodeError:
        record+=result.stdout
    record+='\n'+result.stderr+f'\nProcess exit code: {result.returncode}\n'
    (output/f'{name}.txt').write_text(record,encoding='utf-8')
    if result.returncode:
        raise RuntimeError(f'{name} failed; see the actual output in {output}.')
    print('Saved actual output:',name,flush=True)
    return json.loads(result.stdout)

token_config()
auth=['--cookie',str(cookie),'--cookie-jar',str(cookie),'--config',str(config)]
login=capture('loginuser',auth+['--data-binary','@'+str(payload),args.web+'/djangoapp/login'])
assert login.get('status')=='Authenticated'
token_config()
logout=capture('logoutuser',auth+['--data','{}',args.web+'/djangoapp/logout'])
assert logout.get('status')=='Logged out'
capture('getdealerreviews',[args.dealer+'/fetchReviews/dealer/15'])
capture('getalldealers',[args.dealer+'/fetchDealers'])
capture('getdealerbyid',[args.dealer+'/fetchDealer/15'])
kansas=capture('getdealersbyState',[args.dealer+'/fetchDealers/Kansas'])
assert kansas and all(dealer['state']=='Kansas' for dealer in kansas)
capture('getallcarmakes',[args.web+'/djangoapp/get_cars'])
sentiment=capture('analyzereview',[args.sentiment+'/analyze/Fantastic%20services'])
assert sentiment['sentiment']=='positive'
print('All eight command/output records were saved from real services.')

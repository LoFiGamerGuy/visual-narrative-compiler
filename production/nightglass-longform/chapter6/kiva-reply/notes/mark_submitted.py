from pathlib import Path
import sys,json,datetime
f=Path(__file__).resolve().parents[1];p=f/'calls'/f'{sys.argv[1]}.json';d=json.loads(p.read_text());d.update(status='submitted',invoked=True,submitted_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());p.write_text(json.dumps(d,indent=2)+'\n')

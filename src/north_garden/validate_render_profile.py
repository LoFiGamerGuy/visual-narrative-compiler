"""Verify pinned local component hashes for a reusable render profile."""
import argparse, hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('profile',nargs='?',default='experiments/render-profiles/flux2-klein-local-r1.json');a=p.parse_args()
 x=json.loads((ROOT/a.profile).read_text())
 assert x['record_type']=='RenderProfile'
 for c in x['components']: assert sha(ROOT/c['path'])==c['sha256'],c['role']
 commit=subprocess.check_output(['git','-C',str(ROOT/'ComfyUI'),'rev-parse','HEAD'],text=True).strip()
 assert commit==x['adapter_version']['comfyui_commit']
 assert 'NOT_COMMERCIAL_PROFILE' in x['commercial_gate']
 print('0 failures, 0 warnings')
if __name__=='__main__':main()

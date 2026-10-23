"""Offline article-table replay; no RPC or credentials."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
commands=[('studies/market-context-2026-10-22',['calculate.py']),('studies/vamp-races-2026-10-23',['scripts/analyze.py']),('studies/vamp-races-2026-10-23',['scripts/build_chart.py','--svg-only']),('studies/creator-fees-854',['scripts/calculate.py'])]
for folder,args in commands:
    subprocess.run([sys.executable,*args],cwd=root/folder,check=True)
print('Article tables reproduced offline. Helius pilot replay is separate; see pilots/helius-2026-10-23/README.md.')

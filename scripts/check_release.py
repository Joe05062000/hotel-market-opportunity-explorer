"""Fail closed on unexpected release files and common credential signatures."""
from pathlib import Path
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
ALLOWED={
    '.gitignore','.streamlit/config.toml','README.md','app.py','public_core.py',
    'requirements.txt','requirements-dev.txt','pytest.ini',
    'data/sources.json','data/release_manifest.json','docs/DATA_REUSE.md','docs/DEPLOYMENT.md',
    'scripts/check_release.py','scripts/publish_github.sh','tests/test_public.py',
}
IGNORED_DIRS={'.git','.venv','venv','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache'}
PATTERNS=[re.compile('s'+'k'+r'-[A-Za-z0-9_-]{20,}'),
          re.compile('gh'+r'[pousr]_[A-Za-z0-9]{20,}'),
          re.compile('github'+'_pat_'+r'[A-Za-z0-9_]{20,}'),
          re.compile('-----BEGIN '+r'(?:RSA |OPENSSH |EC )?PRIVATE KEY-----')]


def check():
    manifest=json.loads((ROOT/'data/release_manifest.json').read_text())
    if manifest['observations_included'] or manifest['historical_numeric_claims_enabled'] or manifest['approved_observation_files']:
        raise ValueError('Unapproved historical observations enabled')
    candidates=[]
    for path in ROOT.rglob('*'):
        rel=path.relative_to(ROOT)
        if any(part in IGNORED_DIRS for part in rel.parts) or rel.name in {'.DS_Store','Thumbs.db'}: continue
        if path.is_symlink(): raise ValueError(f'Symlink excluded from release: {rel}')
        if not path.is_file(): continue
        if rel.as_posix() not in ALLOWED: raise ValueError(f'Unexpected release file: {rel}')
        text=path.read_text(encoding='utf-8')
        if any(pattern.search(text) for pattern in PATTERNS): raise ValueError(f'Credential signature in {rel}; value not printed')
        candidates.append(rel.as_posix())
    if set(candidates) != ALLOWED: raise ValueError(f'Missing release files: {sorted(ALLOWED-set(candidates))}')
    if (ROOT/'.git').is_dir():
        tracked=subprocess.run(['git','ls-files','-z'],cwd=ROOT,check=True,capture_output=True).stdout.decode().split('\0')
        if set(filter(None,tracked))-ALLOWED: raise ValueError('Git tracks a file outside the release allowlist')
    return sorted(candidates)


if __name__=='__main__':
    files=check()
    print(f'Public release passed: {len(files)} allowlisted text files; no historical observation files or common credential signatures.')

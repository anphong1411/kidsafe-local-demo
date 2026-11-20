"""Build the x64 KidSafe installer from the project's locked Windows environment."""
import argparse
from importlib.metadata import distribution
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
AGENT_DEPS = (
    'certifi', 'cffi', 'charset-normalizer', 'cryptography', 'dnslib', 'filelock',
    'idna', 'pillow', 'psutil', 'pycparser', 'pystray', 'pywin32', 'requests',
    'requests-file', 'six', 'tldextract', 'tzdata', 'urllib3', 'websockets',
)


def stage(payload):
    runtime = payload / 'runtime'
    runtime.mkdir(parents=True)
    base = Path(sys.base_prefix)
    for name in ('python.exe', 'pythonw.exe', 'python3.dll', 'LICENSE.txt'):
        shutil.copy2(base / name, runtime)
    for pattern in ('python3[0-9]*.dll', 'vcruntime*.dll'):
        for path in base.glob(pattern):
            shutil.copy2(path, runtime)
    shutil.copytree(base / 'DLLs', runtime / 'DLLs', ignore=shutil.ignore_patterns('*.pdb'))
    shutil.copytree(base / 'Lib', runtime / 'Lib', ignore=shutil.ignore_patterns(
        '__pycache__', 'site-packages', 'test', 'tests', 'tkinter', 'idlelib', 'ensurepip',
    ))
    locked = dict(re.findall(r'^([\w-]+)==([^\s;]+)', (ROOT / 'requirements.lock').read_text(), re.M))
    for name in AGENT_DEPS:
        installed = distribution(name)
        if installed.version != locked[name]:
            raise ValueError(f'{name} does not match requirements.lock')
        for relative in installed.files:
            if '..' in relative.parts or relative.suffix == '.pyc' or '__pycache__' in relative.parts:
                continue
            source = installed.locate_file(relative)
            if source.is_file():
                destination = runtime / 'Lib' / 'site-packages' / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
    for path in (runtime / 'Lib/site-packages/pywin32_system32').glob('*.dll'):
        shutil.copy2(path, runtime)
    (runtime / 'python._pth').write_text(
        '.\nDLLs\nLib\nLib\\site-packages\nLib\\site-packages\\win32\n'
        'Lib\\site-packages\\win32\\lib\n..\n', encoding='ascii',
    )
    shutil.copytree(ROOT / 'agent', payload / 'agent', ignore=shutil.ignore_patterns(
        '__pycache__', '*.pyc', 'config.example.json', 'requirements.txt',
    ))
    for script in (payload / 'agent/scripts').glob('*.ps1'):
        # Windows PowerShell 5.1 requires a BOM to recognize Vietnamese UTF-8.
        script.write_text(script.read_text(encoding='utf-8-sig'), encoding='utf-8-sig')
    # Exercise native imports with an unrelated current directory and no user site.
    subprocess.run([runtime / 'python.exe', '-I', '-c',
                    'import agent.runtime, agent.service, agent.tray, agent.child_window, PIL.Image, pystray, websockets, '
                    'servicemanager, win32api, win32gui, win32security; '
                    'from zoneinfo import ZoneInfo; ZoneInfo("Asia/Ho_Chi_Minh")'],
                   cwd=payload.parent, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iscc', type=Path, required=True)
    args = parser.parse_args()
    if sys.platform != 'win32' or platform.machine().upper() != 'AMD64':
        parser.error('Build with the x64 Windows project Python.')
    work = ROOT / '.tmp'
    work.mkdir(exist_ok=True)
    output = ROOT / 'releases'
    output.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='setup-', dir=work) as temporary:
        build = Path(temporary)
        payload = build / 'payload'
        stage(payload)
        subprocess.run([args.iscc.resolve(), '/Qp', f'/DPayload={payload}', f'/O{build}',
                        ROOT / 'agent/scripts/KidSafe.iss'], check=True)
        (build / 'KidSafe-Setup-x64.exe').replace(output / 'KidSafe-Setup-x64.exe')


if __name__ == '__main__':
    main()

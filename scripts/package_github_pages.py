"""Export the public KidSafe download site and the standalone Windows installer."""

import argparse
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit
from zipfile import ZIP_DEFLATED, ZipFile

from jinja2 import Environment, FileSystemLoader, select_autoescape


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / 'dashboard'
INSTALLER = ROOT / 'releases' / 'KidSafe-Setup-x64.exe'
STATIC_FILES = (
    'download.css', 'download.js', 'mesh-drift.js', 'mesh-drift.frag',
    'images/download-family.jpg', 'images/how-family.jpg', 'images/how-study.jpg',
    'images/how-together.jpg', 'images/how-child.jpg',
)


def https_origin(value: str) -> str:
    message = 'Use an HTTPS origin such as https://localhost:8446.'
    try:
        address = urlsplit(value)
        port = address.port
    except ValueError as error:
        raise argparse.ArgumentTypeError(message) from error
    if (address.scheme != 'https' or not address.hostname or port == 0
            or address.username is not None or address.path not in ('', '/')
            or address.query or address.fragment or any(char.isspace() or char == '\\' for char in value)):
        raise argparse.ArgumentTypeError(message)
    return f'https://{address.netloc}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--web-only', action='store_true', help='Update a repository that already contains the installer.')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--server-origin', type=https_origin, default='https://localhost:8446',
                        help='HTTPS address of the KidSafe server for the account buttons.')
    args = parser.parse_args()
    installer = None
    if not args.web_only:
        if not INSTALLER.is_file():
            parser.error('Build releases/KidSafe-Setup-x64.exe before packaging the site.')
        if INSTALLER.stat().st_size > 25 * 1024 * 1024:
            parser.error('Installer exceeds the 25 MiB limit for browser uploads to GitHub.')
        installer = INSTALLER.read_bytes()
        if not installer.startswith(b'MZ'):
            parser.error('The Windows installer is not an executable.')

    templates = Environment(loader=FileSystemLoader(DASHBOARD / 'templates'),
                            autoescape=select_autoescape())
    html = templates.get_template('download.html').render(
        available=True, public_download=True, public_server_origin=args.server_origin,
    )
    name = 'KidSafe-github-pages-web-update.zip' if args.web_only else 'KidSafe-github-pages.zip'
    output = args.output or ROOT / 'releases' / name
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, 'w', compression=ZIP_DEFLATED) as archive:
        archive.writestr('index.html', html)
        if installer is not None:
            archive.write(ROOT / 'docs/GITHUB_PAGES_DEPLOY.md', 'README.md')
            archive.writestr('.nojekyll', '')
            archive.writestr(INSTALLER.name, installer)
            archive.writestr(f'{INSTALLER.name}.sha256', f'{sha256(installer).hexdigest()}  {INSTALLER.name}\n')
        for name in STATIC_FILES:
            archive.write(DASHBOARD / 'static' / name, Path(name).name)
    print(output.resolve())


if __name__ == '__main__':
    main()

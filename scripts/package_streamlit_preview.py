"""Package the standalone KidSafe preview for a separate GitHub repository."""

import argparse
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "demo" / "streamlit_preview"
PREVIEW_FILES = (
    ".gitignore", ".streamlit/config.toml", "README.md", "requirements.txt",
    "streamlit_app.py", "preview_frame.js", "sample_data.js",
)
DASHBOARD_FILES = (
    "templates/login.html", "templates/parent.html", "templates/child.html",
    "static/app.css", "static/login.css", "static/app.js", "static/images/login-family.png",
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flat", action="store_true", help="Bundle all dashboard assets into one uploadable file.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    filename = "KidSafe-streamlit-upload.zip" if args.flat else "KidSafe-streamlit-preview.zip"
    output = args.output or Path("releases") / filename
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for name in PREVIEW_FILES:
            if args.flat and name == ".streamlit/config.toml":
                continue
            archive.write(PREVIEW / name, name)
        if args.flat:
            assets = BytesIO()
            with ZipFile(assets, "w", compression=ZIP_DEFLATED) as dashboard:
                for name in DASHBOARD_FILES:
                    dashboard.write(ROOT / "dashboard" / name, name)
            archive.writestr("dashboard-assets.zip", assets.getvalue())
        else:
            for name in DASHBOARD_FILES:
                archive.write(ROOT / "dashboard" / name, f"dashboard/{name}")
    print(output.resolve())


if __name__ == "__main__":
    main()

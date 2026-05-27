$ErrorActionPreference = "Stop"
if (!(Test-Path .venv)) {
  python -m venv .venv
}
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir src

import subprocess, sys, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

PORT = 8501
OUT  = "qr_dashboard_export.pdf"

def _ready(url, timeout=60):
    for _ in range(timeout):
        try:
            if urllib.request.urlopen(url, timeout=2).status == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

def export_pdf(out=OUT, port=PORT, url=None):
    proc = None
    base = url or f"http://localhost:{port}"

    if not url:
        try:
            urllib.request.urlopen(base, timeout=2)
        except Exception:
            app = Path(__file__).parent / "app.py"
            proc = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", str(app),
                 "--server.port", str(port), "--server.headless", "true"],
                cwd=str(Path(__file__).parent.parent),
            )

    assert _ready(base), f"Server not reachable at {base}"

    with sync_playwright() as pw:
        page = pw.chromium.launch(headless=True).new_page(
            viewport={"width": 1440, "height": 900}
        )
        page.goto(base, wait_until="networkidle", timeout=60_000)
        time.sleep(8)
        h = page.evaluate("document.body.scrollHeight")
        for y in range(0, h, 600):
            page.evaluate(f"window.scrollTo(0,{y})")
            time.sleep(0.1)
        page.evaluate("window.scrollTo(0,0)")
        page.pdf(path=out, format="A3", print_background=True,
                 margin={"top":"12mm","bottom":"12mm","left":"10mm","right":"10mm"})

    if proc:
        proc.terminate()
    print(f"PDF saved → {Path(out).resolve()}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--out",  default=OUT)
    p.add_argument("--port", type=int, default=PORT)
    p.add_argument("--url",  default=None)
    a = p.parse_args()
    export_pdf(a.out, a.port, a.url)
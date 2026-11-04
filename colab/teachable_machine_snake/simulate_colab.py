"""Simulates a Colab-like environment: an empty working directory.

Proves cell 0 can bootstrap the sources by itself (git clone), which is the path
a fresh "Open in Colab" takes. Runs in a temp dir under the system temp root.

    python simulate_colab.py
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "teachable_machine_snake.ipynb"

work = Path(tempfile.mkdtemp(prefix="colab_sim_"))
print(f"[sim] 空目錄：{work}")
print(f"[sim] 裡面有 sketch.js 嗎？ {(work / 'sketch.js').exists()}")
print()

# Extract cell 0 and run it from the empty dir, exactly like Colab would.
import nbformat

nb = nbformat.read(NOTEBOOK, as_version=4)
cell = next(c for c in nb.cells if c.cell_type == "code" and "find_sources" in "".join(c.source))

prev = Path.cwd()
os.chdir(work)
try:
    ns = {"__name__": "__main__"}
    exec(compile("".join(cell.source), "cell0", "exec"), ns)
    here = ns["HERE"]
    print()
    print(f"[sim] 解析出的目錄：{here}")
    ok = all((here / n).exists() for n in ("sketch.js", "snake.js", "validate.js"))
    print(f"[sim] 三個檔案都在：{ok}")
    if ok:
        proc = subprocess.run(
            ["node", str(here / "validate.js")],
            cwd=str(here),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        print(proc.stdout.strip().splitlines()[-1])
        sys.exit(proc.returncode)
    sys.exit(1)
finally:
    os.chdir(prev)
    shutil.rmtree(work, ignore_errors=True)

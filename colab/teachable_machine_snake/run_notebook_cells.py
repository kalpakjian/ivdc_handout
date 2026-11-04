"""Executes the notebook's runnable cells in order (skips the Colab-only install cell).

Used to prove the notebook actually works before pushing, without launching Colab.

    python run_notebook_cells.py
"""

import nbformat

NOTEBOOK = "teachable_machine_snake.ipynb"
SKIP = {4}  # cell 4 uses %pip / !nodeenv -- Colab only

nb = nbformat.read(NOTEBOOK, as_version=4)
ns = {}
for index, cell in enumerate(nb.cells):
    if cell.cell_type != "code":
        continue
    if index in SKIP:
        print(f"===== cell {index} (skipped: Colab-only) =====")
        continue
    print(f"===== cell {index} =====")
    exec(compile("".join(cell.source), f"cell{index}", "exec"), ns)

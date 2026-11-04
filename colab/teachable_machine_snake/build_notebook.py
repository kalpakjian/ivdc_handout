"""Builds teachable_machine_snake.ipynb.

Keeping the notebook generated instead of hand-edited means the JSON stays valid
and the cell order can be reviewed like source. Run from this folder:

    python build_notebook.py
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "teachable_machine_snake.ipynb"


def md(text: str) -> dict:
    return {"cell_type": "markdown", "id": _cell_id(text), "metadata": {}, "source": _lines(text)}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "id": _cell_id(text),
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": _lines(text),
    }


def _cell_id(text: str) -> str:
    """Stable, readable cell id so rebuilds do not churn the diff."""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]



def _lines(text: str) -> list[str]:
    """Split into notebook source lines, each keeping its trailing newline."""
    text = text.strip("\n")
    parts = text.split("\n")
    return [p + "\n" for p in parts[:-1]] + [parts[-1]]


INTRO = """\
# Teachable Machine × p5.js：手勢控制貪食蛇（Colab 示範與檢查）

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kalpakjian/ivdc_handout/blob/main/colab/teachable_machine_snake/teachable_machine_snake.ipynb)

對應講義：`Workshop.docx`（Computer Vision Workshop on Robotics）。

**先講清楚：這個遊戲本身不能在 Colab 上玩。**
它是一份 p5.js 網頁，需要瀏覽器的**攝影機**加上 **p5 編輯器**，
而 Colab 的 VM 是無螢幕、無相機的 Linux。所以這本筆記本只做三件事：

| 這裡做什麼 | 為什麼 |
|---|---|
| 1. 顯示完整程式碼 | 直接讀得到修正後的 `sketch.js` / `snake.js` |
| 2. 用 Node 無介面實跑驗證 | 沒有瀏覽器也能確認遊戲邏輯正確 |
| 3. 下載修正後的檔案 | 丟進 <https://editor.p5js.org/> 就能玩 |

真正的手勢玩法（講義 C–E 步）還是回自己的電腦：
Teachable Machine 訓練手勢 → p5.js 貼上兩個檔案 → 用手勢操作。

> 定位同 `colab/preview/`：輔助用，不是主線考試筆記本。
"""

SETUP = """\
## 0. 取得檔案（Colab 用 `git clone`，本機直接讀）

**這一步不能省。** 從 GitHub 開 Colab 時，Colab 只把 `.ipynb` 載進來，
`sketch.js` / `snake.js` / `validate.js` **不會**跟著出現，
`Path.cwd()` 是 `/content`，裡面什麼都沒有 —— 直接跑下一格會全部 `MISS`。

所以這裡會依序嘗試：

1. 目前目錄已有 `sketch.js` → 直接使用（本機執行就是這條路）
2. 找 `teachable_machine_snake/` 子目錄（在 repo 根目錄開筆記本時）
3. 都沒有 → `git clone` 這個 repo（公開，不需要 token）
"""

SETUP_CODE = """\
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "https://github.com/kalpakjian/ivdc_handout"
SUB = "colab/teachable_machine_snake"
# Colab puts notebooks in /content; elsewhere use the temp dir so a stray
# clone never lands in a drive root.
CONTENT = Path("/content") if sys.platform == "linux" and Path("/content").is_dir() else Path(tempfile.gettempdir())


def find_sources() -> Path | None:
    \"\"\"Return a folder that already holds sketch.js / snake.js / validate.js.\"\"\"
    for candidate in (Path.cwd(), Path.cwd() / "teachable_machine_snake", CONTENT / SUB):
        if (candidate / "sketch.js").exists() and (candidate / "snake.js").exists():
            return candidate
    return None


HERE = find_sources()
if HERE is None:
    if shutil.which("git") is None:
        raise SystemExit("沒有 git，也沒有檔案 —— 請手動上傳 sketch.js / snake.js / validate.js")
    target = CONTENT / "ivdc_handout"
    if not target.exists():
        print(f"檔案不在，clone {REPO} ...")
        subprocess.run(["git", "clone", "-q", "--depth", "1", REPO, str(target)], check=True)
    HERE = target / SUB
    print(f"clone 完成 -> {HERE}")

print(f"Python {sys.version.split()[0]}")
print(f"工作目錄：{HERE}")
print()

for name in ("sketch.js", "snake.js", "validate.js"):
    p = HERE / name
    size = p.stat().st_size if p.exists() else 0
    print(f"  {'OK  ' if p.exists() else 'MISS'}  {name:<12} {size:>6} bytes")

node = shutil.which("node")
print()
if node:
    ver = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip()
    print(f"Node：{ver}")
else:
    print("沒有 node —— 第 2 節的驗證會略過；Colab 請先跑下一格安裝。")
"""

INSTALL_NODE = """\
## 0b.（Colab 專用）安裝 Node

本機已經有 Node 的話**跳過這格**。Colab 映像檔通常沒有，
用 `nodeenv` 從 PyPI 抓一顆預編譯的 Node，不需要 root。
"""

INSTALL_NODE_CODE = """\
try:
    import google.colab  # noqa: F401
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

if not IN_COLAB:
    print("不是 Colab，略過安裝（本機請自行確認 node 已安裝）")
elif shutil.which("node"):
    print("已經有 node：", shutil.which("node"))
else:
    %pip install -q nodeenv
    !nodeenv -p --node=lts 2>&1 | tail -3
    for candidate in (Path(sys.prefix) / "bin" / "node", Path("/usr/local/bin/node")):
        if candidate.exists() and not shutil.which("node"):
            os.environ["PATH"] = str(candidate.parent) + os.pathsep + os.environ["PATH"]
    print("node ->", shutil.which("node"))
"""

SHOW_SOURCES = """\
## 1. 修正後的完整程式碼

下面兩格直接**讀檔案**印出內容（不是貼在 markdown 裡），所以永遠跟實際檔案一致。
"""

SHOW_SKETCH = """\
SKETCH = (HERE / "sketch.js").read_text(encoding="utf-8").rstrip()
print("── sketch.js ──")
print(f"（{len(SKETCH.splitlines())} 行）\\n")
print(SKETCH)
"""

SHOW_SNAKE = """\
SNAKE = (HERE / "snake.js").read_text(encoding="utf-8").rstrip()
print("── snake.js ──")
print(f"（{len(SNAKE.splitlines())} 行）\\n")
print(SNAKE)
"""

VERIFY = """\
## 2. 無介面驗證（Node）

`validate.js` 用 p5 的 **stub** 載入**真正的** `sketch.js` / `snake.js`，
模擬 Teachable Machine 回傳的手勢標籤，逐項檢查：

- 手勢 `Left` / `Right` / `Up` / `Down` 是否真的設定方向
- 180° 反向（`Left` → `Right`）是否被擋下
- 蛇正常移動時**不會**馬上結束（原本 `endGame()` 的 bug）
- 真正的自撞與撞牆**仍然**會被判定
- 吃到食物會變長；`draw()` 連跑三格不會誤觸 `END GAME`

Colab 沒有瀏覽器，這種「stub 掉繪圖、只驗邏輯」的方式剛好合適。
"""

VERIFY_CODE = """\
node = shutil.which("node")
if not node:
    print("找不到 node，略過驗證（請先跑 0b）")
else:
    proc = subprocess.run(
        [node, str(HERE / "validate.js")],
        cwd=str(HERE),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
    )
    print(proc.stdout)
    if proc.stderr.strip():
        print("--- stderr ---")
        print(proc.stderr)
    print()
    print("驗證結果：", "全部通過" if proc.returncode == 0 else f"有失敗（exit {proc.returncode}）")
"""

BUGS = """\
## 3. 這次到底改了什麼

講義的 **C、D 步在原始檔案裡已經做好了**（`snake.js` 已建立、模型網址已貼在第 17 行），
**只有 E 步沒做** —— 所以原始檔完全不能用手勢玩：它還在讀方向鍵，
而且從來沒有呼叫手勢判斷函式。

### 3.1 `sketch.js`：補完講義 E 步

| 步驟 | 原本 | 改成 |
|---|---|---|
| E1／E2 | `function keyPressed()` + `keyIsDown(LEFT_ARROW)` … | `function controlSnake()` + `label == "Left"` / `"Right"` / `"Down"` / `"Up"` |
| E3 | `gotResults()` 裡只有一行註解佔位 | 在 `label = results[0].label;` 之後呼叫 `controlSnake()` |

字串要跟 Teachable Machine 的 Image Set 名稱**完全相同**（大小寫敏感），這是講義 HINT 的重點。

### 3.2 `snake.js`：兩個就算做完 E 步也不能玩的 bug

| 位置 | 原本 | 症狀 | 改成 |
|---|---|---|---|
| `endGame()` | `for (let i = 0; i < this.body.length - 1; i++)` | 迴圈**包含蛇頭自己**，`part.x == x && part.y == y` 每次都成立 → 第一格就 `END GAME` | `length - 2`：排除脖子（與蛇頭上一個位置重疊）與蛇頭本身 |
| `setDir()` | 直接 `this.xdir = x; this.ydir = y;` | 手勢從 `Left` 突然變 `Right`（180° 反向）時蛇頭撞進脖子 → 立即自撞 | 擋掉與目前方向完全相反的要求；並忽略 `(0,0)`，免得 `waiting...` 讓蛇停住 |

### 3.3 為什麼看得出來

把同一支 `validate.js` 分別跑**原始檔**與**修正檔**，差異很清楚：
"""

BEFORE_AFTER = """\
| 項目 | 原始檔 | 修正後 |
|---|---|---|
| `controlSnake()` 存在 | ✗ | ✓ |
| `keyPressed()` 已移除 | ✗ | ✓ |
| `Left` 手勢真的設定方向 | ✗（蛇不動，`x` 停在 15） | ✓ |
| 180° 反向被擋 | ✗ | ✓ |
| 正常移動不誤判結束 | ✓（但它另一個 bug 會先炸） | ✓ |
| **合計** | **6 項失敗** | **17/17 通過** |
"""

USAGE = """\
## 4. 下載修正後的檔案

跑完這格，Colab 會把 `sketch.js`、`snake.js` 存到瀏覽器的下載資料夾
（本機執行時只會列出檔案位置）。之後：

1. 到 <https://editor.p5js.org/> 建立新 sketch
2. 用下載的 `sketch.js` 取代原本的
3. 新增檔案 `snake.js`，貼上下載的內容
4. 在 `index.html` 加入這兩行（講義 C6／C7）：

```html
<script src="https://unpkg.com/ml5@0.4.3/dist/ml5.min.js"></script>
<script src="snake.js"></script>
```

5. 模型網址（`sketch.js` 第 17 行）若不是你自己的，換成你的 Teachable Machine 分享連結，
   結尾保留 `/model.json`
6. 按 ▶ 執行，對鏡頭做手勢
"""

USAGE_CODE = """\
try:
    from google.colab import files as _colab_files
except ImportError:
    _colab_files = None

if _colab_files is not None:
    for name in ("sketch.js", "snake.js"):
        _colab_files.download(str(HERE / name))
        print("已下載", name)
else:
    for name in ("sketch.js", "snake.js"):
        print(f"檔案位置：{HERE / name}")
"""

LIMITS = """\
## 5. 這本筆記本驗不到的部分

誠實列出範圍，免得以為「全部通過」就等於遊戲沒問題：

| 有驗到 | 沒驗到 |
|---|---|
| `Snake` 的移動、變長、自撞、撞牆 | 瀏覽器裡的實際畫面與 `frameRate` 手感 |
| `controlSnake()` 對各手勢標籤的反應 | Teachable Machine 模型**真的認得你的手勢**（要用你的鏡頭） |
| `gotResults()` → `controlSnake()` 的串接 | ml5 0.4.3 在特定瀏覽器版本的相容性 |
| 連續三格 `draw()` 不會誤觸結束 | 模型載入失敗／網路被擋時的表現 |

`validate.js` 是用假的 p5 環境跑真程式，所以**邏輯**可信、**畫面**不可信。
最後一步（講義 E4：用手勢真的玩一輪）只能在你自己的電腦完成。
"""


def main() -> None:
    metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "colab": {"provenance": [], "toc_visible": True},
    }
    nb = {
        "cells": [
            md(INTRO),
            md(SETUP),
            code(SETUP_CODE),
            md(INSTALL_NODE),
            code(INSTALL_NODE_CODE),
            md(SHOW_SOURCES),
            code(SHOW_SKETCH),
            code(SHOW_SNAKE),
            md(VERIFY),
            code(VERIFY_CODE),
            md(BUGS),
            md(BEFORE_AFTER),
            md(USAGE),
            code(USAGE_CODE),
            md(LIMITS),
        ],
        "metadata": metadata,
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUT.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT.name}: {len(nb['cells'])} cells, {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()

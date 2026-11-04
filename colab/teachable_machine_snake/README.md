# colab/teachable_machine_snake — 手勢控制貪食蛇（修正版）

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kalpakjian/ivdc_handout/blob/main/colab/teachable_machine_snake/teachable_machine_snake.ipynb)

對應講義 **`Workshop.docx`**（Computer Vision Workshop on Robotics：
Teachable Machine ＋ p5.js ＋ ml5.js 的手勢控制貪食蛇）。

**這個遊戲不能在 Colab 上玩。** 它是 p5.js 網頁，需要瀏覽器鏡頭跟 p5 編輯器，
而 Colab 的 VM 是無螢幕、無相機的 Linux。這裡放的是**修正後可執行的原始碼**，
加上一本用 Node 在無介面下實跑驗證的 notebook。

## 檔案

| 檔案 | 說明 |
|---|---|
| [`sketch.js`](sketch.js) | 主程式（已補完講義 **E 步**：手勢 → 蛇的方向） |
| [`snake.js`](snake.js) | `Snake` 類別（已修掉 2 個不能玩的 bug） |
| [`validate.js`](validate.js) | Node 無介面驗證，17 項檢查 |
| [`teachable_machine_snake.ipynb`](teachable_machine_snake.ipynb) | Colab 版：顯示程式碼、跑驗證、下載檔案 |
| [`build_notebook.py`](build_notebook.py) | 產生上面那本 notebook |
| [`run_notebook_cells.py`](run_notebook_cells.py) | 在本機逐格跑 notebook（本機驗證用，可不上傳） |
| [`simulate_colab.py`](simulate_colab.py) | 模擬 Colab 空目錄，驗證第 0 格的自動 clone |
| `Workshop.docx` | 原始講義，原封不動 |

## 原始碼的問題

講義的 **C、D 步在原始檔裡已經做好了**（`snake.js` 已建立、模型網址已貼在第 17 行），
**只有 E 步沒做** —— 所以原始檔完全不能用手勢玩：它還在讀方向鍵，
而且從來沒有呼叫手勢判斷函式。

| # | 位置 | 問題 | 修正 |
|---|---|---|---|
| 1 | `sketch.js` E1／E2 | `function keyPressed()` 讀 `keyIsDown(LEFT_ARROW)` … | 改名 `controlSnake()`，改比對 `label == "Left"` / `"Right"` / `"Down"` / `"Up"` |
| 2 | `sketch.js` E3 | `gotResults()` 只有一行註解佔位 | 在 `label = results[0].label;` 之後呼叫 `controlSnake()` |
| 3 | `snake.js` `endGame()` | `i < this.body.length - 1` **把蛇頭自己算進去**，`part.x == x && part.y == y` 每次都成立 → **第一格就 `END GAME`** | `length - 2`：排除脖子（與蛇頭上一個位置重疊）與蛇頭本身 |
| 4 | `snake.js` `setDir()` | 手勢從 `Left` 突然變 `Right`（180° 反向）時蛇頭撞進脖子 → 立即自撞 | 擋掉與目前方向完全相反的要求；並忽略 `(0,0)`，免得 `waiting...` 讓蛇停住 |

字串必須跟 Teachable Machine 的 Image Set 名稱**完全相同**（大小寫敏感），這是講義 HINT 的重點。

## 驗證

```bash
node validate.js      # 17/17 checks passed
```

`validate.js` 用 p5 的 stub 載入**真正的** `sketch.js` / `snake.js`，模擬手勢標籤後檢查：
手勢設定方向、180° 反向被擋、正常移動不誤判結束、真正的自撞／撞牆仍會判定、吃食物變長、
連續三格 `draw()` 不誤觸 `END GAME`。

同一支腳本拿去跑**原始檔**是 **11/17**（6 項失敗：沒有 `controlSnake`、還在 `keyPressed`、
蛇完全沒收到方向而停在 `x=15`、反向沒擋）；修正後 **17/17**。

## 怎麼真的玩（講義 C–E 步）

> **在 Colab 上只能「看程式碼 + 跑驗證 + 下載檔案」**，不能玩遊戲。
> 按上面的 **Open in Colab** 徽章即可開啟；第 0 格會自動 `git clone` 這個 repo
> （Colab 只載入 `.ipynb`，不會帶上其他檔案），第 2 格若沒有 Node 會先裝一顆。

1. 到 <https://editor.p5js.org/> 建立新 sketch
2. 用這裡的 `sketch.js` 取代原本的
3. 新增檔案 `snake.js`，貼上這裡的內容
4. `index.html` 加入（講義 C6／C7）：

```html
<script src="https://unpkg.com/ml5@0.4.3/dist/ml5.min.js"></script>
<script src="snake.js"></script>
```

5. `sketch.js` 第 17 行的模型網址若不是你自己的，換成你的 Teachable Machine 分享連結，
   結尾保留 `/model.json`
6. 按 ▶，對鏡頭做手勢

> 想看自己的鏡頭畫面：把 `sketch.js` 第 14 行的 `video.hide();` 註解掉（講義最後的提示）。

## 驗到哪裡、沒驗到哪裡

| 有驗到 | 沒驗到 |
|---|---|
| `Snake` 的移動、變長、自撞、撞牆 | 瀏覽器裡的畫面與 `frameRate` 手感 |
| `controlSnake()` 對各手勢標籤的反應 | Teachable Machine 模型**真的認得你的手勢**（要用你的鏡頭） |
| `gotResults()` → `controlSnake()` 的串接 | ml5 0.4.3 在特定瀏覽器版本的相容性 |
| 連續三格 `draw()` 不誤觸結束 | 模型載入失敗／網路被擋時的表現 |

`validate.js` 是「假 p5、真程式」，所以**邏輯**可信、**畫面**不可信。
講義 E4（用手勢真的玩一輪）只能在自己的電腦完成。

## 重新產生 notebook

改了 `build_notebook.py` 之後：

```bash
cd colab/teachable_machine_snake
python build_notebook.py          # 重新產生 .ipynb
python run_notebook_cells.py      # 本機逐格實跑（會呼叫 node validate.js）
python simulate_colab.py          # 模擬 Colab 空目錄，驗證自動 clone 的路徑
```

> `colab/preview/` 的 HTML 快照目前**不含**這本 notebook（那目錄的三本才在產生清單裡）。

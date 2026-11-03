# IVDC Lesson 8（物件偵測與 CNN）· 材料還原與核對報告

> 對象：IVDC「電腦視覺技術應用」課程 25 頁簡報
> （`8 IVDC Tensorflow and Pytorch for Object Detection and CNN.pptx`）
> 對應文章：<https://kalpakjian.github.io/2026/11/03/ivdc-tf-pytorch-object-detection-cnn/>
> 環境基準日：2026-11

## 1. 摘要

簡報**只有標題是文字層**，其餘全是程式截圖。這份 repo 把它逐頁還原成 9 支可執行腳本，
並在真機上重跑、逐頁核對文章宣稱。核對結果：

- **頁碼宣稱全部正確**（第 2、3、5、7、8–17、18–25 頁）。
- **修正 10 項**事實或推論錯誤（見 §3），其中 **5 項**是我自己文章裡的錯。
- **7 頁**的程式碼被向下捲動箭頭遮住（原本寫「3 處」）。
- TensorFlow 那條線**原本宣告無法驗證**，後來證明可以（`uv run --python 3.11`），已補跑。
- 速度表原本是**跨基準線相除**，已改成同一張影格的單一基準重測。

## 2. 簡報 25 頁對照

「↓」＝該頁程式碼截圖被向下捲動箭頭遮住。

| 頁 | 標題 | 內容 | 狀態 |
|---|---|---|---|
| 1 | Certificate in Application… | 封面 | 文字層只有封面與各頁大標題 |
| 2 | Tensorflow for Object Detection | SSD MobileNet V2 單張圖 | **↓ 第 16 行以下** |
| 3 | Real Time Webcam Detection | TF webcam 迴圈 | **↓ 第 16 行以下** |
| 4 | Real Time Object Detection | 模型建議（SSD MobileNet V2／EfficientDet／Faster R-CNN／YOLO） | 純文字 |
| 5 | Pytorch for Object Detection | `fasterrcnn_resnet50_fpn(weights="DEFAULT")` | **↓ 第 12 行以下** |
| 6 | Real Time Webcam Detection | torch webcam | **↓ 第 13 行以下** |
| 7 | Yolo (Recommended) | 四行程式 ＋ 模型比較（含 DETR） | 只有 4 行 |
| 8 | Tensorflow for CNN | 匯入 ＋ 印版本 | — |
| 9 | Tensorflow for CNN | 與第 8 頁完全相同 | **重複頁** |
| 10–12 | Load Data | `mnist.load_data()` → 形狀 → `reshape` + `/255.0` | — |
| 13 | CNN | Keras `Sequential` 模型 | — |
| 14 | CNN Model Output | `compile` ＋ `fit(epochs=5, validation_split=0.1)` | — |
| 15 | CNN Model Output | 示範輸出 `0.95 / 0.15` → `0.99 / 0.03` | 標題寫 Example output |
| 16–17 | Classification Result | `predict` ＋ `argmax`、輸出 7/7 | — |
| 18 | Or you could use Pytorch | 匯入 ＋ 印版本 | **↓** |
| 19 | Load Data | `torchvision.datasets.MNIST` | **↓ 第 16 行以下** |
| 20 | Load Data | 預期輸出 60000／10000／`(1, 28, 28)` | — |
| 21 | CNN | `nn.Module` 版 CNN | 底部兩行被裁掉（不是箭頭） |
| 22 | CNN Model Output | `DataLoader` ＋ `CrossEntropyLoss` ＋ `Adam(lr=0.001)` | **↓ 第 16 行以下** |
| 23 | CNN Model Output | 示範輸出 `0.1805` → `0.0225` | 標題寫 Example output |
| 24–25 | Classification Result | torch 版推論、輸出 7/7 | 第 25 頁與第 17 頁同 |

**被遮住的頁面共 7 頁**：第 2、3、5、6、18、19、22。
每一支腳本的 docstring 都寫了它對應哪一頁、從第幾行開始是「補完」。

## 3. 勘誤清單

### 3.1 簡報沒說、但一定會踩的（5 項）

| # | 現象 | 正確做法 | 證據 |
|---|---|---|---|
| 1 | `hasattr(cv2, "imshow")` 回 `True`，但呼叫就丟 `(-2:Unspecified error) The function is not implemented` | 要**真的呼叫一次**才驗得出來；`currentUIFramework()` 回空字串是徵兆 | OpenCV 5.0.0 headless 實測，訊息與原文一致 |
| 2 | `cv2.VideoCapture(0)` 開得起來卻是全黑 | 逐個 index 試、量畫面平均亮度 | 實機 camera 0 亮度 2.4／camera 2 亮度 93–110（作者機器） |
| 3 | `cv2.VideoCapture(0, cv2.CAP_DSHOW)` 在 Linux/macOS **每個 index 都失敗** | 依平台選 backend：`CAP_DSHOW if win32 else CAP_ANY` | Linux 實測 `isOpened()=False` vs `CAP_ANY=True` |
| 4 | 「丟 10 幀暖機」在 30 fps 只有 0.33 秒，自動曝光要 1–2 秒 | 用時間判斷（`while time.time()-t0 < 1.5`） | 實作邏輯計算 |
| 5 | `tensorflow_hub` import 就死：`No module named 'pkg_resources'` | setuptools ≥ 81 已移除 `pkg_resources`；本機要 `pip install 'setuptools<81'` | setuptools 84.0.0 實測；**Colab 是 80.10.2，不需要** |

### 3.2 我的文章寫錯的（5 項，已全部更正）

| # | 原本寫 | 正確 | 怎麼發現 |
|---|---|---|---|
| 6 | `optimizer='adam'` vs `optim.Adam(lr=1e-3)`「預設學習率不同」 | **兩邊預設都是 1e-3** | 讀 API：Keras 3.15.1 = 0.001、torch = 0.001 |
| 7 | 表格用 `fasterrcnn_resnet50`／`fasterrcnn_mobilenet` 等簡寫 | torchvision 只有 `fasterrcnn_resnet50_fpn`、`fasterrcnn_mobilenet_v3_large_fpn`、`..._320_fpn`、`ssdlite320_mobilenet_v3_large`，簡寫會 `AttributeError` | 讀 `torchvision.models.detection.faster_rcnn.__all__` |
| 8 | 「實測結果幾乎吻合」（TF 段） | 當時**根本沒跑**；補跑後 test accuracy **0.9872** | `uv run --python 3.11 --with tensorflow-cpu` 實跑 |
| 9 | 「loss 幾乎逐位吻合，**證明架構還原正確**」 | loss 受初始化影響，不能當證據；硬證據是**參數量 225,034**（兩框架一致） | 兩邊 `count_params()` / `numel()` 實測 |
| 10 | 「實測差距 **34 倍**」（`37.4 ÷ 1.1`） | **25.6 倍**（1.4 → 35.8 FPS，同一張影格）；34 是跨基準線相除 | 同場景重測（見 §4） |

順帶更正兩處：

- 「硬猜成 `toilet` 或 **`truck`**」→ 實測是 `toilet` 或 **`refrigerator`**，`truck` 沒出現過。
- 「**記 YOLO**，因為速度與準確度天花板最好」→ 理由是**四行程式碼**；`ssdlite320` 在 `bus.jpg` 上信心
  反而更高（`person 0.989`／`bus 0.985` vs `0.866`／`0.873`），速度也幾乎相同（33.1 vs 35.8 FPS）。

## 4. 實測數據（同一張 1280×720 實機影格）

Linux / CPU、門檻 0.5、單張推論；畫面是洗衣機（不在 COCO 80 類別裡）。

| 模型 | 延遲 | 速度 | 最高信心 | ≥0.5 檢出 | 猜成什麼 |
|---|---|---|---|---|---|
| `fasterrcnn_resnet50_fpn`（簡報原版） | 731 ms | **1.4 FPS** | 0.584 | 1 | `toilet` |
| `fasterrcnn_resnet50_fpn` ＋ `min_size=400` | 266 ms | 3.8 FPS | 0.494 | 0 | — |
| `fasterrcnn_mobilenet_v3_large_fpn` | 137 ms | 7.3 FPS | **0.697** | 2 | `toilet`、`refrigerator` |
| `fasterrcnn_mobilenet_v3_large_320_fpn` | 29 ms | 34.6 FPS | 0.464 | **0** | — |
| `ssdlite320_mobilenet_v3_large` | 30 ms | 33.1 FPS | 0.561 | 1 | `refrigerator` |
| `yolov8n` 640 / 960 / 1280 | 28/36/33 ms | 35.8/27.5/30.0 FPS | 0.404/0.253/0.394 | **0 / 0 / 0** | `refrigerator`, `toilet` |

三個結論：

1. **最快的模型一個東西都沒偵測到**——「快」跟「有用」是兩件事。
2. **這一幕沒有模型答對**，因為洗衣機不在 COCO 類別裡，只能硬猜。
3. **`min_size=400` 換來 2.7 倍**（731→266 ms），而此場景本來就沒有真陽性可掉，是純賺。

換到有答案的 `bus.jpg`（YOLOv8n，同一台機器）：

| `imgsz` | 延遲 | 速度 | ≥0.5 檢出 | 內容 |
|---|---|---|---|---|
| 640 | 27.6 ms | 36.2 FPS | 4 | `bus 0.873` ＋ `person 0.866 / 0.853 / 0.825` |
| 960 | 29.6 ms | 33.8 FPS | 4 | 同樣四個，`person 0.886` 最高 |
| 1280 | 41.8 ms | 23.9 FPS | 6 | 多出 `bus 0.690 / 0.634 / 0.542` **三個重複框** |

> 解析度拉高檢出更多要打折看：1280 多出來的是同一台公車被框三次，外加一個 0.289 的 `skateboard`。
> NMS 救不回重疊框。

## 5. 環境矩陣

| 項目 | 本機（Linux，量測基準） | Colab 2026.10（實測同版本重現） | 作者 Windows（文章中數字） |
|---|---|---|---|
| Python | 3.14.8 / 3.11 / 3.13 | 3.13.18 | 3.15.1 |
| torch / torchvision | 2.15.0+cpu / 0.29.2+cpu | **2.11.0+cpu / 0.26.0+cpu** | 2.14.1+cpu / 0.29.1+cpu |
| TensorFlow / hub | 2.21.0 / 0.16.1 | 2.21.0 / 0.16.1（皆預裝） | 未安裝（原宣告裝不上） |
| setuptools | 84（**需 < 81**） | **80.10.2（不需降版）** | — |
| OpenCV | 5.0.0（headless） | 5.0.0.93 | 5.0.0 |
| ultralytics | 8.4.201 | 需 `%pip install`（未預裝） | 8.x |
| webcam / GUI | 有相機、無 GUI | **皆無** → 用 `--video` | 有 |

9 支腳本在「本機」與「Colab 同版本」兩套環境都完整跑過。

## 6. Colab 上怎麼跑

| 情境 | 做法 |
|---|---|
| 能連 GitHub | Colab 開 [`colab/ivdc_exam_all_in_one.ipynb`](colab/ivdc_exam_all_in_one.ipynb) → Run all |
| GitHub 被擋 | 這個 notebook 本身就是完整程式碼（`%%writefile` 內嵌 9 支腳本），下載後上傳到 Colab 即可 |
| 只能傳一個檔 | 上傳 `ivdc_handout.zip` → `!unzip -q ivdc_handout.zip` → `%cd ivdc_handout` |

**三條規則**

1. Colab **沒有 webcam、沒有螢幕** → `--video clip.mp4`、不要 `imshow`。
2. **用 `%run`，不要用 `!python`** —— `!python` 走 shell 的 PATH，可能指到另一顆直譯器
   （實測踩到：kernel 是 3.13，`!python` 用了系統 3.14 → `No module named 'cv2'`）。
3. **`setuptools` 不用降版**（Colab 是 80.10.2）。

### 錯誤 → 解法

| 症狀 | 解法 |
|---|---|
| `cv2.error ... not implemented ... GTK+` | 不要 `imshow`，用 `--no-show`，圖以 `display(Image(...))` 呈現 |
| `[錯誤] 找不到有畫面的攝影機` | Colab 沒相機 → `--video clip.mp4` |
| `No module named 'ultralytics'` | `%pip install -q ultralytics` |
| `No module named 'cv2'` 且用了 `!python` | 改成 `%run` |
| TF 印 `CUDA Runtime error ... GPU will not be used` | CPU runtime 的正常 stub，不影響結果 |
| TF-Hub 卡住 | 首次下載約 20 MB，等它 |
| Runtime disconnected | `Runtime → Run all`（全部重跑 < 2 分鐘） |

## 7. 驗證方式

| 項目 | 方法 | 結果 |
|---|---|---|
| 9 支腳本編譯 | `python -m py_compile` | 全通過 |
| 腳本行為 | 實機 / 影片 / 圖片逐支執行 | 全通過（見各腳本 §「實測」） |
| notebook（clone 版） | nbclient + ipykernel，Colab 同版本 | 23 格、**0 錯誤** |
| notebook（自包含版） | 同上，**從空目錄**（無 git、無 repo） | 43 格、**0 錯誤**；`%%writefile` 產物與 repo **md5 一致** |
| 文章內部連結 | `tools/notes-qa/check_public_links.py` | 649 頁 / 19,684 連結、**0 broken** |
| 中文粗體渲染 | `tools/notes-qa/check_cjk_bold.js` | 0 受影響 |

## 8. 還沒驗的（誠實標記）

1. **Windows 專屬路徑**：`CAP_DSHOW` vs `CAP_MSMF` 的實際行為，以及作者機器的原始 1.1 FPS。
   這台是 Linux，量不到；不影響任何結論（僅為平台註記）。
2. **Colab GPU runtime**：本報告的 Colab 驗證是在 CPU 版同版本環境做的。T4/L4 上
   `torch.cuda.is_available()` 應為 `True`（腳本 `07` 支援 `--device cuda`），未實測。
3. **簡報頁碼以外的教材內容**（例如講師口述）當然不在比對範圍。

## 9. 重跑

```bash
git clone https://github.com/kalpakjian/ivdc_handout && cd ivdc_handout
python src/00_check_env.py                     # 先自檢
python src/03_torch_object_detection_image.py --image bus.jpg --model ssdlite320
python src/04_torch_webcam_detection.py --video clip.mp4    # 沒有相機時
python bench/bench_detection.py --camera 0 --yolo           # 重跑 §4 那張表
```

TensorFlow 線若在自己電腦被 setuptools 卡住：

```bash
uv run --no-project --python 3.11 --with tensorflow-cpu \
    --with tensorflow-hub --with 'setuptools<81' -- python src/06_tf_cnn_mnist.py
```

## 10. 授權與出處

課程材料版權屬匯縱專業發展中心；本 repo 只還原**程式碼結構**與實測筆記，
不含簡報原檔。程式碼以 MIT 授權使用。

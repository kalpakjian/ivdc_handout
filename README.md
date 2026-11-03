# ivdc_handout — IVDC Lesson 8「物件偵測與 CNN」可執行腳本

課程簡報的程式碼全是截圖（只有標題是文字層），這個目錄是把它逐頁還原成可執行檔案的成果。
每個檔案都獨立可跑，並且用註解標出**哪一行是簡報原文、哪一行是我補的**。

- 🌐 **線上好讀版（入口頁）→ <https://kalpakjian.github.io/ivdc_handout/>** —— 三本 notebook 的 HTML 快照、報告 HTML 版、Colab 連結都在這一頁
- 📄 **完整核對報告（勘誤 10 項、實測數據、Colab 指南）→ [REPORT.md](REPORT.md)**
- 📓 **Colab 考試用筆記本（完全自包含）→ [colab/ivdc_exam_all_in_one.ipynb](colab/ivdc_exam_all_in_one.ipynb)**
- 對應文章：[同一份課堂材料，用 TensorFlow 與 PyTorch 各跑一遍](https://kalpakjian.github.io/2026/11/03/ivdc-tf-pytorch-object-detection-cnn/)

## 標註慣例

| 標記 | 意思 |
|---|---|
| `# [原文]` | 簡報截圖上讀得到的程式碼 |
| `# [補完]` | 截圖被右下角滾動箭頭遮住／講義省略，依框架標準介面補完 |

簡報有三處被滾動箭頭蓋住，三處都用 `# [補完]` 標在原地，不是事後在 README 裡補說明——
半年後你才分得出哪段是自己的。

## 檔案

| 檔案 | 內容 |
|---|---|
| `src/00_check_env.py` | 環境自檢（套件、GUI、攝影機、暖機） |
| `src/01_tf_object_detection_image.py` | TF-Hub SSD MobileNet V2 單張圖 |
| `src/02_tf_webcam_detection.py` | 同上，即時 webcam |
| `src/03_torch_object_detection_image.py` | torchvision 偵測模型單張圖（含模型別名表） |
| `src/04_torch_webcam_detection.py` | torchvision 即時 webcam（多模型可切換） |
| `src/05_yolo_detection.py` | YOLOv8（簡報標「Recommended」的四行方案） |
| `src/06_tf_cnn_mnist.py` | TF/Keras MNIST CNN，五個階段 |
| `src/07_torch_cnn_mnist.py` | PyTorch MNIST CNN，同樣五個階段 |
| `bench/bench_detection.py` | 同一段畫面的偵測模型基準線（筆記 §六 那張表的來源） |

## 簡報頁碼對照

| 頁 | 內容 | 腳本 |
|---|---|---|
| 2–3 | TensorFlow 物件偵測（單張圖／webcam） | `01`、`02` |
| 4 | 模型建議（SSD MobileNet V2／EfficientDet／Faster R-CNN／YOLO） | — |
| 5–6 | PyTorch 物件偵測（單張圖／webcam） | `03`、`04` |
| 7 | Yolo (Recommended) ＋ 模型比較 | `05` |
| 8–17 | TensorFlow CNN（MNIST） | `06` |
| 18–25 | PyTorch CNN（MNIST） | `07` |

25 頁裡有幾頁是重複或半截：第 8、9 頁是同一張截圖；第 16／17 與 24／25 是同一組輸出；
第 21 頁底部兩行被裁掉；第 **2、3、5、6、18、19、22** 頁的程式碼被向下捲動箭頭遮住
（不是 3 頁，是 7 頁）。每支腳本的 docstring 都寫了它對應哪一頁、從第幾行開始是補的。

## 在 Colab 上跑（考試／沒有 webcam 的環境）

Colab 是「無螢幕、無相機、Linux、已預裝大半套件」的環境，跟本機差三件事：

| Colab 2026.10 實際狀態 | 對這些腳本的影響 |
|---|---|
| Python 3.13.18、TF 2.21.0、tensorflow-hub 0.16.1、torch 2.11.0+cpu、torchvision 0.26.0+cpu、opencv 5.0.0、numpy 2.4.6 | **不用裝、不用降版**，8 支腳本在這個組合上實測全部通過 |
| `setuptools` 是 **80.10.2**（< 81） | `pkg_resources` 還在 → `tensorflow_hub` 直接可 import，**不需要 `setuptools<81`**（那是自己電腦遇到 setuptools ≥ 81 才要） |
| **沒有 `ultralytics`** | 只有 `05_yolo_detection.py` 需要先 `!pip install -q ultralytics` |
| **沒有 webcam、沒有 GUI** | `imshow` 自動退回存檔；`02`／`04` 加 `--video 檔案.mp4` 用影片取代攝影機，其餘流程一行不改 |
| **沒有 `git`／GitHub 被擋** | 用 `colab/ivdc_exam_all_in_one.ipynb`（整份腳本內嵌，不用 clone）；或上傳 `ivdc_handout.zip` 後 `!unzip` |

兩本現成的筆記本：

| 筆記本 | 需要網路 | 說明 |
|---|---|---|
| [`colab/ivdc_exam_all_in_one.ipynb`](colab/ivdc_exam_all_in_one.ipynb) | 只下載權重／MNIST | **完全自包含**：9 支腳本用 `%%writefile` 內嵌，原封不動寫成 `src/*.py`，不需要 git clone |
| [`colab/ivdc_exam_quickstart.ipynb`](colab/ivdc_exam_quickstart.ipynb) | 需要 GitHub | `git clone` 版，適合程式碼已經在 repo 裡、想跟著上游更新 |

不想開 Colab、只想快速看內容 → [`colab/preview/`](colab/preview) 有三本的 HTML 快照（`all_in_one`／`quickstart`／`yolo_only`）。

兩本都在「Colab 2026.10 同版本」環境（Python 3.13 / torch 2.11 / TF 2.21 / hub 0.16.1）
用 nbclient 逐格執行過：**0 錯誤**。手動跑的話：

```python
!git clone -q https://github.com/kalpakjian/ivdc_handout
%cd ivdc_handout
%run src/00_check_env.py --skip-camera          # 先自檢
%run src/03_torch_object_detection_image.py --image bus.jpg --model ssdlite320
%run src/04_torch_webcam_detection.py --video clip.mp4 --model ssdlite320   # 沒有相機就給影片
```

<strong>用 `%run` 不要用 `!python`。</strong> `!python` 走的是 shell 的 PATH，可能指到另一個直譯器
（我就被咬過：筆記本 kernel 是 3.13，`!python` 卻用了系統的 3.14，於是 `No module named cv2`）。
`%run` 一定用 kernel 那顆；`%pip` 同理，一定裝進 kernel 的環境。

沒有 webcam 又需要「即時偵測」時，用一張圖合成一段影片即可：

```python
import cv2
img = cv2.imread("bus.jpg")
w = cv2.VideoWriter("clip.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 15.0, (img.shape[1], img.shape[0]))
for _ in range(30):
    w.write(img)
w.release()
```

## 安裝

三條線的相依互不相容（尤其 TF 要 Python 3.11/3.12，3.15 沒有 wheel），
所以建議用 `uv` 開臨時環境，不要裝在同一個 venv 裡：

```bash
# PyTorch 線（03 / 04 / 07）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install opencv-python pillow      # 要彈窗就別裝 opencv-python-headless

# TensorFlow 線（01 / 02 / 06）
uv run --no-project --python 3.11 --with tensorflow-cpu \
    --with tensorflow-hub --with 'setuptools<81' \
    --with opencv-python-headless -- python src/06_tf_cnn_mnist.py

# YOLO（05）
pip install ultralytics
```

`--with 'setuptools<81'` 不是裝飾：`tensorflow_hub` 會 `from pkg_resources import ...`，
而 setuptools 81 之後把 `pkg_resources` 拿掉了，於是 import 直接死（實測 setuptools 84.0.0 → `ModuleNotFoundError: pkg_resources`）。

## 跑法

```bash
python src/00_check_env.py                                  # 先自檢，換機器都先跑這支

python src/01_tf_object_detection_image.py  --image bus.jpg
python src/02_tf_webcam_detection.py                        # 或 --no-show --max-frames 60
python src/03_torch_object_detection_image.py --image bus.jpg --model ssdlite320
python src/04_torch_webcam_detection.py --model fasterrcnn_mobilenet_320
python src/04_torch_webcam_detection.py --model fasterrcnn_resnet50_fpn --min-size 400
python src/05_yolo_detection.py --source bus.jpg --imgsz 640
python src/06_tf_cnn_mnist.py --epochs 5
python src/07_torch_cnn_mnist.py --epochs 5
```

每支都支援 `--no-show`（headless 機器改存檔）與 `--max-frames`（煙霧測試），
所以 CI／沒有螢幕的機器也跑得完。

## 同一段畫面的基準線

要比 FPS，就得**同一張影格、同一個門檻、同一台機器**。這支腳本對每張圖跑同一批模型，
量純推論時間，順便印「最高信心」與「≥門檻有幾個」——所以「很快但什麼都沒看到」會直接現形：

```bash
python bench/bench_detection.py --camera 0 --yolo      # 現場抓一張 1280×720 再跑
python bench/bench_detection.py --frame frame.jpg --json out.json
```

實測（Linux / CPU / 一支 1280×720 USB 攝影機 / 門檻 0.5；畫面是洗衣機）：

| 模型 | 延遲 | 速度 | 最高信心 | ≥0.5 檢出 | 猜成什麼 |
|---|---|---|---|---|---|
| `fasterrcnn_resnet50_fpn` | 752 ms | 1.3 FPS | 0.584 | 1 | `toilet` |
| `fasterrcnn_resnet50_fpn` + `min_size=400` | 262 ms | 3.9 FPS | 0.494 | 0 | — |
| `fasterrcnn_mobilenet_v3_large_fpn` | 136 ms | 7.4 FPS | 0.697 | 2 | `refrigerator`、`toilet` |
| `fasterrcnn_mobilenet_v3_large_320_fpn` | 29 ms | 34.3 FPS | 0.464 | **0** | — |
| `ssdlite320_mobilenet_v3_large` | 33 ms | 30.5 FPS | 0.561 | 1 | `refrigerator` |
| `yolov8n` 640 | 23 ms | 43.2 FPS | 0.404 | **0** | `refrigerator` |
| `yolov8n` 960 | 32 ms | 31.0 FPS | 0.253 | **0** | `refrigerator` |
| `yolov8n` 1280 | 34 ms | 29.8 FPS | 0.394 | **0** | `toilet` |

三件事：

1. **最快的模型一個都沒偵測到**。洗衣機不在 COCO 的 80 類別裡，模型只能硬猜
   （`toilet`／`refrigerator`），所以「快」跟「有用」是兩件事。
2. **`min_size=400` 換來 2.9 倍**（752→262 ms），而這一幕本來就沒有真陽性可掉，是純賺。
3. 這張表的「速度」是純 `model(...)` 的時間，**不含**攝影機讀取與畫框；
   `src/04_torch_webcam_detection.py` 顯示的 9.2 FPS 是端到端（含 cv2 讀幀 + 畫框 + 存圖），
   兩者不要混在一起比。

## 逐支腳本的實測（2026-11，Linux / CPU）

環境：Python 3.11 與 3.14、TF 2.21.0、Keras 3.15.1、torch 2.15.0+cpu、
torchvision 0.29.2+cpu、ultralytics 8.4.201、OpenCV 5.0.0（headless）。

| 腳本 | 結果 |
|---|---|
| `00_check_env.py` | 抓到手上有 GUI＝無、camera 0 可用（brightness 41） |
| `01`（bus.jpg） | person 0.861、bus 0.756、person 0.750…（門檻 0.4 共 10 個） |
| `02`（webcam，6 幀） | 8.6 FPS，headless 存檔成功 |
| `03`（bus.jpg，ssdlite320） | person 0.989、bus 0.985、person 0.865、person 0.624（共 4 個） |
| `04`（webcam，ssdlite320） | 9.2 FPS，camera 0 auto-pick |
| `05`（bus.jpg，yolov8n imgsz=640） | 6 個物件、最高信心 0.87、推論 19.8 ms（≈50 FPS） |
| `06`（MNIST 5 epochs） | test accuracy **0.9872**、params 225,034 |
| `07`（MNIST 2 epochs 煙霧測試） | test accuracy 0.9887、params 225,034 |

對照：同一顆網路在 TF 與 torch 的參數量都是 225,034 —— 這是「架構等價」的證據，
loss 曲線接近只能算同量級（隨機初始化一換就會漂）。

## 已知坑（都寫進程式註解了）

1. **`tensorflow_hub` + setuptools ≥ 81** → `ModuleNotFoundError: pkg_resources`。
   這是 import 階段就死，訊息完全看不出跟 TF Hub 有關。
2. **`hasattr(cv2, "imshow")` 會騙人**：headless 版函式存在、呼叫才丟 `not implemented`。
3. **`cv2.VideoCapture(0)` 可能開得起來卻是全黑**，要量亮度；而且 index 不一定是 0。
4. **`CAP_DSHOW` 是 Windows 專屬**，寫死會讓 Linux/macOS 每個 index 都失敗。
5. **暖機「10 幀」不夠**（30 fps ≈ 0.33 秒），自動曝光要 1～2 秒，請用時間判斷。
6. **torchvision 簡寫不存在**：`fasterrcnn_resnet50` 要寫 `fasterrcnn_resnet50_fpn`。
7. **SSD 家族沒有 `model.weights`**，類別名稱要從 `WeightsEnum` 拿。
8. **`min_size=800` 是 CPU 上的隱形稅**：720p 短邊被放大到 800，降到 400 可換 2～3 倍 FPS。

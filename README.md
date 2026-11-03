# ivdc_handout — IVDC Lesson 8「物件偵測與 CNN」可執行腳本

課程簡報的程式碼全是截圖（只有標題是文字層），這個目錄是把它逐頁還原成可執行檔案的成果。
每個檔案都獨立可跑，並且用註解標出**哪一行是簡報原文、哪一行是我補的**。

對應文章：[同一份課堂材料，用 TensorFlow 與 PyTorch 各跑一遍](https://kalpakjian.github.io/2026/11/03/ivdc-tf-pytorch-object-detection-cnn/)

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

## 實測（2026-11，Linux / CPU）

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

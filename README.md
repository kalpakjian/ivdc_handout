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

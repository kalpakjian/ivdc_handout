#!/usr/bin/env python3
"""01_tf_object_detection_image.py — TensorFlow/TF-Hub SSD MobileNet V2 單張圖偵測。

用法:
    python 01_tf_object_detection_image.py --image bus.jpg
    python 01_tf_object_detection_image.py --image bus.jpg --threshold 0.4 --show

模型網址與環境（實測 2026-11）
    簡報用的 https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2 仍然可用：
    curl 會回 404（網頁層已下架），但 hub.load() 還是解析得到模型檔。
    真正會擋人的是 tensorflow_hub 依賴 pkg_resources，而 setuptools>=81 已經把它移除，
    於是 import tensorflow_hub 直接 ModuleNotFoundError。解法是釘住 setuptools：
        uv run --no-project --python 3.11 --with tensorflow-cpu \
            --with tensorflow-hub --with 'setuptools<81' -- python 01_...py
    想換模型（例如 Kaggle Models 上的同名版本）就用 --model-url。

標註慣例
    # [原文]  簡報截圖上讀得到的程式碼
    # [補完]  截圖被滾動箭頭遮住／講義省略，依框架標準介面補完

簡報對應：第 2 頁（Tensorflow for Object Detection），第 16 行以下被向下箭頭遮住。
"""

from __future__ import annotations

import argparse
import os
import sys

DEFAULT_MODEL_URL = "https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2"

# COCO id -> 名稱（SSD MobileNet V2 的 labelmap；缺號代表該 id 在 COCO 裡沒用）
# [補完] 簡報只印 class id。要看得懂輸出就得有這張表。
COCO_LABELS = {
    1: "person", 2: "bicycle", 3: "car", 4: "motorcycle", 5: "airplane", 6: "bus",
    7: "train", 8: "truck", 9: "boat", 10: "traffic light", 11: "fire hydrant",
    13: "stop sign", 14: "parking meter", 15: "bench", 16: "bird", 17: "cat",
    18: "dog", 19: "horse", 20: "sheep", 21: "cow", 22: "elephant", 23: "bear",
    24: "zebra", 25: "giraffe", 27: "backpack", 28: "umbrella", 31: "handbag",
    32: "tie", 33: "suitcase", 34: "frisbee", 35: "skis", 36: "snowboard",
    37: "sports ball", 38: "kite", 39: "baseball bat", 40: "baseball glove",
    41: "skateboard", 42: "surfboard", 43: "tennis racket", 44: "bottle",
    46: "wine glass", 47: "cup", 48: "fork", 49: "knife", 50: "spoon", 51: "bowl",
    52: "banana", 53: "apple", 54: "sandwich", 55: "orange", 56: "broccoli",
    57: "carrot", 58: "hot dog", 59: "pizza", 60: "donut", 61: "cake", 62: "chair",
    63: "couch", 64: "potted plant", 65: "bed", 67: "dining table", 70: "toilet",
    72: "tv", 73: "laptop", 74: "mouse", 75: "remote", 76: "keyboard",
    77: "cell phone", 78: "microwave", 79: "oven", 80: "toaster", 81: "sink",
    82: "refrigerator", 84: "book", 85: "clock", 86: "vase", 87: "scissors",
    88: "teddy bear", 89: "hair drier", 90: "toothbrush",
}


def load_model(model_url: str):
    """載入 TF-Hub 模型；失敗時給出可執行的下一步，而不是丟一坨 traceback。"""
    import tensorflow_hub as hub

    try:
        return hub.load(model_url)
    except Exception as exc:
        print(f"[錯誤] 載入模型失敗: {model_url}", file=sys.stderr)
        print(f"        {type(exc).__name__}: {str(exc)[:300]}", file=sys.stderr)
        print("\n可能原因與解法：", file=sys.stderr)
        print("  1. setuptools>=81 移除了 pkg_resources → pip install 'setuptools<81'",
              file=sys.stderr)
        print("  2. 沒有網路 / 防火牆擋掉 tfhub.dev 與 storage.googleapis.com", file=sys.stderr)
        print("  3. 想換模型：--model-url <kaggle 或 tfhub 網址>", file=sys.stderr)
        print("  4. 先確認環境：python 00_check_env.py", file=sys.stderr)
        return None


def imshow_available() -> bool:
    # [原文] 坑四：不能只判斷函式存在，要真的呼叫一次
    import cv2
    import numpy as np

    try:
        cv2.imshow("__probe__", np.zeros((4, 4, 3), np.uint8))
        cv2.waitKey(1)
        cv2.destroyWindow("__probe__")
        return True
    except Exception:
        return False


def draw(frame, boxes, scores, classes, threshold: float):
    """在畫面上畫框 + 標籤。boxes 是歸一化 (ymin, xmin, ymax, xmax)。"""
    import cv2

    h, w = frame.shape[:2]
    for box, score, cls in zip(boxes, scores, classes):
        if score < threshold:
            continue
        # [原文] 座標是 0～1 的歸一化值，順序是 ymin, xmin, ymax, xmax
        ymin, xmin, ymax, xmax = box
        p0 = (int(xmin * w), int(ymin * h))
        p1 = (int(xmax * w), int(ymax * h))
        cv2.rectangle(frame, p0, p1, (0, 0, 255), 2)
        label = f"{COCO_LABELS.get(int(cls), 'class_' + str(int(cls)))} {score:.2f}"
        cv2.putText(frame, label, (p0[0], max(p0[1] - 6, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
    return frame


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TF-Hub SSD MobileNet V2 單張圖偵測")
    parser.add_argument("--image", required=True, help="輸入圖片路徑")
    parser.add_argument("--model-url",
                        default=os.environ.get("IVDC_TF_MODEL_URL", DEFAULT_MODEL_URL))
    parser.add_argument("--threshold", type=float, default=0.5, help="信心門檻（預設 0.5）")
    parser.add_argument("--out", default="out/tf_detection.jpg", help="輸出標註圖")
    parser.add_argument("--show", action="store_true", help="彈窗顯示（需要 GUI）")
    args = parser.parse_args(argv)

    import cv2
    import tensorflow as tf

    print(f"Python {sys.version.split()[0]} / TF {tf.__version__}")
    print(f"模型: {args.model_url}")
    model = load_model(args.model_url)
    if model is None:
        return 2

    # [原文] 讀圖 → BGR 轉 RGB → uint8 張量 → 加 batch 維度
    image = cv2.imread(args.image)
    if image is None:
        print(f"[錯誤] 讀不到圖片: {args.image}", file=sys.stderr)
        return 2
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    input_tensor = tf.convert_to_tensor(image_rgb, dtype=tf.uint8)
    input_tensor = tf.expand_dims(input_tensor, 0)  # (1, H, W, 3)

    # [原文] model(input_tensor) 一次做完前處理 + 推論 + NMS
    detections = model(input_tensor)

    # [補完] 簡報截圖到此為止（被右下角滾動箭頭蓋住），以下依 TF-Hub 標準介面補完
    boxes = detections["detection_boxes"][0].numpy()
    scores = detections["detection_scores"][0].numpy()
    classes = detections["detection_classes"][0].numpy().astype(int)

    kept = [(b, s, c) for b, s, c in zip(boxes, scores, classes) if s >= args.threshold]
    print(f"\n檢出 {len(kept)} 個（門檻 {args.threshold}）")
    for box, score, cls in kept:
        name = COCO_LABELS.get(int(cls), "class_" + str(int(cls)))
        ymin, xmin, ymax, xmax = box
        print(f"  {name:16s} score={score:.3f} "
              f"box=({xmin:.3f}, {ymin:.3f}, {xmax:.3f}, {ymax:.3f}) 歸一化")

    annotated = draw(image.copy(), boxes, scores, classes, args.threshold)
    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)
    cv2.imwrite(args.out, annotated)
    print(f"\n已存檔: {args.out}")

    if args.show:
        if not imshow_available():
            print("[提醒] 這台機器沒有 GUI backend，只輸出檔案（見 00_check_env.py）")
            return 0
        cv2.imshow("TF SSD MobileNet V2", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

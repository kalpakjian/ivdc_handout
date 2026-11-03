#!/usr/bin/env python3
"""02_tf_webcam_detection.py — TensorFlow/TF-Hub SSD MobileNet V2 即時 webcam 偵測。

用法:
    python 02_tf_webcam_detection.py
    python 02_tf_webcam_detection.py --camera 2 --threshold 0.4
    python 02_tf_webcam_detection.py --no-show --max-frames 60   # 無 GUI 機器煙霧測試

四個坑都解掉了（對應筆記 §十）：
    坑一 相機不一定在 index 0      -> pick_camera() 逐個開、量亮度
    坑二 Windows 要 DirectShow      -> 依序試 DSHOW / MSMF / ANY
    坑三 開機前幾幀不能用           -> 依「時間」暖機 1.5 秒（不是固定 10 幀）
    坑四 imshow 沒有 fallback 會崩  -> imshow_available()，沒有 GUI 就存檔

標註慣例
    # [原文]  簡報截圖上讀得到的程式碼
    # [補完]  截圖被滾動箭頭遮住／講義省略，依框架標準介面補完

簡報對應：第 3 頁（Real Time Webcam Detection），第 16 行以下被向下箭頭遮住。
"""

from __future__ import annotations

import argparse
import os
import sys
import time

DEFAULT_MODEL_URL = "https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2"


def _load_labels() -> dict:
    """標籤表沿用 01（避免兩份 COCO 對照表各自走鐘）；找不到就退回 class id。"""
    # [補完] 簡報的 webcam 版沒有印類別名稱
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from importlib import import_module

        return import_module("01_tf_object_detection_image").COCO_LABELS
    except Exception:
        return {}


def imshow_available() -> bool:
    # [原文] 坑四
    import cv2
    import numpy as np

    try:
        cv2.imshow("__probe__", np.zeros((4, 4, 3), np.uint8))
        cv2.waitKey(1)
        cv2.destroyWindow("__probe__")
        return True
    except Exception:
        return False


def camera_backends() -> list[int]:
    # [原文] 坑二：Windows 上 CAP_MSMF 常常打不開
    import cv2

    if sys.platform == "win32":
        return [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    return [cv2.CAP_ANY]


def pick_camera(preferred: int = 0, max_index: int = 6, min_brightness: float = 20.0):
    # [原文] 坑一：VideoCapture(0) 可能開得起來但全黑，不會報錯
    import cv2

    order = [preferred] + [i for i in range(max_index + 1) if i != preferred]
    for idx in order:
        for api in camera_backends():
            cap = cv2.VideoCapture(idx, api)
            if not cap.isOpened():
                cap.release()
                continue
            mean = -1.0
            t0 = time.time()
            while time.time() - t0 < 1.0:
                ok, frame = cap.read()
                if ok and frame is not None:
                    mean = float(frame.mean())
            if mean >= min_brightness:
                print(f"using camera {idx} (backend {api}, brightness {mean:.0f})")
                return cap
            cap.release()
            print(f"camera {idx} (backend {api}): black (mean {mean:.1f}) - skip")
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TF-Hub SSD MobileNet V2 即時偵測")
    parser.add_argument("--camera", type=int, default=0, help="偏好的攝影機 index")
    parser.add_argument("--model-url",
                        default=os.environ.get("IVDC_TF_MODEL_URL", DEFAULT_MODEL_URL))
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--warmup", type=float, default=1.5, help="暖機秒數（自動曝光）")
    parser.add_argument("--max-frames", type=int, default=0, help="跑幾個 frame 就停（0=不限）")
    parser.add_argument("--no-show", action="store_true", help="不要彈窗，改成存圖")
    parser.add_argument("--out-dir", default="out/webcam_tf", help="--no-show 時的存圖目錄")
    args = parser.parse_args(argv)

    import cv2
    import tensorflow as tf
    import tensorflow_hub as hub

    labels = _load_labels()
    print(f"Python {sys.version.split()[0]} / TF {tf.__version__}")
    try:
        model = hub.load(args.model_url)
    except Exception as exc:
        print(f"[錯誤] 載入模型失敗: {args.model_url}", file=sys.stderr)
        print(f"        {type(exc).__name__}: {str(exc)[:200]}", file=sys.stderr)
        print("        常見原因：setuptools>=81 移除 pkg_resources（pip install 'setuptools<81'）",
              file=sys.stderr)
        return 2

    cap = pick_camera(args.camera)
    if cap is None:
        print("[錯誤] 找不到有畫面的攝影機（先跑 00_check_env.py）", file=sys.stderr)
        return 2

    show_gui = (not args.no_show) and imshow_available()
    if not show_gui:
        os.makedirs(args.out_dir, exist_ok=True)
        print(f"[提醒] 沒有 GUI backend，改成存圖到 {args.out_dir}/")

    # [原文] 坑三：前幾幀不能用。簡報用固定 10 幀，這裡用時間（10 幀≈0.3 秒，不夠）
    t0 = time.time()
    while time.time() - t0 < args.warmup:
        cap.read()

    frames = 0
    fps = 0.0
    last = time.time()
    saved = 0
    processed = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("[錯誤] 讀不到 frame（相機被拔掉？）", file=sys.stderr)
                break
            processed += 1

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # [原文] 同一套前處理：uint8 張量 + batch 維度
            input_tensor = tf.convert_to_tensor(rgb, dtype=tf.uint8)
            input_tensor = tf.expand_dims(input_tensor, 0)

            detections = model(input_tensor)

            # [補完] 門檻過濾 + 畫框（簡報截圖沒這段）
            h, w = frame.shape[:2]
            boxes = detections["detection_boxes"][0].numpy()
            scores = detections["detection_scores"][0].numpy()
            classes = detections["detection_classes"][0].numpy().astype(int)
            for box, score, cls in zip(boxes, scores, classes):
                if score < args.threshold:
                    continue
                ymin, xmin, ymax, xmax = box
                p0 = (int(xmin * w), int(ymin * h))
                p1 = (int(xmax * w), int(ymax * h))
                cv2.rectangle(frame, p0, p1, (0, 0, 255), 2)
                label = f"{labels.get(int(cls), 'class_' + str(int(cls)))} {score:.2f}"
                cv2.putText(frame, label, (p0[0], max(p0[1] - 6, 12)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

            frames += 1
            now = time.time()
            if now - last >= 0.5:
                fps = frames / (now - last)
                frames, last = 0, now
            cv2.putText(frame, f"{fps:5.1f} FPS", (10, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

            if show_gui:
                cv2.imshow("TF Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                path = os.path.join(args.out_dir, f"frame_{saved:04d}.jpg")
                cv2.imwrite(path, frame)
                saved += 1

            if args.max_frames and processed >= args.max_frames:
                break
    finally:
        cap.release()
        if show_gui:
            cv2.destroyAllWindows()

    if not show_gui:
        print(f"已存 {saved} 張到 {args.out_dir}/")
    print(f"最後一次量到的速度: {fps:.1f} FPS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

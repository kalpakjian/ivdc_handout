#!/usr/bin/env python3
"""04_torch_webcam_detection.py — torchvision 偵測模型即時 webcam（多模型可切換）。

用法:
    python 04_torch_webcam_detection.py
    python 04_torch_webcam_detection.py --model fasterrcnn_mobilenet_320
    python 04_torch_webcam_detection.py --model fasterrcnn_resnet50_fpn --min-size 400
    python 04_torch_webcam_detection.py --no-show --max-frames 30    # 無 GUI 煙霧測試

速度與模型別名
    `--model` 接受 torchvision 真名或筆記裡的簡寫（見 03 的 MODEL_ALIASES）。
    CPU 上真正該調的是 `--min-size`：預設 800 會把 720p 短邊放大到 800，
    調到 400 通常可拿回 2～3 倍 FPS。

標註慣例
    # [原文]  簡報截圖上讀得到的程式碼
    # [補完]  截圖被滾動箭頭遮住／講義省略，依框架標準介面補完

簡報對應：第 6 頁（Real Time Webcam Detection），第 13 行以下被向下箭頭遮住。
"""

from __future__ import annotations

import argparse
import os
import sys
import time

# [補完] 簡寫 → torchvision 真實函式名（與 03 相同，避免兩份表走鐘就從 03 借）
MODEL_ALIASES = {
    "fasterrcnn_resnet50": "fasterrcnn_resnet50_fpn",
    "fasterrcnn_resnet50_v2": "fasterrcnn_resnet50_fpn_v2",
    "fasterrcnn_mobilenet": "fasterrcnn_mobilenet_v3_large_fpn",
    "fasterrcnn_mobilenet_320": "fasterrcnn_mobilenet_v3_large_320_fpn",
    "ssdlite320": "ssdlite320_mobilenet_v3_large",
    "retinanet": "retinanet_resnet50_fpn_v2",
}


def categories_for(resolved: str, model) -> list[str]:
    """COCO 類別名稱。SSD 家族的 model 沒有 .weights 屬性，退回 WeightsEnum。"""
    # [補完] 實測 ssdlite320 沒有 .weights，直接取會 AttributeError
    weights = getattr(model, "weights", None)
    if weights is not None:
        return list(weights.meta["categories"])
    enum = {
        "ssdlite320_mobilenet_v3_large": "SSDLite320_MobileNet_V3_Large_Weights",
        "ssd300_vgg16": "SSD300_VGG16_Weights",
    }.get(resolved)
    if enum:
        try:
            from torchvision.models import get_weight

            return list(get_weight(f"{enum}.DEFAULT").meta["categories"])
        except Exception:
            pass
    return []


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
    # [原文] 坑二
    import cv2

    if sys.platform == "win32":
        return [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    return [cv2.CAP_ANY]


def pick_camera(preferred: int = 0, max_index: int = 6, min_brightness: float = 20.0):
    # [原文] 坑一
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
    parser = argparse.ArgumentParser(description="torchvision 偵測模型即時 webcam")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--video", default="",
                        help="用影片檔當來源（Colab／伺服器沒有 webcam 時用這個）")
    parser.add_argument("--model", default="fasterrcnn_resnet50_fpn")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--min-size", type=int, default=None,
                        help="覆寫 min_size（CPU 上調小可大幅加速，例如 400）")
    parser.add_argument("--max-size", type=int, default=None)
    parser.add_argument("--warmup", type=float, default=1.5)
    parser.add_argument("--max-frames", type=int, default=0)
    parser.add_argument("--no-show", action="store_true")
    parser.add_argument("--out-dir", default="out/webcam_torch")
    args = parser.parse_args(argv)

    import cv2
    import torch
    import torchvision
    from PIL import Image
    from torchvision import transforms
    from torchvision.models import detection

    resolved = MODEL_ALIASES.get(args.model, args.model)
    if not hasattr(detection, resolved):
        available = sorted(n for n in dir(detection) if n[0].islower() and not n.startswith("_"))
        print(f"[錯誤] torchvision 沒有 {args.model!r}（解析為 {resolved!r}）", file=sys.stderr)
        print("        可用的模型：", ", ".join(available), file=sys.stderr)
        return 2

    kwargs = {"weights": "DEFAULT"}
    if args.min_size is not None:
        kwargs["min_size"] = args.min_size
    if args.max_size is not None:
        kwargs["max_size"] = args.max_size
    print(f"PyTorch {torch.__version__} / torchvision {torchvision.__version__}")
    print(f"模型: {resolved}" + (f" (min_size={args.min_size})" if args.min_size else ""))
    model = getattr(detection, resolved)(**kwargs)
    model.eval()
    categories = categories_for(resolved, model)
    transform = transforms.ToTensor()

    # [補完] Colab／伺服器沒有 webcam：--video 用影片檔取代攝影機，其餘流程完全一樣
    if args.video:
        cap = cv2.VideoCapture(args.video)
        if not cap.isOpened():
            print(f"[錯誤] 開不起影片: {args.video}", file=sys.stderr)
            return 2
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        print(f"來源: 影片 {args.video}（{n} 幀）")
        args.warmup = 0.0
    else:
        cap = pick_camera(args.camera)
        if cap is None:
            print("[錯誤] 找不到有畫面的攝影機（先跑 00_check_env.py；"
                  "沒有 webcam 的環境請用 --video 影片檔）", file=sys.stderr)
            return 2

    show_gui = (not args.no_show) and imshow_available()
    if not show_gui:
        os.makedirs(args.out_dir, exist_ok=True)
        print(f"[提醒] 沒有 GUI backend，改成存圖到 {args.out_dir}/")

    # [原文] 坑三：暖機（用時間，不用固定幀數）
    t0 = time.time()
    while time.time() - t0 < args.warmup:
        cap.read()

    processed = 0
    saved = 0
    fps = 0.0
    count = 0
    last = time.time()
    t_start = time.time()
    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                if args.video:
                    print("影片播完")          # 影片 EOF 不是錯誤
                else:
                    print("[錯誤] 讀不到 frame", file=sys.stderr)
                break
            processed += 1

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # [原文] PIL → ToTensor → 加 batch 維度
            tensor = transform(Image.fromarray(rgb)).unsqueeze(0)

            with torch.no_grad():
                prediction = model(tensor)[0]

            # [原文] 已依分數降序，可以直接 break
            for box, score, label in zip(prediction["boxes"].numpy(),
                                         prediction["scores"].numpy(),
                                         prediction["labels"].numpy()):
                if score < args.threshold:
                    break
                x0, y0, x1, y1 = [int(v) for v in box]
                cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 255, 0), 2)
                name = (categories[int(label)] if 0 <= int(label) < len(categories)
                        else f"class_{int(label)}")
                cv2.putText(frame, f"{name} {score:.2f}", (x0, max(y0 - 6, 12)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

            count += 1
            now = time.time()
            if now - last >= 0.5:
                fps = count / (now - last)
                count, last = 0, now
            cv2.putText(frame, f"{fps:5.1f} FPS", (10, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

            if show_gui:
                cv2.imshow("PyTorch Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                cv2.imwrite(os.path.join(args.out_dir, f"frame_{saved:04d}.jpg"), frame)
                saved += 1

            if args.max_frames and processed >= args.max_frames:
                break
    finally:
        cap.release()
        if show_gui:
            cv2.destroyAllWindows()

    if not show_gui:
        print(f"已存 {saved} 張到 {args.out_dir}/")
    # 影片很短或 --max-frames 很小時，0.5 秒的取樣窗可能還沒關過，退回平均值
    if fps <= 0 and processed:
        fps = processed / max(time.time() - t_start, 1e-6)
    print(f"平均速度: {fps:.1f} FPS（{processed} 幀）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

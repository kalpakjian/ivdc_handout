#!/usr/bin/env python3
"""bench/bench_detection.py — 同一段畫面的偵測模型基準線。

為什麼要有這支：把「FPS」放在一起比很危險，除非<strong>同一張影格、同一個門檻、同一台機器</strong>。
這支就是筆記 §六 那張表的來源——它對每張圖跑同樣的模型、量純推論時間、
順便印出「最高信心」與「≥門檻有幾個」，所以「快但什麼都沒看到」會直接現形。

用法:
    python bench/bench_detection.py --frame frame.jpg
    python bench/bench_detection.py --camera 0 --repeat 5      # 現場抓一張再跑
    python bench/bench_detection.py --frame frame.jpg --yolo    # 加測 YOLOv8n（需 ultralytics）
    python bench/bench_detection.py --frame frame.jpg --json out.json

輸出：一張 Markdown 表 + （可選）JSON。時間是「模型 forward 的平均值」，
不含攝影機讀取與畫框，所以會比 04_torch_webcam_detection.py 顯示的 FPS 高。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

CASES = [
    ("fasterrcnn_resnet50_fpn", {}),
    ("fasterrcnn_resnet50_fpn", {"min_size": 400, "max_size": 667}),
    ("fasterrcnn_mobilenet_v3_large_fpn", {}),
    ("fasterrcnn_mobilenet_v3_large_320_fpn", {}),
    ("ssdlite320_mobilenet_v3_large", {}),
]


def grab_frame(camera: int) -> str:
    """抓一張實機影格存檔，回傳路徑（沿用 04 的 pick_camera）。"""
    import cv2

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/src")
    from importlib import import_module

    pick = import_module("04_torch_webcam_detection").pick_camera
    cap = pick(camera)
    if cap is None:
        print("[錯誤] 找不到有畫面的攝影機（先跑 src/00_check_env.py）", file=sys.stderr)
        raise SystemExit(2)
    try:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        for _ in range(10):
            cap.read()
        ok, frame = cap.read()
    finally:
        cap.release()
    if not ok or frame is None:
        print("[錯誤] 讀不到 frame", file=sys.stderr)
        raise SystemExit(2)
    path = os.path.abspath("bench_frame.jpg")
    cv2.imwrite(path, frame)
    print(f"captured {path} ({frame.shape[1]}x{frame.shape[0]}, brightness {frame.mean():.0f})")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="同一段畫面的偵測模型基準線")
    parser.add_argument("--frame", help="影格路徑；沒給就用 --camera 現場抓")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--repeat", type=int, default=5, help="每個模型計時幾次（預設 5）")
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--yolo", action="store_true", help="加測 YOLOv8n 640/960/1280")
    parser.add_argument("--json", dest="json_out", default="")
    args = parser.parse_args(argv)

    import cv2
    import torch
    from torchvision.models import detection
    from importlib import import_module

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/src")
    # 類別名稱沿用 03 的邏輯：SSD 家族沒有 .weights，要從 WeightsEnum 拿
    cats_helper = import_module("03_torch_object_detection_image")

    path = args.frame or grab_frame(args.camera)
    bgr = cv2.imread(path)
    if bgr is None:
        print(f"[錯誤] 讀不到圖片: {path}", file=sys.stderr)
        return 2
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    tensor = torch.from_numpy(rgb).permute(2, 0, 1).float().div(255.0).unsqueeze(0)
    print(f"frame: {rgb.shape[1]}x{rgb.shape[0]}, threshold={args.threshold}, "
          f"repeat={args.repeat}\n")

    rows = []
    for fn, kwargs in CASES:
        label = fn + (" + min_size=400" if kwargs.get("min_size") == 400 else "")
        try:
            model = getattr(detection, fn)(weights="DEFAULT", **kwargs)
            model.eval()
            with torch.no_grad():
                for _ in range(args.warmup):
                    model(tensor)
                t0 = time.time()
                for _ in range(args.repeat):
                    pred = model(tensor)[0]
                dt = (time.time() - t0) / args.repeat
        except Exception as exc:
            print(f"| {label} | — | — | — | — | FAILED {type(exc).__name__} |")
            continue

        scores = pred["scores"].numpy()
        labels = pred["labels"].numpy()
        cats = cats_helper.categories_for(fn, model)
        keep = scores >= args.threshold
        names = sorted({cats[int(l)] for l in labels[keep]}) if cats else []
        rows.append({"model": label, "ms": round(dt * 1000, 1), "fps": round(1 / dt, 1),
                     "max_score": round(float(scores.max()), 3),
                     "n": int(keep.sum()), "labels": names})
        print(f"| `{label}` | {dt*1000:.0f} ms | {1/dt:.1f} FPS | "
              f"{scores.max():.3f} | {int(keep.sum())} | "
              f"{'、'.join('`' + n + '`' for n in names) or '—'} |")
        del model

    if args.yolo:
        from ultralytics import YOLO

        model = YOLO("yolov8n.pt")
        for imgsz in (640, 960, 1280):
            r = model.predict(source=rgb, imgsz=imgsz, conf=0.25, verbose=False)[0]
            ms = float(r.speed["inference"])
            confs = r.boxes.conf.cpu().numpy() if r.boxes is not None and len(r.boxes) else []
            names = sorted({r.names[int(c)] for c in r.boxes.cls}) if len(confs) else []
            keep = int((confs >= args.threshold).sum()) if len(confs) else 0
            top = float(max(confs)) if len(confs) else 0.0
            rows.append({"model": f"yolov8n imgsz={imgsz}", "ms": round(ms, 1),
                         "fps": round(1000 / ms, 1), "max_score": round(top, 3),
                         "n": keep, "labels": names})
            print(f"| `yolov8n imgsz={imgsz}` | {ms:.0f} ms | {1000/ms:.1f} FPS | {top:.3f} | "
                  f"{keep} | {'、'.join('`' + n + '`' for n in names) or '—'} |")

    if args.json_out:
        json.dump(rows, open(args.json_out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"\n已存 {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""05_yolo_detection.py — YOLOv8 偵測（簡報標「Recommended」的四行方案）。

用法:
    python 05_yolo_detection.py --source bus.jpg            # 單張圖
    python 05_yolo_detection.py --source 0 --show           # webcam 即時
    python 05_yolo_detection.py --source 0 --no-show --max-frames 30
    python 05_yolo_detection.py --source bus.jpg --imgsz 1280   # 小目標更完整，但更慢

為什麼預設是 yolov8n
    nano 版在 CPU 上才跑得動即時；換 yolov8s/m 精度更好但速度掉一個檔次。
    `--imgsz` 是速度/精度最直接的旋鈕：640 → 960 → 1280 速度約 37 / 19 / 11 FPS。

標註慣例
    # [原文]  簡報截圖上讀得到的程式碼
    # [補完]  截圖被滾動箭頭遮住／講義省略，依框架標準介面補完
"""

from __future__ import annotations

import argparse
import os
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="YOLOv8 偵測（單張圖或 webcam）")
    parser.add_argument("--source", default="0",
                        help="圖片/影片路徑，或 webcam index（例如 0）")
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--show", action="store_true", help="彈窗顯示（需要 GUI）")
    parser.add_argument("--no-show", action="store_true", help="不彈窗（headless 機器）")
    parser.add_argument("--max-frames", type=int, default=0, help="0=不限（webcam 測試用）")
    parser.add_argument("--out-dir", default="out/yolo")
    args = parser.parse_args(argv)

    from ultralytics import YOLO

    # [原文] 簡報的四行：載入 model、predict(source=0, show=True)
    model = YOLO(args.model)

    source: object = args.source
    if args.source.isdigit():
        source = int(args.source)

    show = args.show and not args.no_show
    os.makedirs(args.out_dir, exist_ok=True)

    print(f"model={args.model} source={source} imgsz={args.imgsz} conf={args.conf}")
    frames = 0

    # [原文] model.predict(source=0, show=True) —— 加上實用參數
    results = model.predict(
        source=source,
        imgsz=args.imgsz,
        conf=args.conf,
        stream=True,   # [補完] 一律 stream：webcam/長影片才不會把結果累積在記憶體
        show=show,
        verbose=False,
    )

    for result in results:
        frames += 1
        names = result.names
        boxes = result.boxes
        n = 0 if boxes is None else len(boxes)
        top = 0.0 if n == 0 else float(boxes.conf.max())

        # [補完] 速度要用 ultralytics 自己的 result.speed，不要用「總時間 / 張數」：
        #        那樣會把模型載入與第一次 warmup 算進去（單張圖會量到 2 FPS 這種假數字）
        infer_ms = float((getattr(result, "speed", {}) or {}).get("inference", 0.0))
        fps = 1000.0 / infer_ms if infer_ms > 0 else 0.0
        print(f"frame {frames:04d}: {n} 個物件, 最高信心 {top:.2f}, "
              f"推論 {infer_ms:.1f} ms ({fps:.1f} FPS)")

        if show:
            continue
        path = os.path.join(args.out_dir, f"pred_{frames - 1:04d}.jpg")
        result.save(filename=path)  # [補完] headless 時存檔，不然什麼都看不到

        if args.max_frames and frames >= args.max_frames:
            break

    if not show:
        print(f"\n已存 {frames} 張到 {args.out_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

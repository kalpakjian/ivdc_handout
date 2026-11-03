#!/usr/bin/env python3
"""03_torch_object_detection_image.py — torchvision Faster R-CNN 單張圖偵測。

用法:
    python 03_torch_object_detection_image.py --image bus.jpg
    python 03_torch_object_detection_image.py --image bus.jpg --model fasterrcnn_mobilenet_320
    python 03_torch_object_detection_image.py --image bus.jpg --min-size 400   # CPU 加速關鍵

模型名稱（重要）
    筆記 §六 的表格用了 `fasterrcnn_resnet50` / `fasterrcnn_mobilenet` 這種簡寫，
    但 torchvision 裡真正的函式名只有：
        fasterrcnn_resnet50_fpn, fasterrcnn_resnet50_fpn_v2,
        fasterrcnn_mobilenet_v3_large_fpn, fasterrcnn_mobilenet_v3_large_320_fpn,
        ssdlite320_mobilenet_v3_large, retinanet_resnet50_fpn(_v2),
        fcos_resnet50_fpn, ssd300_vgg16
    直接 getattr 簡寫會 AttributeError，所以這裡有一張別名表。

標註慣例
    # [原文]  簡報截圖上讀得到的程式碼
    # [補完]  截圖被滾動箭頭遮住／講義省略，依框架標準介面補完
"""

from __future__ import annotations

import argparse
import os
import sys

# [補完] 簡寫 → torchvision 真實函式名（筆記表格的簡寫照抄會炸，這裡補起來）
MODEL_ALIASES = {
    "fasterrcnn_resnet50": "fasterrcnn_resnet50_fpn",
    "fasterrcnn_resnet50_v2": "fasterrcnn_resnet50_fpn_v2",
    "fasterrcnn_mobilenet": "fasterrcnn_mobilenet_v3_large_fpn",
    "fasterrcnn_mobilenet_320": "fasterrcnn_mobilenet_v3_large_320_fpn",
    "ssdlite320": "ssdlite320_mobilenet_v3_large",
    "retinanet": "retinanet_resnet50_fpn_v2",
}

# [補完] SSD/SSDLite 的 model 物件沒有 .weights 屬性（實測 AttributeError），
#        要靠 WeightsEnum 才拿得到類別名稱，所以備一張 模型 → WeightsEnum 的表。
WEIGHTS_ENUM = {
    "fasterrcnn_resnet50_fpn": "FasterRCNN_ResNet50_FPN_Weights",
    "fasterrcnn_resnet50_fpn_v2": "FasterRCNN_ResNet50_FPN_V2_Weights",
    "fasterrcnn_mobilenet_v3_large_fpn": "FasterRCNN_MobileNet_V3_Large_FPN_Weights",
    "fasterrcnn_mobilenet_v3_large_320_fpn": "FasterRCNN_MobileNet_V3_Large_320_FPN_Weights",
    "ssdlite320_mobilenet_v3_large": "SSDLite320_MobileNet_V3_Large_Weights",
    "ssd300_vgg16": "SSD300_VGG16_Weights",
    "retinanet_resnet50_fpn": "RetinaNet_ResNet50_FPN_Weights",
    "retinanet_resnet50_fpn_v2": "RetinaNet_ResNet50_FPN_V2_Weights",
    "fcos_resnet50_fpn": "FCOS_ResNet50_FPN_Weights",
}


def categories_for(resolved: str, model) -> list[str]:
    """COCO 類別名稱清單（取不到就回空 list，呼叫端退回印 class id）。"""
    weights = getattr(model, "weights", None)
    if weights is not None:
        return list(weights.meta["categories"])
    enum = WEIGHTS_ENUM.get(resolved)
    if enum:
        try:
            from torchvision.models import get_weight

            return list(get_weight(f"{enum}.DEFAULT").meta["categories"])
        except Exception:
            pass
    return []


def build_model(name: str, min_size: int | None, max_size: int | None):
    """依名稱建模型；回傳 (model, 解析後的函式名, 類別名稱清單)。"""
    import torchvision
    from torchvision.models import detection

    resolved = MODEL_ALIASES.get(name, name)
    if not hasattr(detection, resolved):
        available = sorted(n for n in dir(detection)
                           if n[0].islower() and not n.startswith("_"))
        print(f"[錯誤] torchvision 沒有 {name!r}（解析為 {resolved!r}）", file=sys.stderr)
        print("        可用的模型：", ", ".join(available), file=sys.stderr)
        return None, resolved, []

    # [原文] 這一行是簡報的重點
    factory = getattr(detection, resolved)
    kwargs = {"weights": "DEFAULT"}
    # [補完] CPU 加速：預設 min_size=800 會把 720p 短邊放大到 800，這步吃掉大半時間
    if min_size is not None:
        kwargs["min_size"] = min_size
    if max_size is not None:
        kwargs["max_size"] = max_size
    model = factory(**kwargs)
    # [原文] 一定要呼叫：train 模式回傳的是 loss，不是預測框
    model.eval()
    return model, resolved, categories_for(resolved, model)


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="torchvision 偵測模型單張圖")
    parser.add_argument("--image", required=True)
    parser.add_argument("--model", default="fasterrcnn_resnet50_fpn",
                        help="模型名或別名（預設簡報用的 fasterrcnn_resnet50_fpn）")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--min-size", type=int, default=None,
                        help="覆寫 min_size（CPU 上調小可大幅加速，例如 400）")
    parser.add_argument("--max-size", type=int, default=None)
    parser.add_argument("--out", default="out/torch_detection.jpg")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args(argv)

    import cv2
    import torch
    import torchvision
    from PIL import Image
    from torchvision import transforms

    print(f"PyTorch {torch.__version__} / torchvision {torchvision.__version__}")
    model, resolved, categories = build_model(args.model, args.min_size, args.max_size)
    if model is None:
        return 2
    print(f"模型: {resolved}")

    image = Image.open(args.image).convert("RGB")
    # [原文] ToTensor() 會轉成 (3,H,W) 且縮放到 0～1，正是 torchvision 偵測模型要的範圍
    transform = transforms.ToTensor()
    tensor = transform(image).unsqueeze(0)  # (1, 3, H, W)

    # [補完] 簡報截圖到此為止，以下依 torchvision 標準介面補完
    with torch.no_grad():
        prediction = model(tensor)[0]

    boxes = prediction["boxes"].numpy()    # 絕對像素座標，不是歸一化
    scores = prediction["scores"].numpy()  # 已依分數降序
    labels = prediction["labels"].numpy()

    frame = cv2.cvtColor(cv2.imread(args.image), cv2.COLOR_BGR2RGB)
    kept = 0
    print(f"\n檢出（門檻 {args.threshold}）:")
    for box, score, label in zip(boxes, scores, labels):
        if score < args.threshold:
            break  # [原文] 已依分數降序，可以直接 break
        x0, y0, x1, y1 = [int(v) for v in box]
        name = categories[int(label)] if 0 <= int(label) < len(categories) else f"class_{int(label)}"
        print(f"  {name:16s} score={score:.3f} box=({x0}, {y0}, {x1}, {y1}) 絕對像素")
        cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 255, 0), 2)
        cv2.putText(frame, f"{name} {score:.2f}", (x0, max(y0 - 6, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        kept += 1
    print(f"共 {kept} 個")

    annotated = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    cv2.imwrite(args.out, annotated)
    print(f"已存檔: {args.out}")

    if args.show:
        if not imshow_available():
            print("[提醒] 沒有 GUI backend，只輸出檔案")
            return 0
        cv2.imshow("PyTorch Detection", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

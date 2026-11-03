#!/usr/bin/env python3
"""00_check_env.py — 相機 + 顯示環境自檢 (pre-exam environment check)。

IVDC Lesson 8「物件偵測與 CNN」講義還原腳本。每換一台機器（尤其是考試機）先跑這支。

用法:
    python 00_check_env.py
    python 00_check_env.py --strict          # 缺 GUI / 相機就回傳非 0
    python 00_check_env.py --skip-camera     # 考試機沒相機時

檢查四件事:
    1. 套件版本（缺哪個、怎麼裝）
    2. 有沒有 GUI backend —— 注意 hasattr(cv2, "imshow") 會騙人，
       一定要「真的呼叫一次」才算數
    3. 攝影機：不是 index 0 就是對的，要逐個開、量畫面亮度
    4. 前幾幀能不能用（自動曝光）

標註慣例
    # [原文]  簡報截圖上讀得到的程式碼
    # [補完]  截圖被滾動箭頭遮住／講義省略，依框架標準介面補完
"""

from __future__ import annotations

import argparse
import importlib
import platform
import sys

# [原文] 簡報自檢清單：缺哪個、就印出對應的 pip install
PACKAGES = [
    ("cv2", "opencv-python"),
    ("torch", "torch"),
    ("torchvision", "torchvision"),
    ("tensorflow", "tensorflow"),
    ("tensorflow_hub", "tensorflow-hub"),
    ("ultralytics", "ultralytics"),
    ("numpy", "numpy"),
    ("matplotlib", "matplotlib"),
]


def report_packages() -> dict[str, str]:
    """回傳 {module: version}，順便印出人看的表格。"""
    found: dict[str, str] = {}
    print("== 套件 ==")
    for module, package in PACKAGES:
        try:
            mod = importlib.import_module(module)
            version = getattr(mod, "__version__", "?")
            found[module] = version
            print(f"  OK      {module:16s} {version}")
        except Exception:
            print(f"  MISSING {module:16s} -> pip install {package}")
    print(f"  --      python           {platform.python_version()} ({sys.executable})")
    return found


def imshow_available() -> bool:
    """真的彈一次視窗才算數。"""
    # [原文] 這段是「坑四」的解法：不能只判斷函式存在
    import cv2
    import numpy as np

    try:
        cv2.imshow("__probe__", np.zeros((4, 4, 3), np.uint8))
        cv2.waitKey(1)
        cv2.destroyWindow("__probe__")
        return True
    except Exception:
        return False


def report_gui() -> bool:
    print("\n== 顯示 (GUI) ==")
    try:
        import cv2
    except Exception:
        print("  MISSING cv2 -> 無法檢查 GUI")
        return False

    # [原文] currentUIFramework() 回空字串 = 沒有 GUI backend
    try:
        framework = cv2.currentUIFramework()
    except Exception:
        framework = "(這個版本沒有 currentUIFramework())"
    print(f"  UI 框架: {framework or '(空 = 無)'}")

    ok = imshow_available()
    print("  OK      可以正常彈窗" if ok else "  失敗    imshow 不可用（headless 版 OpenCV）")
    if not ok:
        print("  修法:    pip uninstall opencv-python-headless -y && pip install opencv-python")
    return ok


def _backend() -> int:
    """Windows 上用 DirectShow；其他平台交給 OpenCV 自己挑。"""
    # [補完] 簡報只講 Windows（CAP_DSHOW）。原樣搬到 Linux 會每個 index 都開不起來，
    #        所以在這裡依平台選擇後端。
    import cv2

    return cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY


def camera_backends() -> list[int]:
    """要依序嘗試的後端清單。"""
    import cv2

    # [原文] 坑二：Windows 上 CAP_MSMF 常常打不開，要依序重試
    if sys.platform == "win32":
        return [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    return [cv2.CAP_ANY]


def pick_camera(preferred: int = 0, max_index: int = 6, min_brightness: float = 20.0):
    """回傳第一個「真的有畫面」的攝影機（已開好、已暖機）。

    [原文] 坑一：cv2.VideoCapture(0) 可能成功開啟卻是全黑，不會報錯。
    [補完] 暖機改成「時間」而不是固定幀數：自動曝光要 1～2 秒，
           只丟 10 幀（約 0.3 秒）根本不夠。
    """
    import cv2
    import time

    order = [preferred] + [i for i in range(max_index + 1) if i != preferred]
    for idx in order:
        for api in camera_backends():
            cap = cv2.VideoCapture(idx, api)
            if not cap.isOpened():
                cap.release()
                continue
            mean = -1.0
            t0 = time.time()
            while time.time() - t0 < 1.0:  # 等自動曝光穩定
                ok, frame = cap.read()
                if ok and frame is not None:
                    mean = float(frame.mean())
            if mean >= min_brightness:
                print(f"  OK      camera {idx} (backend {api}, brightness {mean:.0f})")
                return cap
            cap.release()
            print(f"           camera {idx} (backend {api}): black (mean {mean:.1f}) - skip")
    return None


def list_cameras(max_index: int = 6) -> bool:
    print("\n== 攝影機 ==")
    cap = pick_camera(0, max_index)
    if cap is None:
        print("  失敗    找不到有畫面的攝影機")
        print("  修法:    換 index、檢查裝置管理員，或直接跳過這項 (--skip-camera)")
        return False
    cap.release()
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="IVDC Lesson 8 環境自檢")
    parser.add_argument("--skip-camera", action="store_true", help="不檢查攝影機")
    parser.add_argument("--max-camera-index", type=int, default=6, help="最多試到第幾個 index")
    parser.add_argument("--strict", action="store_true", help="GUI/相機不可用時回傳非 0")
    args = parser.parse_args(argv)

    print(f"== 平台 ==\n  {platform.platform()}\n")
    found = report_packages()
    gui_ok = report_gui()
    cam_ok = True if args.skip_camera else list_cameras(args.max_camera_index)

    print("\n== 結論 ==")
    model_paths = [name for name in ("torch", "tensorflow", "ultralytics") if name in found]
    print(f"  可用推論框架: {', '.join(model_paths) if model_paths else '（無）'}")
    print(f"  GUI: {'可以用 imshow' if gui_ok else '沒有，請走存檔模式'}")
    if args.skip_camera:
        cam_text = "未檢查（--skip-camera）"
    else:
        cam_text = "可用" if cam_ok else "不可用（請改用 --video 影片檔）"
    print(f"  相機: {cam_text}")

    if args.strict and not (gui_ok and cam_ok):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

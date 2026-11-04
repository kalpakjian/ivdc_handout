# 考试现场清单 — IVDC 电脑视觉（Object Detection & CNN）

> 已用 **Logitech Brio 300** 实机验证。下面的每个数字都是本机实测，
> 不是理论值。合计发现 **4 个会导致当场翻车的问题**，全部已修复并验证。

---

## 0. 先跑自检（30 秒，务必先做）

```powershell
cd C:\Users\princ\ivdc_handout\src
python 00_check_env.py
```

当前本机输出（已修好的状态）：

```
[1] 套件    cv2 5.0.0 / numpy 2.5.4 / torch 2.14.1 / torchvision 0.29.1  ✅
            tensorflow ❌  ultralytics ❌
[2] imshow  UI 框架: WIN32  ->  OK 可以正常弹窗  ✅
[3] 摄像头  OK  DirectShow  打开成功, 1280x720   ✅
```

---

## 1. 四个已修复的坑

### 坑 ①（最致命）摄像头索引不固定，**不要写死 index**

实测枚举本机摄像头（**2026-11-04 复查**）：

| 索引 | 画面亮度 | 实际情况 |
|---|---|---|
| **camera 0** | **121~123** | ✅ **Brio 300 真身**（本次） |
| **camera 1** | 1.4 | ❌ 黑屏（虚拟设备） |
| **camera 2** | 2.5 | ❌ 黑屏 |
| **camera 3** | 打不开 | — 不存在 |

> ⚠️ **索引会随 USB 插拔／开机顺序改变。** 早期这份笔记记录的是
> 「camera 2 才是 Brio、camera 0 是黑屏」，今天实测**完全相反**：
> Brio 跑到了 camera 0，camera 2 反而变成黑屏。
> 所以**任何写死 `--camera 2` 的命令都不可靠**，包括本文档旧版里的示例。

`VideoCapture(0)` **会成功打开**，但可能流出纯黑假画面 —— 不报错、不崩溃，
你只会看到"检测不到任何东西"，然后怀疑自己代码写错了。

**修复**：`pick_camera()` 自动遍历 0~6，逐一看画面亮度，
自动跳过黑屏的那个，选中真正有画面的。日志会打印：

```
camera 0: opened but frame is black (mean 1.4) - skipping
camera 1: opened but frame is black (mean 2.5) - skipping
using camera 0 (mean brightness 123)
```

**考试机上的索引一定不同，这个自动探测就是保险。直接跑脚本，不要手动指定索引。**

**自己确认当前索引**（不确定时先跑这个）：

```powershell
.\.venv-yolo\Scripts\python.exe -c "import cv2; [print(f'camera {i}: opened={c.isOpened()}') or c.release() for i in range(4) for c in [cv2.VideoCapture(i, cv2.CAP_DSHOW)]]"
```

### 坑 ②headless opencv 让 `cv2.imshow()` 直接抛异常（已修好）

原来是 `opencv-python-headless`，`imshow` 报：

```
error: (-2:Unspecified error) The function is not implemented.
```

**已卸载 headless、改装带 GUI 的 `opencv-python 5.0.0.93`**，
现在 `UI 框架: WIN32`，窗口正常。脚本同时保留自动降级逻辑：
万一考试机还是 headless 版，也不会崩，会转为存档模式。

### 坑 ③幻灯片用的 resnet50 在 CPU 上只有 1 FPS

`fasterrcnn_resnet50_fpn` 实测 **1.1 FPS**，演示会卡成幻灯片。
但 Brio 300 本身跑满 **30 FPS**（实测 30.4），瓶颈在模型。

**实测各模型（1280x720 真实画面，CPU）**：

| 模型 | 速度 | 最高置信度 | 检出 | 评价 |
|---|---|---|---|---|
| `fasterrcnn_resnet50`（幻灯片原版） | 1.1 FPS | 0.830 | 4 个 | 最准但太慢 |
| **`fasterrcnn_mobilenet`（新默认）** | **5.4 FPS** | **0.938** | **1 个** | **平衡点** |
| `fasterrcnn_mobilenet_320` | 24.6 FPS | 0.194 | **0 个** | ⚠️ 快但漏检 |
| `ssdlite320` | 19.5 FPS | 0.355 | 1 个（误检） | 轻量 |

⚠️ **注意：最快的那个反而检测不到东西**。320px 输入分辨率太低。
所以默认值设在 `fasterrcnn_mobilenet`（5.4 FPS），不是最快的那个。

### 坑 ④摄像头刚开的 1~2 秒过曝/黑屏

自动曝光没稳定前检测出的是噪声。脚本内置 `--warmup`（默认 10 帧）自动丢弃。

---

## 2. 考试命令速查

```powershell
cd C:\Users\princ\ivdc_handout\src
python 00_check_env.py                        # ① 永远先跑这个

# ---- 目标检测 A：PyTorch Faster R-CNN（主 .venv，已验证）----
python 04_torch_webcam_detection.py                              # 默认 5.4 FPS
python 04_torch_webcam_detection.py --model fasterrcnn_resnet50   # 最准但 1 FPS
python 04_torch_webcam_detection.py --threshold 0.35 --save       # 降阈值+录像
python 04_torch_webcam_detection.py --max-frames 100              # 跑完自动停
python 04_torch_webcam_detection.py                              # 自动挑相机（推荐）

# ---- 目标检测 B：YOLOv8n（独立 venv，最快 37 FPS，已验证）----
..\.venv-yolo\Scripts\python.exe 05_yolo_detection.py --source 0
..\.venv-yolo\Scripts\python.exe 05_yolo_detection.py --source 0 --imgsz 1280
..\.venv-yolo\Scripts\python.exe 05_yolo_detection.py --source photo.jpg
..\.venv-yolo\Scripts\python.exe 05_yolo_detection.py --source backup_clip.mp4

# ---- 单张图片 ----
python 03_torch_object_detection_image.py --image photo.jpg

# ---- CNN 分类 ----
python 07_torch_cnn_mnist.py     # 实测 99.09%
```

---

## 3. 演示注意事项（重要）

- **拿真实物体**：杯子、瓶子、手机、键盘、洗衣机。实测 Brio 300 对着房间
  能检出 `oven 0.938`；但对着纯色/手写数字基本检不出，那是模型局限不是代码错。
- **光线要够**：本机整体偏暗，阈值用 `--threshold 0.35`（默认 0.5 偏严）。
- **FPS 显示会从 1.8 爬到 4.6**，因为启动阶段包含 warmup，属正常。
- 如果老师问"为什么不是实时"：直接说明 CPU 上 resnet50 只有 1 FPS，
  换成 mobilenet backbone 提升到 5.4 FPS，并指出第 4/7 页本来就推荐更快的模型 —— **这是加分回答**。

---

## 4. 开考前检查

- [ ] `python 00_check_env.py` → 三项全绿（套件/imshow/摄像头）
- [ ] `yolov8n.pt` 提前下载放同目录（若要用 YOLO）
- [ ] 手机里存几张真实物体照片（`--image` 兜底）
- [ ] 录一段 10 秒 mp4（`--video` 兜底，摄像头万一被占用）
- [ ] 关掉 Teams / Zoom / 微信 —— 它们会独占摄像头
- [ ] TensorFlow 未装：若考试要 TF 版需 `pip install tensorflow`（Python 3.15 支持存疑，**建议直接用 PyTorch 版**）

---

## 5. 现场排错

| 现象 | 原因 | 处理 |
|---|---|---|
| 画面全黑但没报错 | 选到了虚拟摄像头 | 已自动跳过；别手写 `--camera N`，让脚本自己挑 |
| `objects 0` 但画面正常 | 阈值太高/物体不在 COCO 80 类 | `--threshold 0.3`，换真实物体 |
| `The function is not implemented` | headless opencv | 已修；或加 `--save` 不弹窗 |
| 一直 1 FPS | resnet50 太重 | 用默认 mobilenet，或 YOLO |
| `cannot open video source` | 被别的程序占用 | 关掉 Teams/微信 |
| `ModuleNotFoundError: tensorflow` | 没装 TF | `pip install tensorflow` |

---

## 6. 实测基准（可直接写进报告）

| 项目 | 结果 |
|---|---|
| 摄像头型号 | Logitech Brio 300 @ 2026-11-04 实测为 **index 0**（会变，勿写死）, 1280x720, 30 FPS |
| 分辨率上限 | 1280x720（请求 1080p/4K 均被拒） |
| PyTorch CNN (MNIST, 5 epoch) | **99.09%**，loss 0.1847 → 0.0218 |
| resnet50 检测 | 1.1 FPS，4 个目标（carrot 0.830 / truck 0.640） |
| mobilenet 检测 | **5.4 FPS，oven 0.938** ✅ |
| mobilenet_320 检测 | 24.6 FPS 但 **0 检出** |

### YOLOv8n 实测（独立 venv，ultralytics 8.4.200 / torch 2.15.0）

| imgsz | 速度（CPU） | 准确度 |
|---|---|---|
| 640 | **37.4 FPS** | bus.jpg: `bus 0.87` + `person 0.87/0.85/0.83`（4 个，全对） |
| 960 | 18.8 FPS | 中间档 |
| 1280 | 11.1 FPS | 同一张图 **7 个**检出，小目标更全面 |

**结论：YOLO 比 Faster R-CNN 快 7 倍（37 vs 5.4 FPS），而且要演示实时效果就用它。**
第 7 页幻灯片标注的 "Yolo (Recommended)" 是对的。

⚠️ 注意 `imgsz` 的影响：640 速度最快但小目标容易漏；1280 慢 3 倍但准确度明显提升。
演示时用 640 保证流畅，要看清小物体时加 `--imgsz 1280`。

---

## 7. 已备好的兜底素材

| 文件 | 用途 |
|---|---|
| `backup_clip.mp4` | 10 秒 1280x720 录像（54 帧），摄像头被占用时 `--source backup_clip.mp4` |
| `yolov8n.pt` | YOLO 权重已下载到本地，**考场断网也能用** |

Faster R-CNN 权重也已缓存到 `C:\Users\princ\.cache\torch\hub\checkpoints`，
断网同样可用。

---

## 8. 两个 venv 的分工（重要，别搞混）

| 环境 | Python | 能跑 | 不能跑 |
|---|---|---|---|
| **主环境**（系统 Python 3.15） | `python` | `00`~`04`、`06`/`07` | `05_yolo`（无 ultralytics） |
| **`.venv-yolo`**（独立） | `..\.venv-yolo\Scripts\python.exe` | `05_yolo` ✅ | 也可用 00/04（它有 torch+opencv） |

- 主环境：opencv **5.0.0（带 GUI，WIN32）**、torch 2.14.1、numpy 2.5.4
- `.venv-yolo`：ultralytics 8.4.200、torch 2.15.0、opencv 5.0.0（带 GUI）、numpy 2.5.4

两边都验证过 `cv2.imshow` 可弹窗、能打开摄像头（索引会变，脚本自动挑）。
**如果嫌切换麻烦，考试只用一个：直接全程用 `.venv-yolo` 那个 Python，
它能把 00/04/05/07 全跑起来。**


---

## 0. 动手前先跑自检（30 秒）

```powershell
cd C:\Users\princ\ivdc_handout\src
python 00_check_env.py
```

它会打印四块内容：套件、`cv2.imshow` 是否可用、摄像头是否可用、结论。
**先看这个再写任何代码**，能省掉现场 80% 的排错时间。

---

## 1. 三个已复现的坑（以及脚本里怎么绕过的）

### 坑 A：`cv2.imshow()` 直接抛异常，程序当场崩

本机的 opencv 是 **headless 版**（`opencv-python-headless 5.0.0.93`），
`cv2.currentUIFramework()` 返回空字符串，`imshow` 报：

```
error: (-2:Unspecified error) The function is not implemented.
Rebuild the library with Windows, GTK+ 2.x or Cocoa support.
```

注意：`hasattr(cv2, "imshow")` **返回 True**，所以"检查函数存不存在"是没用的，
必须**真的调用一次**才知道。三个摄像头脚本现在都内置了 `imshow_available()`
探测函数，不可用就自动降级为"不开窗、直接存文件"，绝不崩。

**想真正看到窗口**（考试若要演示实时画面）：

```powershell
pip uninstall opencv-python-headless -y
pip install opencv-python
```

### 坑 B：`VideoCapture(0)` 在 Windows 上未必打得开

必须显式用 **DirectShow**。本机实测：`CAP_ANY` / `CAP_DSHOW` 能开，
`CAP_MSMF` 打不开。脚本现在按 `DirectShow -> MSMF -> 默认` 依次重试。

另外摄像头刚打开会有 **1~2 秒黑屏 / 过曝**（自动曝光没稳定），
直接检测会得到一堆假结果。脚本用 `--warmup 10` 先丢掉前 10 帧。

### 坑 C：CPU 上只有 **约 1 FPS**

本机实测 Faster R-CNN (resnet50-FPN) 单帧推理 **0.8~0.9 秒**。
幻灯片标题叫 "Real Time"，但 CPU 上做不到实时 —— 这点如果老师问起，
**要能主动说明**（这反而是加分的回答）：

| 模型 | 本机 CPU 实测 | 说明 |
|---|---|---|
| Faster R-CNN resnet50 | ~1.1 FPS | 幻灯片第 5/6 页用的就是这个 |
| SSD MobileNet V2 | 快得多 | 幻灯片第 4 页说"初学者首选" |
| YOLOv8n | 最快 | 幻灯片第 7 页标注 "Recommended" |

**如果老师要求真的实时**，改用 `05_yolo_detection.py`（第 7 页推荐方案），
或把 Faster R-CNN 的 backbone 换成 `fasterrcnn_mobilenet_v3_large_fpn`。

---

## 2. 模型在"非真实场景"下的表现（重要，别误判成 bug）

实测发现：Faster R-CNN 对**手写数字、纯色几何图形**的置信度极低（0.1 左右），
因为 COCO 模型只认 80 类真实物体。但它对真实桌面场景有效 ——
本机实测白化的摄像头画面里认出了 `vase 0.824`、`knife 0.779`。

**结论：演示时一定要拿真实物体**（杯子、瓶子、手机、人脸/人），
不要拿一张 MNIST 数字去测目标检测，否则会显示 "0 objects" 而你以为是代码错了。

阈值建议：现场光线不好时用 `--threshold 0.3`，默认 0.5 可能偏严。

---

## 3. 考试命令速查

```powershell
cd C:\Users\princ\ivdc_handout\src

# ---- 先自检 ----
python 00_check_env.py

# ---- 目标检测 ----
python 04_torch_webcam_detection.py                          # PyTorch 摄像头（推荐先跑这个）
python 04_torch_webcam_detection.py --threshold 0.3 --save    # 降阈值 + 录像
python 04_torch_webcam_detection.py --max-frames 100          # 跑 100 帧自动停
python 03_torch_object_detection_image.py --image photo.jpg   # 单张图片

# ---- YOLO（第 7 页"推荐"方案，需先装 ultralytics）----
python 05_yolo_detection.py --source 0 --save
python 05_yolo_detection.py --source photo.jpg

# ---- CNN 分类 ----
python 07_torch_cnn_mnist.py        # 已实测：99.09% 准确率
python 06_tf_cnn_mnist.py           # 需先装 tensorflow
```

**没有摄像头时**（备用演示方案，避免现场卡死）：

```powershell
python 04_torch_webcam_detection.py --video some_clip.mp4
python 05_yolo_detection.py --source some_clip.mp4
```

建议**提前录一段 10 秒的 mp4 放在同目录**，摄像头万一坏了也能演示。

---

## 4. 开考前必须准备好的东西

- [ ] `python 00_check_env.py` 跑通，确认摄像头 + imshow 状态
- [ ] **`yolov8n.pt` 提前下载好**放在脚本同目录（首次运行会自动联网下载，考场可能没网）
- [ ] Faster R-CNN 权重已缓存（本机已缓存于 `C:\Users\princ\.cache\torch\hub\checkpoints`）
- [ ] 手机里存几张真实物体照片（杯子/瓶子/键盘），图片检测可兜底
- [ ] 一段 10 秒 mp4 视频作为摄像头备胎
- [ ] 确认 `python` 在 PATH 里（考试机可能要用 `py` 或完整路径）

### 关于 TensorFlow

本机**没装 TensorFlow**，所以 `01_tf_*.py` / `02_tf_*.py` / `06_tf_cnn_mnist.py`
无法在本机验证运行。如果考试要跑 TensorFlow 版：

```powershell
pip install tensorflow tensorflow-hub
```

⚠️ 注意 TF 目前对 Python 3.15 支持可能不完整。若装不上，
**考试就用 PyTorch 版本**（`03`/`04`/`07` 都已在本机完整验证通过），
CNN 部分两份幻灯片的结构是完全等价的（见 NOTES.md 的架构对照表）。

### 关于 ultralytics

它会依赖 `numpy<2`，可能把你现在的 numpy 2.5.4 降级。
**建议单独建虚拟环境**，别污染已验证好的 torch 环境：

```powershell
python -m venv ..\.venv-yolo
..\.venv-yolo\Scripts\activate
pip install ultralytics
```

---

## 5. 现场排错对照表

| 现象 | 原因 | 处理 |
|---|---|---|
| `The function is not implemented` | headless opencv | 用 `--save`，或装回 `opencv-python` |
| 窗口里一片黑 / 全白过曝 | 摄像头自动曝光没稳定 | 已内置 `--warmup`，或加帧数 |
| `cannot open video source` | 摄像头被别的程序占用 | 关掉微信/Teams/Zoom 再试 |
| `objects 0` 但画面正常 | 阈值太高 / 物体不在 COCO 80 类里 | `--threshold 0.2`，换真实物体 |
| 一直 1 FPS | CPU 跑 resnet50 | 改用 YOLO 或 mobilenet backbone |
| `ModuleNotFoundError: tensorflow` | 没装 TF | `pip install tensorflow` |
| `No module named 'ultralytics'` | 没装 YOLO | `pip install ultralytics` |

---

## 6. 本机实测结果（可写进报告）

| 项目 | 结果 |
|---|---|
| 摄像头 | DirectShow 打开成功，1280x720（2026-11-04 实测 index 0，亮度 123） |
| `cv2.imshow` | **可用**（2026-11-04 实测 WIN32 可弹窗；`opencv-python` 5.0.0，非 headless） |
| PyTorch CNN (MNIST, 5 epoch) | **99.09%** 准确率，loss 0.1847 → 0.0218 |
| Faster R-CNN 单帧推理 | 0.79–0.92 s（约 1 FPS） |
| Faster R-CNN 真实场景识别 | vase 0.824 / knife 0.779 ✅ |
| Faster R-CNN 对 MNIST 数字 | 0.114（不识别，属正常） |

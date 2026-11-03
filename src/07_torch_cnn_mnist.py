#!/usr/bin/env python3
"""07_torch_cnn_mnist.py — PyTorch CNN 數字分類（MNIST）。

同樣五個階段，換 PyTorch 寫：載入資料 → 前處理 → 建模型 → 訓練 → 單張推論。

用法:
    python 07_torch_cnn_mnist.py                # 5 epochs
    python 07_torch_cnn_mnist.py --epochs 1     # 快速煙霧測試
    python 07_torch_cnn_mnist.py --device cuda  # 有 GPU 時

標註慣例
    # [原文]  簡報截圖上讀得到的程式碼
    # [補完]  截圖被滾動箭頭遮住／講義省略，依框架標準介面補完

簡報對應：第 18–25 頁（Or you could use Pytorch）。第 21 頁底部兩行被裁掉、第 19／22 頁被箭頭遮住。
"""

from __future__ import annotations

import argparse
import sys


def build_model():
    """回傳 (model, param_count)。"""
    import torch
    import torch.nn as nn

    # [原文] 建立模型。注意最後一層沒有 softmax：CrossEntropyLoss 內建
    class Net(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Conv2d(1, 32, 3)
            self.pool = nn.MaxPool2d(2, 2)
            self.conv2 = nn.Conv2d(32, 64, 3)
            self.fc1 = nn.Linear(64 * 5 * 5, 128)
            self.fc2 = nn.Linear(128, 10)

        def forward(self, x):
            # 28 → 26 → 13 → 11 → 5，所以特徵圖是 64 × 5 × 5
            x = self.pool(torch.relu(self.conv1(x)))
            x = self.pool(torch.relu(self.conv2(x)))
            x = x.view(-1, 64 * 5 * 5)
            x = torch.relu(self.fc1(x))
            return self.fc2(x)

    model = Net()
    return model, sum(p.numel() for p in model.parameters())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PyTorch MNIST CNN（簡報 §八）")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    parser.add_argument("--data-dir", default="./data")
    parser.add_argument("--out", default="", help="模型權重輸出檔（預設不存）")
    args = parser.parse_args(argv)

    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torchvision
    import torchvision.transforms as transforms

    print(f"PyTorch {torch.__version__} / torchvision {torchvision.__version__}")
    device = torch.device(args.device)
    if args.device == "cuda" and not torch.cuda.is_available():
        print("[提醒] CUDA 不可用，退回 CPU", file=sys.stderr)
        device = torch.device("cpu")

    # [原文] 載入資料：ToTensor() 同時做 (H,W,C)→(C,H,W) 與 /255
    transform = transforms.ToTensor()
    train_dataset = torchvision.datasets.MNIST(
        root=args.data_dir, train=True, download=True, transform=transform)
    test_dataset = torchvision.datasets.MNIST(
        root=args.data_dir, train=False, download=True, transform=transform)

    print("Training samples:", len(train_dataset))    # 60000
    print("Test samples:", len(test_dataset))         # 10000
    print("Image shape:", train_dataset[0][0].shape)  # torch.Size([1, 28, 28])

    model, params = build_model()
    model.to(device)
    print(model)
    # [補完] 印參數量：與 TF 版同樣是 225,034，這才是架構等價的證據
    print(f"Param count: {params:,}")

    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=args.batch_size, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=512)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    # [原文] 訓練迴圈五步：zero_grad → forward → loss → backward → step
    for epoch in range(args.epochs):
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        print(f"Epoch {epoch + 1}/{args.epochs}, Loss: {running_loss / len(train_loader):.4f}")

    # [補完] 簡報的輸出有 test accuracy，但截圖裡沒有評估迴圈 —— 這段就是缺的那塊
    model.eval()
    correct = 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            correct += (torch.argmax(model(images), dim=1) == labels).sum().item()
    total = len(test_dataset)
    print(f"Test accuracy: {correct / total:.4f} ({correct}/{total})")

    # [原文] 單張推論：unsqueeze(0) 加上 batch 維度
    image, actual_label = test_dataset[0]
    with torch.no_grad():
        output = model(image.unsqueeze(0).to(device))
        predicted_label = torch.argmax(output, dim=1).item()
    print("Predicted Class:", predicted_label)
    print("Actual Class:", actual_label)

    if args.out:
        torch.save(model.state_dict(), args.out)
        print(f"已存權重: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

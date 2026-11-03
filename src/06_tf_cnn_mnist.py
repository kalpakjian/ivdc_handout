#!/usr/bin/env python3
"""06_tf_cnn_mnist.py — TensorFlow/Keras CNN 數字分類（MNIST）。

簡報 §七 的五個階段：載入資料 → 前處理 → 建模型 → 訓練 → 單張推論。

用法:
    python 06_tf_cnn_mnist.py                 # 5 epochs（簡報設定）
    python 06_tf_cnn_mnist.py --epochs 2      # 快速煙霧測試
    python 06_tf_cnn_mnist.py --no-plot       # 不畫圖

Python 版本
    TensorFlow 沒有 3.15 的 wheel（2026-11 實測），所以這支要用 3.11／3.12 跑：
        uv run --no-project --python 3.11 --with tensorflow-cpu -- python 06_tf_cnn_mnist.py

標註慣例
    # [原文]  簡報截圖上讀得到的程式碼
    # [補完]  截圖被滾動箭頭遮住／講義省略，依框架標準介面補完
"""

from __future__ import annotations

import argparse
import os
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TF/Keras MNIST CNN（簡報 §七）")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=32, help="Keras fit 預設值")
    parser.add_argument("--no-plot", action="store_true", help="不輸出預測圖")
    parser.add_argument("--out-dir", default="out/mnist_tf")
    args = parser.parse_args(argv)

    import numpy as np
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.datasets import mnist

    print(f"Python {sys.version.split()[0]} / TF {tf.__version__} / Keras {keras.__version__}")

    # [原文] 1. 載入資料
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    print("Training Data Shape:", x_train.shape)   # (60000, 28, 28)
    print("Test Data Shape:", x_test.shape)        # (10000, 28, 28)

    # [原文] 2. 前處理：多一維是通道數，除以 255 是正規化到 0～1
    x_train = x_train.reshape(-1, 28, 28, 1) / 255.0
    x_test = x_test.reshape(-1, 28, 28, 1) / 255.0

    # [原文] 3. 建立模型
    model = keras.Sequential([
        layers.Conv2D(32, (3, 3), activation="relu", input_shape=(28, 28, 1)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation="relu"),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(128, activation="relu"),
        layers.Dense(10, activation="softmax"),
    ])
    # [補完] 印出參數量：這是「兩套框架的架構真的等價」最硬的證據
    #        （PyTorch 版同樣是 225,034；loss 曲線接近只能算同量級，不能當證明）
    print(f"Param count: {model.count_params():,}")

    # [原文] 4. 編譯與訓練
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    history = model.fit(
        x_train, y_train,
        epochs=args.epochs,
        batch_size=args.batch_size,
        validation_split=0.1,
        verbose=2,
    )

    # [補完] 簡報沒貼評估段落，但它的預期輸出一開始就是 test accuracy
    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
    print(f"\nTest loss: {test_loss:.4f}")
    print(f"Test accuracy: {test_acc:.4f}")

    # [原文] 5. 單張推論
    index = 0
    prediction = model.predict(x_test[index:index + 1], verbose=0)
    print("Predicted Class:", int(np.argmax(prediction)))
    print("Actual Class:", int(y_test[index]))

    if not args.no_plot:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            os.makedirs(args.out_dir, exist_ok=True)
            path = os.path.join(args.out_dir, "prediction.png")
            plt.figure(figsize=(3, 3))
            plt.imshow(x_test[index].reshape(28, 28), cmap="gray")
            plt.title(f"pred={int(np.argmax(prediction))} / actual={int(y_test[index])}")
            plt.axis("off")
            plt.tight_layout()
            plt.savefig(path, dpi=120)
            print(f"已存檔: {path}")
        except Exception as exc:  # matplotlib 不是必要相依
            print(f"[提醒] 沒畫圖（{type(exc).__name__}），不影響結果")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

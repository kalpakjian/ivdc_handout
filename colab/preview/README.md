# colab/preview — notebook 的 HTML 快照

三本筆記本的 `nbconvert --to html` 版本，給「不想登入 Colab、只想快速看一眼內容」的情況用。
純靜態（含程式碼與表格），**不能執行**。

| 檔案 | 對應 notebook |
|---|---|
| `ivdc_exam_all_in_one.html` | `../ivdc_exam_all_in_one.ipynb`（9 支腳本內嵌，不需 clone） |
| `ivdc_exam_quickstart.html` | `../ivdc_exam_quickstart.ipynb`（git clone 版） |
| `yolo_only.html` | `../yolo_only.ipynb`（只有 YOLO 的 4 格） |

> ❗ `../teachable_machine_snake/teachable_machine_snake.ipynb`（手勢控制貪食蛇）**不在這裡**，
> 也不該放：它靠 Node 執行 `validate.js`，HTML 靜態快照沒意義。
> 要看內容請直接開 notebook，或看 `../teachable_machine_snake/README.md`。


## 重新產生

改了 `.ipynb` 之後要一起更新（否則兩份會不一致）：

```bash
cd ~/Projects/ivdc_handout
for nb in ivdc_exam_all_in_one ivdc_exam_quickstart yolo_only; do
  jupyter nbconvert --to html --output-dir colab/preview \
      --output "$nb" "colab/$nb.ipynb"
done
```

> 線上想看「渲染後」而不是原始碼，把 raw 網址丟進 <https://raw.githack.com> 即可，
> 例如 `raw.githack.com/kalpakjian/ivdc_handout/main/colab/preview/yolo_only.html`。

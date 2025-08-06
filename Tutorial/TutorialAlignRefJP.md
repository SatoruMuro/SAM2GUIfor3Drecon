# 位置合わせ修正ツール AlignRef の使い方（日本語）

---

## 📦 アプリのダウンロードと起動

1. 以下のリンクから `AlignRef.exe` をダウンロードしてください  
👉 [AlignRef v1.0 ダウンロードページ](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/releases/tag/AlignRefv1.0)

2. ダウンロードした `AlignRef.exe` をダブルクリックして起動します  
※ 初回起動時に Windows SmartScreen などの警告が表示される場合は「詳細情報」→「実行」を選択してください

---

## 🖼️ 画像の読み込みと表示

1. `Load Image Folder` をクリックして、画像フォルダを選択  
2. フォルダ内の画像（JPG/PNG/TIFF/DICOMなど）が読み込まれ、同じサイズのキャンバスに変換されます  
3. `←`, `→` キー、または `F`/`R`/`J`/`U` キーで前後の画像に切り替え可能  
4. `Fit to Window` ボタンで表示を画面にフィットさせます

---

## 🎨 キャンバス背景の設定と拡張

- `Canvas BG Color` から背景色（White または Black）を選択  
- `Expand Canvas` を押すと、全画像に上下左右100pxずつ余白が追加されます（位置調整のため）

---

## 🟡 画像の重ね合わせ（オーバーレイ）

- `Overlay Previous Image`：ひとつ前の画像を半透明で重ねて表示  
- `Overlay Next Image`：ひとつ後の画像を半透明で重ねて表示  
- `Clear Overlay`：オーバーレイ画像を非表示に戻す

---

## 🎯 位置の調整（位置合わせ）

1. `Start Recording Position` を押す  
2. キーボードで画像の移動・回転を行う：

   - 移動：`WASD`, `OKL;`, `↑↓←→`  
   - 回転：左回転 `Q`, `I` / 右回転 `E`, `P`

3. 位置が決まったら `Finish Recording Position` を押す  
4. 調整を適用したい範囲の画像を選び：

   - 開始画像に移動して `Set Position Start`  
   - 終了画像に移動して `Set Position End`

5. `Apply Position & Rotation` を押して一括適用  
6. `Cancel Applied Position` で元に戻すことも可能

---

## ✂️ クロップ（不要部分の切り取り）

1. `Start Crop` を押し、画像上で対角の2点をクリック  
2. 赤い枠が表示されます  
3. `Apply Crop` で全画像に同じ範囲でクロップを適用  
4. `Undo Crop` で元に戻せます  
5. `Clear Crop Box` で赤枠だけを削除可能

---

## 💾 画像の書き出し（エクスポート）

1. `Export Format` を選択（JPG, PNG, BMP, TIFF, DICOM）  
2. `Export Aligned Images` を押すと、加工後の画像を一括保存します  
   - 保存先フォルダは自動で作成されます（例：`inputname_aligned_YYYYMMDD_HHMMSS`）

---

## ⌨️ ショートカットキーまとめ

| 操作 | キー |
|------|------|
| 次の画像 | `→`, `F`, `J`, `PageDown` |
| 前の画像 | `←`, `R`, `U`, `PageUp` |
| 拡大縮小 | `Ctrl + マウスホイール` |
| 上下移動 | `W`, `S`, `O`, `L`, `↑`, `↓` |
| 左右移動 | `A`, `D`, `K`, `;`, `←`, `→` |
| 左回転 | `Q`, `I` |
| 右回転 | `E`, `P` |

---

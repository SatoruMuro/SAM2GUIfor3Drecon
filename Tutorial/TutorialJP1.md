# Seg&Refの使い方 - Step 1（日本語）

## Step 1：AIによる自動セグメンテーション

---

### 🖼 使用する画像の準備

- **対象**：連続切片画像・連続断層画像  
- **形式**：JPEG（`.jpg`）形式の画像  
- **ファイル名**：`image0001.jpg`, `image0002.jpg`, ... のように連番で保存  
- **推奨サイズ**：1辺が **1000ピクセル以下** （大きい画像も可能ですが、処理時間が長くなります）    
  ※一括リサイズには以下のツールが便利です：
  - 🔗 [ImageJ（Mac/Windows対応）](https://imagej.net/ij/)
  - 🔗 [IrfanView（Windows専用）](https://www.irfanview.com/)

---

### 🚀 セグメンテーションツールの起動（Google Colab）

**ツール名**：SAM2 GUI for Img Seq  
🔗 [こちらから開く（Google Colab）](https://colab.research.google.com/github/SatoruMuro/SAM2GUIfor3Drecon/blob/main/ColabNotebooks/SAM2GUIforImgSeqv4_7.ipynb)

#### 起動手順：
1. 「ランタイム」＞「ランタイムのタイプを変更」＞ **T4 GPU** を選択して保存  
2. メニュー「ランタイム」＞「すべてのセルを実行」  →警告が出たら「このまま実行」を選択（※実行完了まで約6分）  
3. ノートブックの **最下部までスクロール**  →セルの下に表示される `Running on public URL` のリンクをクリック  
   → Gradio GUIが開きます  
⚠️ **Colabノートブックの画面は閉じないでください！**

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/step1-01-2.PNG" alt="newmethod" width="50%">

---

### 🖱 GUIの基本操作フロー

1. 画像のアップロード（複数枚）  
2. 基準となる画像を選択  
3. 対象物のセグメンテーション  
   - 左上と右下の座標をそれぞれ指定  
   - 対象物のセグメンテーションが完了したら「完了」ボタンを押す  
4. 必要に応じて 2つ目、3つ目の対象物を追加（最大20個まで）  
5. 全対象物のセグメンテーション完了後、「Start Tracking」を押す  
6. セグメンテーション結果を確認  
7. 生成ファイルをダウンロード

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/GUIimage.JPG" alt="newmethod" width="50%">

---

### 📁 出力されるファイル

| フォルダ名 | 内容 | 形式 | 使用用途 |
|-----------|------|------|----------|
| `segmented_images` | 元画像とマスクを重ねた確認用画像 | PNG | 確認・記録・プレゼン |
| `mask_color_images` | RGBマスク画像 | PNG | 確認・記録・プレゼン |
| `mask_svgs` | ベクター形式マスク画像 | SVG | Step 2の修正作業 |
| `grayscale_masks` | グレースケールマスク画像 | PNG | Step 3の3D再構築 |


---

### 🎨 セグメンテーションの色ラベル

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/colorlabels1.jpg" alt="colorlist" width="50%">


---

### 🔁 ツールをリセットするには？

Gradio GUIの動作がおかしい場合は、以下の手順でリセットしてください：

1. GradioのGUI画面を一度閉じる  
2. Colabのノートブック画面に戻る  
3. メニュー「ランタイム」＞「ランタイムを接続解除して削除」  
4. 再度「すべてのセルを実行」

---

### ▶️ 次のステップへ進む 🔗

- 👉 [Step 2：マスク修正](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/TutorialJP2.md)
- 👉 [Step 3：3D再構築](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/TutorialJP3.md)

---


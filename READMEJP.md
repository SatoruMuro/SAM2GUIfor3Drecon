# SegRef3D

**SegRef3D** は、画像のセグメンテーションおよび修正をインタラクティブに行える PyQt6 ベースのGUIツールです。Meta社の Segment Anything Model 2（SAM2）を統合し、AIによる自動セグメンテーション、複数フレームにわたるオブジェクト追跡、編集、3D STL出力までをサポートします。

---

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/SegRef3Dimage01.png" alt="image" width="100%">

## 🧠 主な機能

* 🖼 画像フォルダの一括読み込み（DICOM含む）
* 📆 SAM2 による自動セグメンテーション（ボックスプロンプト）とマルチフレーム追跡
* ✨ 任意の範囲を指定したオブジェクト追跡（Start/Endフレームの指定、バッチ処理）
* 🎨 最大20オブジェクトまでのマスク編集と可視化切替
* 🖊 フリーハンド、点指定、境界スナップの描画モード
* ✏ Undo／Redo による編集履歴管理
* ↔ 色ラベルの一括変換・再割り当て機能
* 🔺 CT／MRIプリセットや手動による閾値抽出
* 🗈 間引き機能（N枚に1枚のみ保持）
* 🧲 出力機能：

  * グレースケールTIFF（昇順／降順）
  * mmスケーリング済みオブジェクト別 3D STL 出力
  * オブジェクトごとの体積CSV出力

---

## ⚙️ 動作環境

* OS：**Windows 10/11（64bit）**
* GPU：**CUDA対応NVIDIA GPU**（SAM2使用時）
* ソフトウェア：

  * Python 3.10以降
  * PyTorch（GPU環境ではCUDA版）

---

## 🚀 クイックスタート

### 1. ダウンロード

以下の実行ファイルをダウンロード：

* [`SegRef3D.exe`](https://www.dropbox.com/scl/fi/1xgq28szs6by1sp1qbskw/SegRef3D.zip?rlkey=3jtwph3muk24888rpya54f222&dl=1)
  （**Python + PyTorch の事前インストールが必要**）

`_internal` フォルダは `SegRef3D.exe` と同じ場所に配置してください。

> 📁 **補足:** ダウンロードして解凍したフォルダ（`SegRef3D.exe` と `_internal` フォルダを含む）は、`C:\` 直下に置くことを推奨します。  
> 例：`C:\SegRef3D\SegRef3D.exe`  
> ❗ デスクトップやドキュメントなど、**パスが長い場所や日本語・空白を含む場所**に置くと、実行時にエラーが発生する可能性があります。


### 2. 実行前の準備

⚠️ `.exe` を起動する前に **PythonとPyTorchをインストール**しておく必要があります。

---

### 🐍 Pythonのインストール（必須）

1. Python 3.10.x を以下からダウンロード：
   [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)

2. インストール時に以下を必ずチェック：
   ✅ Add Python to PATH

---

### 🔍 PyTorchがインストール済みか確認

コマンドプロンプトで以下を実行：

```
python -c "import torch; print(torch.__version__)"
```

→ バージョンが表示されればOK
→ エラーが出る場合は未インストール

---

### 📦 PyTorchのインストール方法

以下のいずれかをコマンドプロンプトで実行：

🟢 CUDA GPUあり（推奨）：

```
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

🔴 CPUのみ（非推奨）：

```
pip install torch torchvision
```

詳細: [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)

---

### 3. 起動

`SegRef3D.exe` をダブルクリックで起動。

> ⚠️ NVIDIA GPU + CUDA が無い場合、SAM2に関するボタンは無効になります。

---

## 📘 詳細チュートリアル

詳しい操作手順はこちら：  
👉 [使用方法チュートリアル（日本語）](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/TutorialSegRef3DJP.md)

---

## 🔄 位置合わせ

連続組織切片の画像などでは、セグメンテーションや3D再構築の前に位置合わせが必要です。  
👉 [詳細なレジストレーション手順はこちらをご覧ください](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/Registration.md)

> 💡 **補足:** CTやMRI画像は撮影時にすでに整列されているため、通常は位置合わせは**不要**です。  
> 一方で、**組織の連続切片**では、物理的な歪みや切片ズレの影響により、位置合わせが必要になることがあります。

---

## 📂 入力フォーマット

* 入力画像形式：`.jpg`, `.png`, **または DICOM (.dcm)**
* 組織連続切片の場合は、セグメンテーション前に位置合わせ（Registration）が必要：
  [詳細はこちら](Tutorial/Registration.md)
* マスク形式：SVG（最大20色の定義済みRGBに対応）

---

## 🧠 SAM2 自動セグメンテーション機能

* **Set Box Prompt** を押して範囲指定
* **Run Seg** を押してSAM2によるセグメンテーション実行
* **Set Tracking Start / End** を使ってトラッキング範囲を指定し、**Run Tracking** を押して伝播
* 必要に応じて **Run Batch Tracking** により複数オブジェクトを一括追跡

> 📌 `sam2_interface.py` は内部で `sam2pkg/sam2` の `build_sam2` モジュールを呼び出しています。

---

## ⚙️ STL／体積CSV 出力

* DICOM画像の場合は **キャリブレーション不要**
* `.jpg`, `.png` の場合：

  * **Draw Calibration Line** でスケール線を描画
  * 実際の長さ（mm）と z間隔（mm）を入力
* その後、**Export STL** または **Export Volume CSV** をクリック

---

## 🎨 マスク編集ツール

* **Add to Mask** / **Erase from Mask**：描画領域を追加／削除
* **Transfer To**：描画領域を別のオブジェクトに移動
* **Convert Color**：色ラベルを全画像にわたって変換
* **Overlap Detection**：2つのオブジェクトの重なり領域を抽出・可視化
* **Undo/Redo Edit**：編集の取り消しとやり直し

---

## 🖥️ GPU非搭載環境での活用法

CUDA非対応環境でも、以下のように段階的に処理することでSegRef3Dを使用可能です：

* Google Colab上で自動セグメンテーション（SAM2）を実行
* 生成されたSVGマスクをローカルPCで修正・STL出力

### 🔗 Webベースのセグメンテーション手順

* 🇯🇵 日本語: [TutorialJP1.md](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/TutorialJP1.md)
* 🇺🇸 英語: [TutorialEN1.md](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/TutorialEN1.md)

### 📷 Web処理用画像の注意点

* Web版は `.jpg` のみ対応
* SegRef3DでDICOM画像を読み込むと、自動的に `.jpg` 変換画像も保存されます

### 🔁 統合ワークフロー

* Webで作成した `.svg` ファイルをSegRef3Dに読み込み
* インタラクティブに修正・3D STL出力を実施
* GPUが無い場合、SegRef3D上の自動セグメンテーション機能は無効になります

---


# License
The code for the SegRef3D, JPG Converter, SAM2  for Img Seq, ColorChanger, Vectorizer Colab, Segment Editor PP, Graphic2shape, and Object Mask Splitter is licensed under the [Apache 2.0 License](https://github.com/SatoruMuro/SAM2for3Drecon/blob/main/LICENSE).

---

# 📚 Citation｜引用

本ツールを研究・論文等で使用される場合は、以下の論文を引用してください。  
If you use this tool for research or academic purposes, please cite the following article:

**Muro S, Ibara T, Nimura A, Akita K.**  
**Seg & Ref: A Newly Developed Toolset for Artificial Intelligence-Powered Segmentation and Interactive Refinement for Labor-Saving Three-Dimensional Reconstruction.**  
*Microscopy (Oxford)*. (in press)  
🔗 [DOI: 10.1093/jmicro/dfaf015](https://academic.oup.com/jmicro/advance-article/doi/10.1093/jmicro/dfaf015/8051094?utm_source=authortollfreelink&utm_campaign=jmicro&utm_medium=email&guestAccessKey=d61820c6-f079-42aa-b81c-767f36f8d455)

---

### 📎 BibTeX

```bibtex
@article{Muro2025,
  author    = {Muro, Satoru and Ibara, T. and Nimura, A. and Akita, K.},
  title     = {Seg \& Ref: A Newly Developed Toolset for Artificial Intelligence-Powered Segmentation and Interactive Refinement for Labor-Saving Three-Dimensional Reconstruction},
  journal   = {Microscopy (Oxford)},
  year      = {in press},
  doi       = {10.1093/jmicro/dfaf015}
}
```

---

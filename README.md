# "Seg & Ref": AI-Powered Segmentation and Interactive Refinement for Labor-Saving 3D Reconstruction  

---

## 🛠 Workflow
🔹 **Step 0. Image Preprocessing (Registration or DICOM Conversion)**
- 🧬 **Histological sections**  →  🔗 [Registration](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/Registration.md)
- 🏥 **CT or MRI in DICOM format**  →  🔗 [DICOM Conversion](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/toolforDICOM.md)
  
🧠 **Step 1. Seg: AI-Powered Segmentation**  
- 🔗 [SAM2GUIforImgSeq (Colab)](https://colab.research.google.com/github/SatoruMuro/SAM2GUIfor3Drecon/blob/main/ColabNotebooks/SAM2GUIforImgSeqv4_7.ipynb)
  
 🎨 **Step 2. Ref: Interactive Refinement**  
- 🔗 [ColorChanger (Colab)](https://colab.research.google.com/github/SatoruMuro/SAM2GUIfor3Drecon/blob/main/ColabNotebooks/ColorChanger_v1_4.ipynb)  (Optional)  
- 🔗 [SegmentEditorPP](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/releases/tag/ref2.0) (with [Graphic2shape](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/releases/tag/gv1.2))  
  
🧱 **Step 3. 3D Reconstruction**  
- 🔗 [3D Slicer](https://www.slicer.org/)
  
<img src="images/graphical_abstract_v01jpg.jpg" alt="threesteps" width="50%">

---

# What is "Seg & Ref"?  

**Seg & Ref（セグレフ）**は、3D再構築のための連続断層画像に特化した **Webベースの自動セグメンテーションツール**です。

### 🧠 主な特徴｜Key Features

- 🧩 **連続切片に特化**  
  組織連続切片・解剖断面・CT・MRI・超音波などに対応  
  *Specialized for serial sections including histology, anatomy, CT, MRI, and ultrasound*

- 🤖 **SAM2によるゼロショット自動セグメンテーション**  
  学習不要で対象を自動抽出  
  *Zero-shot segmentation using Segment Anything Model 2 (SAM2), no training needed*

- 💻 **インストール不要のWeb GUI**  
  ブラウザ上で動作、PCへの環境構築不要  
  *Runs entirely in a browser. No local setup required.*

- ✍️ **マスク修正ツール付き**  
  セグメンテーション結果をユーザー自身で確認・修正可能  
  *Includes an interactive correction tool for mask editing*

- 🧱 **3D Slicerとの連携**  
  出力マスクはそのまま3D Slicerで読み込み、迅速な3D再構築が可能  
  *Outputs can be directly imported into 3D Slicer for quick reconstruction*

### ⚠️ 注意｜Notes

- 🧬 **組織連続切片**を使用する場合は、セグメンテーション前に**位置合わせ**が必要です  
　→ 自動位置合わせの方法は 🔗 [こちら（MultiStackReg）](Tutorial/Registration.md)  
　*Histological serial sections require registration before segmentation. See [this page](Tutorial/Registration.md) for details.*

- 🏥 **CTやMRIなどのDICOM画像は、事前にJPEG（.jpg）形式へ変換**しておく必要があります  
　→ DICOM画像からJPEGへの変換ツールは 🔗 [こちら（DICOM Conversion）](Tutorial/toolforDICOM.md)  
　*CT or MRI DICOM images must be converted to .jpg format before use. See [DICOM Conversion](Tutorial/toolforDICOM.md).*

- 🪟 **Step 2で使用する修正ツール**（Segment Editor PP / Graphic2shape）は**Windows専用**です  
　Macなど他のOSでは動作に制限があります  
　*Correction tools used in Step 2 are developed for Windows and may not work on macOS or Linux.*

---

## 🎥 解説・デモ動画（Demo Videos）

### 📘 ツールの紹介｜Introduction to Seg & Ref

<table>
<tr>
<td align="center">
<b>🔹 日本語紹介動画</b><br>
<a href="https://youtu.be/Zs4pfO2FmXE">
  <img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/watchvideoicon1.png" alt="Seg&Ref JP Intro" width="100">
</a><br>
「Seg & Ref」ツールの概要と使い方（日本語）
</td>
<td align="center">
<b>🔹 English Intro Video</b><br>
<a href="https://youtu.be/rz2QdxfIM9w">
  <img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/watchvideoicon1.png" alt="Seg&Ref EN Intro" width="100">
</a><br>
Introduction to "Seg & Ref" Segmentation Tool (English)
</td>
</tr>
</table>

### 🛠 操作デモ｜Usage Demonstrations

<table>
<tr>
<td align="center">
<b>🕒 10分で分かる操作デモ｜10-Minute Demo</b><br>
<a href="https://youtu.be/12ihvPAgfps">
  <img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/watchvideoicon1.png" alt="10-min Demo" width="100">
</a><br>
基本操作をまとめたショートデモ（10分）<br>
Short demonstration covering basic operations (10 min)
</td>
<td align="center">
<b>🎬 フルライブデモ｜Full Live Demonstration</b><br>
<a href="https://youtu.be/-0zrfhaeAX4">
  <img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/watchvideoicon1.png" alt="Full Live Demo" width="100">
</a><br>
操作を実演するライブ収録（フルバージョン）<br>
Full-length live demonstration with step-by-step operation
</td>
</tr>
</table>

---

# 使い方（日本語）

0. 🛠️ Step 0：画像の前処理（位置合わせ・DICOM変換）
   - 🧬 組織切片画像の位置合わせ → [Registration](./Tutorial/Registration.md)
   - 🏥 CT・MRI（DICOM形式）の変換 → [DICOM Conversion](./Tutorial/toolforDICOM.md)

1. 🟢 [Step 1：AIによる自動セグメンテーション](./Tutorial/TutorialJP1.md)
2. ✍️ [Step 2：セグメンテーションマスクの修正](./Tutorial/TutorialJP2.md)
3. 🧱 [Step 3：3D再構築とSTL出力](./Tutorial/TutorialJP3.md)


---

# How to Use (English)

0. 🛠️ Step 0: Image Preprocessing (Registration / DICOM Conversion)  
   - 🧬 Registration of histological section images → [Registration](./Tutorial/Registration.md)  
   - 🏥 Conversion of CT/MRI (DICOM format) → [DICOM Conversion](./Tutorial/toolforDICOM.md)

1. 🟢 [Step 1: AI-Powered Automatic Segmentation](./Tutorial/TutorialEN1.md)  
2. ✍️ [Step 2: Refining Segmentation Masks](./Tutorial/TutorialEN2.md)  
3. 🧱 [Step 3: 3D Reconstruction and STL Export](./Tutorial/TutorialEN3.md)


---


# Update  
**2025.6.10**  
SAM2GUIforImgSeqに、割り当て色番号の開始番号をユーザーが指定できる機能を追加（SAM2GUIforImgSeqv4.7.ipynb）。  

**2025.4.14**  
Segment Editor PPに一括処理などのマクロを複数追加（SegmentEditorPPv2.0.pptm）

**2025.3.11**  
No module named 'sam2'となるエラーを修正（SAM2GUIforImgSeqv4.6.ipynb）。  

**2025.3.11**  
PyTorch + CUDA + cuDNNの互換性を修正（SAM2GUIforImgSeqv4.3.ipynb）。  

**2025.2.4**  
SAM2 GUI for Img Seqのリセット方法を明記（SAM2GUIforImgSeqv4.2.ipynb）。  
SegmentEditorPPの新しいバージョンを追加(SegmentEditorPP1.4.pptm)。  

**2024.11.19**  
SAM2 GUI for Img Seqの中身をSAM2からSAM2.1にグレードアップさせました（SAM2GUIforImgSeqv4.0.ipynb）。これにより精度向上が期待されます（使用実感としてはあまり変わらないかもです）。  

**2024.10.25**  
Segment Editor PPにグレースケールのマスク画像の出力機能を追加しました（SegmentEditorPPv1.2.pptm）。これにより、3D slicerでのセグメント認識がより簡便になります。Tutorialの記載を更新しました。  

**2024.10.25**  
SAM2 GUI for Img Seqにグレースケールのマスク画像の出力機能を追加しました（SAM2GUIforImgSeqv3.6.ipynb）。これにより、3D slicerでのセグメント認識がより簡便になります。（詳細は後日Tutorialを更新して記載します）  

**2024.10.17**  
SAM2 GUI for Img Seqにベクター化機能（SVGファイル出力機能）を追加しました（SAM2GUIforImgSeqv3.4.ipynb）。これにより、[Vectorizer Colab](https://colab.research.google.com/github/SatoruMuro/SAM2GUIfor3Drecon/blob/main/ColabNotebooks/Vectorizer_v5.ipynb)を用いてベクター変換作業を行う必要がなくなりました。同様にColorChangerにもベクター化機能を追加しました（ColorChanger_v1.3.ipynb）。  

---

# Link of tools  
JPG Converter: [HuggingFace](https://huggingface.co/spaces/SatoruMuro/JPGconverter),[GoogleColab](https://colab.research.google.com/github/SatoruMuro/SAM2GUIfor3Drecon/blob/main/ColabNotebooks/JPGconverter_v1_1.ipynb)  
SAM2 GUI for Img Seq: [HuggingFace](https://huggingface.co/spaces/SatoruMuro/SAM2GUIforImgSeq)(*Low-precision model running slowly on CPU), [GoogleColab](https://colab.research.google.com/github/SatoruMuro/SAM2GUIfor3Drecon/blob/main/ColabNotebooks/SAM2GUIforImgSeqv4_7.ipynb)(*High-power model running on GPU, this is recommended) , [GoogleColab(previous version](https://colab.research.google.com/github/SatoruMuro/SAM2GUIfor3Drecon/blob/main/ColabNotebooks/SAM2GUIforImgSeqv3_9.ipynb)   
Color Changer: [HuggingFace](https://huggingface.co/spaces/SatoruMuro/ColorChanger), [GoogleColab](https://colab.research.google.com/github/SatoruMuro/SAM2GUIfor3Drecon/blob/main/ColabNotebooks/ColorChanger_v1_4.ipynb)  
Object Mask Splitter: [GoogleColab](https://colab.research.google.com/github/SatoruMuro/SAM2GUIfor3Drecon/blob/main/ColabNotebooks/ObjectMaskSplitterv2_5.ipynb) , [GoogleColab(new ver)](https://colab.research.google.com/github/SatoruMuro/SAM2GUIfor3Drecon/blob/main/ColabNotebooks/ObjectMaskSplitterv2_8.ipynb)   

---

# License
The code for the JPG Converter, SAM2  for Img Seq, ColorChanger, Vectorizer Colab, Segment Editor PP, Graphic2shape, and Object Mask Splitter is licensed under the [Apache 2.0 License](https://github.com/SatoruMuro/SAM2for3Drecon/blob/main/LICENSE).

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

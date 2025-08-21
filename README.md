# SegRef3D

**SegRef3D** is a PyQt6-based GUI tool for interactive image segmentation and refinement. It integrates the Segment Anything Model 2 (SAM2) for AI-powered segmentation and supports multi-frame object tracking, editing, and export for 3D reconstruction workflows.    
  
日本語は[こちら](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/READMEJP.md)  

---
<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/SegRef3Dimage02.png" alt="image"  width="100%">

---

## 🎥 SegRef3D Tutorial Videos

Watch the **Basic Workflow** video to learn how to use SegRef3D, from loading images to AI-powered segmentation, mask editing, tracking, and exporting results.  

[How to use SegRef3D: 01. Basic Workflow (YouTube)](https://youtu.be/JModwfnBTYU)

---

## 🧠 Features

* 🖼 Load image folders
* 📆 Integration with **SAM2** for box-prompted segmentation and video tracking
* ✨ Object tracking with start/end frame selection and batch execution
* 🎨 Mask editing for up to 20 objects, with per-object color toggling
* 🖊 Freehand, point-to-point, and snap-to-boundary drawing modes
* ✏ Undo/redo support for editing
* ↔ Convert and reassign object colors across all masks
* 🔺 Threshold-based region extraction (CT/MRI presets or manual)
* 🗈 Thinning: reduce number of images by keeping every N-th
* 🧲 Export:
  * Mask images as grayscale TIFF (ascending/descending order)
  * 3D STL models by color (with mm/px and z-spacing calibration)
  * Volume statistics per object as CSV

---

## ⚙️ System Requirements

* **Operating System:** Windows 10/11 (64-bit)  
* **Hardware:** NVIDIA GPU with CUDA support (for using SAM-based segmentation and tracking)  
  - CPU-only environment: SegRef3D can run, but **SAM features are disabled**.  
    Other functions (e.g., file handling, visualization, basic utilities) remain available.  
* **Software:** No need to install Python or PyTorch — they are already bundled with SegRef3D  



---

## 🚀 Quick Start

### 1. Download

Download the ready-to-use **SegRef3D** application as a ZIP file:

* [`SegRef3D.zip`](https://www.dropbox.com/scl/fi/1xgq28szs6by1sp1qbskw/SegRef3D.zip?rlkey=3jtwph3muk24888rpya54f222&st=ajyyhjrm&dl=1)  

After downloading, unzip the file.

> 📁 **Tip:** Move the entire unzipped folder (which includes `SegRef3D.exe` and the `_internal` folder) to a simple path like `C:\SegRef3D\`.  
> ❗ Avoid placing the folder in locations with **long paths, Japanese characters, or spaces** (e.g., Desktop or Documents), as this may cause runtime errors.


### 2. Preparation Before Execution

✅ **No need to install Python or PyTorch.**  
Everything required to run SegRef3D is already bundled inside the application.

⚠️ **Requirement:**  
If you want to use **SAM-based segmentation and tracking**, make sure the PC has an **NVIDIA GPU with a compatible driver installed**.  

- **GPU environment:** Full functionality (including SAM)  
- **CPU environment:** SAM features are disabled, but other tools remain usable  


### 3. Run

Double-click `SegRef3D.exe` to start the application.  
The `_internal` folder **must be located in the same directory** as `SegRef3D.exe`.

> ⚠️ SAM2 features (AI segmentation and tracking) require an NVIDIA GPU and CUDA-compatible drivers.  
> If your system is not compatible, the related buttons will be automatically disabled.  
> ❗ Be careful **not to delete the `_internal` folder** — the application will fail to launch without it.  
> 💡 **Tip:** The first startup may take longer than usual while the environment initializes.  


---

## 📘 Full Tutorial

Looking for step-by-step instructions?  
👉 [Read the full usage tutorial here](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/TutorialSegRef3DEN.md)

---

## 🔄 Registration (Alignment)

For serial images such as histological sections, alignment (registration) is essential before segmentation or 3D reconstruction.  
👉 [See detailed registration steps here](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/Registration.md)

> 💡 **Note:** Registration is typically **not required** for CT or MRI images, since they are already aligned during acquisition. However, **histological serial sections** often need registration (alignment) due to physical distortion and sectioning artifacts.

---

## 📂 Input Format

* Input images: `.jpg`, `.png`, **or DICOM (.dcm)** files stored in a folder
* Histological serial sections require registration before segmentation. See [this page](Tutorial/Registration.md) for details.
  `.jpg`, `.png`, **or DICOM (.dcm)** files stored in a folder
* Masks: SVG format with objects encoded using predefined 20 RGB colors

---

## 🧠 SAM2 Integration

To use SAM2 for segmentation and tracking:

* Press **Set Box Prompt** and select a rectangular area
* Press **Run Seg** to apply SAM2 segmentation
* Use **Set Tracking Start / End** and **Run Tracking** to propagate mask
* Optionally use **Run Batch Tracking** for multiple object prompts

> 📌 Note: `sam2_interface.py` internally loads the `build_sam2` module from `sam2pkg/sam2`.

---

## 🎨 Object Editing Tools

* **Add to Mask** / **Erase from Mask**: modify selected object by drawing
* **Transfer To**: reassign mask region to another object
* **Convert Color**: reassign color label across images
* **Overlap Detection**: visualize and extract overlapping areas
* **Undo/Redo Edit**: fully reversible editing

---

## ⚙️ STL and Volume Export

* If your input images are DICOM files, calibration is **not required**.
* For other image types (e.g., `.jpg`, `.png`):

  * Draw a line using **Draw Calibration Line**
  * Input actual mm length and z-spacing
* Then, click **Export STL** or **Export Volume CSV**

---

## 🖥️ For Non-GPU Environments

If you do not have a CUDA GPU environment, you can still perform segmentation using a hybrid approach:

* Run automatic segmentation on the web (Google Colaboratory)
* Perform manual refinement and 3D STL export locally using SegRef3D

### 🔗 Web-based Segmentation Tutorial

* 🇯🇵 Japanese: [TutorialJP1.md](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/TutorialJP1.md)
* 🇺🇸 English: [TutorialEN1.md](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/TutorialEN1.md)

### 📷 Notes for Web-based Workflow

* The web version only supports `.jpg` images as input.
* When you load DICOM images into SegRef3D, the corresponding `.jpg` versions are automatically saved in the new folder.
* You can then upload those `.jpg` images to Google Colab for segmentation.

### 🔁 Final Integration

* Import the `.svg` mask files generated on the web into SegRef3D.
* You can edit them interactively and export STL models even without a GPU.
* On non-GPU systems, all automatic SAM2 features will be disabled by default.

---


# Update  
**2025.7.29**  
SegRef3Dを公開。

**2025.7.3**  
SAM2GUIのローカル実行版を公開。

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

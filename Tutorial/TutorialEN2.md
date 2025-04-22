# How to Use Seg&Ref - Step 2

## Step 2: Refining Segmentation Masks

---

### ⚠️ Important Notes
**Segment Editor PP** and **Graphic2shape** are **Windows-only tools**. Functionality may be limited on other operating systems (e.g., macOS, Linux).

---

### 🧠 For Those Who Performed Segmentation Multiple Times

If you performed segmentation multiple times in Step 1, please use the color re-mapping tool below to avoid overlapping color labels:

🔗 [ColorChanger (Colab)](https://colab.research.google.com/github/SatoruMuro/SAM2GUIfor3Drecon/blob/main/ColabNotebooks/ColorChanger_v1_4.ipynb)

---

### 🛠 Tools Required

- 🔽 [Segment Editor PP](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/releases/tag/ref2.0) (PowerPoint Macro Tool)  
- 🔽 [Graphic2shape](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/releases/tag/gv1.2) (Shape Conversion Tool)  
- 🔁 Input file: `mask_svgs` (SVG files) output from Step 1

---

### ✅ 1️⃣ Initial Setup (Files)

**(1) Enabling Macros in the .pptm File**  
1. Right-click the file and select **Properties**  
2. Under the “General” tab, check `Unblock`  
3. Click OK  
4. Open the file in PowerPoint and click **Enable Content**

**(2) Slide Size Adjustment**  
Adjust the slide size to match the aspect ratio (width:height) of your source images.

**(3) Add Macros to the Quick Access Toolbar**  
Add macros `Ba`, `Bb`, and `Bc` to the toolbar:

1. Click the "▼" at the top-left corner  
2. Select “More Commands”  
3. Choose `Macros` from the dropdown  
4. Add the three macros and arrange them in order  
5. Shortcut keys like `Alt + 1`, `Alt + 2`, etc. will now work

**(4) Display Developer Tab**  
Enable via:  
`File > Options > Customize Ribbon > Developer`

---

### ✅ 2️⃣ Setup for Editing Environment

**(1) Recommended Setup**  
- Touchscreen PC (e.g., Surface Book) + pen  
  or  
- Pen tablet (e.g., Wacom Cintiq) + keyboard  

Recommended position:
- Pen in right hand, keyboard in left (or reversed for left-handed users)

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/setting01.jpg" alt="Setting" width="50%">

**(2) Key Remapping with PowerToys**  
Use [PowerToys](https://github.com/microsoft/PowerToys/releases/tag/v0.85.0) to remap keys:

| Function                    | Original Key | Remapped Key |
|----------------------------|--------------|--------------|
| Macro Ba                   | Alt + 1      | A            |
| Macro Bb                   | Alt + 2      | S            |
| Macro Bc                   | Alt + 3      | D            |
| Slide back                 | PgUp         | R            |
| Slide forward              | PgDn         | F            |
| Ctrl (zoom)                | Ctrl         | E            |
| Delete                     | Delete       | Q            |
| Esc (deselect)             | Esc          | W            |

🖋 Example:
- Index finger = PgUp/PgDn
- Middle finger = Ctrl
- Other hand = Mouse scroll for zoom

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/setting02.png" alt="Setting" width="50%">

---

### 🗂 Macro Structure and Workflow (Segment Editor PP)

#### 🔷 Group A: Input Preparation

| Macro Name | Description |
|------------|-------------|
| `AaAddImages` | Import source images (1 per slide) |
| `AbAddMasks`  | Overlay SVG masks on each slide |
| `AcDeleteBlackShapesWith70PercentTransparent` | Remove black background and apply 70% opacity |

**Steps:**
1. Open PowerPoint and bring to front  
2. Run `AaAddImages` → select folder of `.jpg` source images  
3. Run `AbAddMasks` → select `mask_svgs` folder  
4. Launch [Graphic2shape](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/releases/tag/gv1.2)  
   → Enter slide count and wait for shape conversion  
5. Run `AcDeleteBlackShapesWith70PercentTransparent`

---

#### 🖊 Group B: Editing Masks

| Macro Name | Description |
|------------|-------------|
| `BaSelectShapeAndRecord` | Set mask as editing target |
| `BbCutimageWithPreviousShapeAndApplyColor` | Subtract drawn area |
| `BcMergeWithPreviousShapeAndApplyColor` | Add drawn area |

**Steps:**
1. Select the mask  
2. Run `BaSelectShapeAndRecord`  
3. Use Freeform or Curve tool to draw  
4. With shape selected, run `Bb` or `Bc`

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/refine01.png" alt="Refine" width="80%">

---

#### 💾 Group C: Exporting Results

| Macro Name | Description |
|------------|-------------|
| `CaFinalizeMasks` | Hide background and isolate masks |
| `CbExportToGrayPNG` | Export grayscale PNG (for Step 3) |
| `CbExportToPNG` | Export RGB PNG |
| `CcReturnToMaskEditing` | Revert to edit mode |

**Steps:**
1. Run `CaFinalizeMasks`  
2. Run `CbExportToGrayPNG` → enter image dimensions  
   (e.g., 378 × 613 px)

💡 Use `CbExportToPNG` for RGB-based workflows  
💡 Use `CcReturnToMaskEditing` to resume editing

---

### 📁 Output Folder Notes

- Files are saved in `edittedmasks` folder (same as `.pptm` location)  
- If already exists, it will be **overwritten**

---

### ▶️ Proceed to Next Step 🔗

👉 [Step 3: 3D Reconstruction](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/TutorialEN3.md)

---

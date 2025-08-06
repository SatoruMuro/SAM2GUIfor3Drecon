# AlignRef User Guide (English)

---

## 📦 Download and Launch the App

1. Download `AlignRef.exe` from the following link:  
👉 [Download AlignRef.exe via Dropbox](https://www.dropbox.com/scl/fi/xgc0czggdzfe3fzdzj153/AlignRef.exe?rlkey=2981juzc8p3jtuo7e3ove5gq3&st=rzqy9mvg&dl=1)  
※ Due to its large file size, the application is distributed via Dropbox instead of GitHub.

2. Double-click `AlignRef.exe` to launch the application  
※ On first launch, Windows SmartScreen may show a warning. Click “More info” → “Run anyway” to proceed.

---

## 🖼️ Loading and Viewing Images

1. Click `Load Image Folder` and select a folder containing your images  
2. Images (JPG/PNG/TIFF/DICOM, etc.) will be loaded and resized to a unified canvas  
3. Use `←`/`→` or `F`/`R`/`J`/`U` keys to switch between images  
4. Click `Fit to Window` to fit the image display to the screen

---

## 🎨 Canvas Background and Expansion

- Select canvas background color from `Canvas BG Color` (White or Black)  
- Click `Expand Canvas` to add 100px margin to all sides of every image (for alignment purposes)

---

## 🟡 Image Overlay

- `Overlay Previous Image`: overlay the previous image in semi-transparent mode  
- `Overlay Next Image`: overlay the next image  
- `Clear Overlay`: remove any overlaid image

---

## 🎯 Position Adjustment (Image Alignment)

1. Click `Start Recording Position`  
2. Use the keyboard to move and rotate the image:

   - Move: `WASD`, `OKL;`, `↑↓←→`  
   - Rotate: Left `Q`, `I` / Right `E`, `P`

3. When finished, click `Finish Recording Position`  
4. Set the range of images to apply the adjustment:

   - Go to the first frame → `Set Position Start`  
   - Go to the last frame → `Set Position End`

5. Click `Apply Position & Rotation` to apply the transform to all selected images  
6. Use `Cancel Applied Position` to undo the operation

---

## ✂️ Cropping (Remove Unwanted Areas)

1. Click `Start Crop`, then click two diagonal corners on the image  
2. A red box will appear  
3. Click `Apply Crop` to crop all images with the same box  
4. Use `Undo Crop` to revert the change  
5. Use `Clear Crop Box` to remove the red box only

---

## 💾 Exporting Images

1. Select the `Export Format` (JPG, PNG, BMP, TIFF, or DICOM)  
2. Click `Export Aligned Images` to export all processed images  
   - A new folder will be created automatically (e.g., `inputname_aligned_YYYYMMDD_HHMMSS`)

---

## ⌨️ Keyboard Shortcuts

| Action | Keys |
|--------|------|
| Next image | `→`, `F`, `J`, `PageDown` |
| Previous image | `←`, `R`, `U`, `PageUp` |
| Zoom in/out | `Ctrl + Mouse Wheel` |
| Move up/down | `W`, `S`, `O`, `L`, `↑`, `↓` |
| Move left/right | `A`, `D`, `K`, `;`, `←`, `→` |
| Rotate left | `Q`, `I` |
| Rotate right | `E`, `P` |

---

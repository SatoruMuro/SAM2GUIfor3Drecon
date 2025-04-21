# How to Use Seg & Ref - Step 1 (English)

## Step 1: AI-Powered Automatic Segmentation

---

### 🖼 Preparing the Input Images

- **Target**: Serial section images / continuous tomographic images  
- **Format**: JPEG (`.jpg`)  
- **File naming**: Save the images sequentially as `image0001.jpg`, `image0002.jpg`, etc.  
- **Recommended size**: Each side should be **1000 pixels or less**  
  (Larger images are acceptable but may increase processing time)

💡 Batch resizing tools:
- 🔗 [ImageJ (Mac/Windows)](https://imagej.net/ij/)
- 🔗 [IrfanView (Windows only)](https://www.irfanview.com/)

---

### 🚀 Launching the Segmentation Tool (Google Colab)

**Tool name**: SAM2 GUI for Img Seq  
🔗 [Click here to open in Google Colab](https://colab.research.google.com/github/SatoruMuro/SAM2GUIfor3Drecon/blob/main/ColabNotebooks/SAM2GUIforImgSeqv4_6.ipynb)

#### How to launch:
1. From the menu, go to `Runtime > Change runtime type`, and select **T4 GPU**, then save  
2. Click `Runtime > Run all`  
   → When a warning appears, click “Run anyway” (Execution takes about 6 minutes)  
3. Scroll to the **very bottom of the notebook**  
4. Click the `Running on public URL` link that appears under Cell  
   → This will open the Gradio GUI  
⚠️ **Do not close the Colab notebook while the GUI is running!**

<img src="images/step1-01-2.PNG" alt="newmethod" width="50%">

---

### 🖱 Basic GUI Operation Flow

1. Upload multiple images  
2. Select a reference image  
3. Segment each target object  
   - Specify the top-left and bottom-right coordinates  
   - Click the “Done” button once the segmentation is complete  
4. Add the next object if needed (up to 20 objects can be segmented)  
5. After all segmentations are complete, click “Start Tracking”  
6. Review the segmentation results  
7. Download the generated output files

<img src="images/GUIimage.JPG" alt="newmethod" width="50%">

---

### 📁 Output Files

| Folder Name         | Description                                             | Format | Use Case                        |
|---------------------|---------------------------------------------------------|--------|----------------------------------|
| `segmented_images`  | Overlay of original image and segmentation mask         | PNG    | Review, documentation, presentation |
| `mask_color_images` | RGB segmentation masks                                  | PNG    | Review, documentation, presentation |
| `mask_svgs`         | Vectorized segmentation masks                           | SVG    | Manual correction in Step 2     |
| `grayscale_masks`   | Grayscale segmentation masks                            | PNG    | 3D reconstruction in Step 3     |

---

### 🎨 Segmentation Color Labels

<img src="images/colorlabels1.jpg" alt="colorlist" width="50%">

---

### 🔁 How to Reset the Tool

If the Gradio GUI becomes unresponsive, follow these steps to reset:

1. Close the Gradio GUI window  
2. Return to the Colab notebook  
3. Go to `Runtime > Disconnect and delete runtime`  
4. Then run `Runtime > Run all` again

---

### ▶️ Proceed to the Next Step 🔗

- 👉 [Step 2: Interactive Mask Refinement](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/TutorialEN2.md)
- 👉 [Step 3: 3D Reconstruction](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/TutorialEN3.md)

---

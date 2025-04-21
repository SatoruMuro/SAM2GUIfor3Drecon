## How to Use Seg&Ref - Step 3

## Step 3: 3D Reconstruction and STL Export

In this step, you will use the free software [3D Slicer](https://www.slicer.org/) to generate a 3D model from the refined grayscale masks created in Step 2.  
Other software such as Amira-Avizo or ImageJ can also be used to generate 3D models from grayscale masks.

---

### 🔧 Preparation

- 🔗 [Download 3D Slicer](https://www.slicer.org/)
- Determine the **actual image scale (px/mm)** used in your section images  
  (e.g., via scale bar embedded in the image or measuring the physical specimen)

---

### 🗂 1. Load Mask Images and Adjust Scale

1. Launch 3D Slicer
2. From the top menu, set the view mode to **"Conventional"**
3. Go to `Add Data > Choose Directory to Add` and select the folder containing the **grayscale masks (mask_gray_png)** exported from Step 2
4. Go to `Volumes > Volume Information` and adjust **Image Spacing**:
   - From left to right: `X axis`, `Y axis`, `Z axis`
   - For `Z axis`, enter:  
     **px/mm × slice interval (mm)**  
     (e.g., 2.96 px/mm × 0.2 mm = 0.592)

💡 `X` and `Y` spacing can typically remain at 1.0  
💡 As long as the ratio among `X`, `Y`, and `Z` is preserved, you may scale as needed (e.g., actual size or 10× scale)  
💡 If the display shifts, use the `Center View` button to re-center the image

<img src="images/step3-03.PNG" alt="Import Image" width="90%">

<img src="images/step3-04.PNG" alt="Volume Info" width="90%">

---

### 🧱 2. Extract Segments and Build 3D Model

1. Switch to the `Segment Editor` module
2. Click `Add` to create a new segment
3. Select `Threshold`, then click and drag on the image to select grayscale areas
4. Check the selection and click `Apply`
5. Repeat for each object
6. Click `Show 3D` to display the 3D model  
   (You can toggle smoothing via the ▼ icon)
7. Use `Center View` if needed to re-center the display

<img src="images/step3-06-3.PNG" alt="Segment Editor" width="70%">

---

### 💾 3. Export STL Files

1. Switch to the `Segmentations` module
2. Select `Export to files`
3. Export each segment as an individual STL file

<img src="images/step3-07.PNG" alt="STL Export" width="50%">

---

### 🔍 4. View 3D Models

1. Launch 3D Slicer again
2. Switch to `3D only` view mode
3. Go to `Add Data > Choose Files to Add` and select all STL files you exported (you can also drag & drop)
4. Switch to the `Models` module and adjust **color and transparency** for each model
5. Click `Save` to save the scene as an MRML file  
   → You can reopen it later with all settings preserved

---

### 🎨 5. Display Settings & Screenshots

- To change the background to black:  
  `View Controllers > 3D View Controllers > Eye icon > Black background`

- To turn off cube and axis labels:  
  `View Controllers > 3D View Controllers > Eye icon`  
  → Uncheck `3D cube` and `3D axis label`

- To capture a screenshot:
  1. Click the camera icon in the top toolbar
  2. Select `3D View`
  3. Click `Save As` and specify the file name and folder → `OK`

---


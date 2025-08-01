# SegRef3D Tutorial (English)

---

## 🕹️ Basic Controls

- **🔄 Switch images**  
  - Next image: `PageDown`, `F`, or `J`  
  - Previous image: `PageUp`, `R`, or `U`

- **🔍 Zoom in/out**  
  - Zoom in: `E`, `I`, `+`, or `=`  
  - Zoom out: `Q`, `P`, or `-`  
  - (You can also use `Ctrl` + scroll)

- **🧭 Pan (when zoomed)**  
  - Move up: `W`, `O`, or `↑`  
  - Move down: `S`, `L`, or `↓`  
  - Move left: `A`, `K`, or `←`  
  - Move right: `D`, `;`, or `→`  
  - (Alternatively, use scroll or `Shift` + scroll for horizontal panning)

- **✏️ Drawing (Click mode)**  
  - Confirm current drawing: `G` or `H`  
  - Undo last click point: `T` or `Y`

- **↩️ Undo drawing/editing**  
  - `Ctrl + Z` (if implemented separately)


---

## 🔄 Basic Workflow

### 🤖 Segmentation (SAM2)

1. Click `Load Image Folder` to import images
2. Click `Prepare Tracking`
3. Use `Set Box Prompt` to draw a box around the target
4. Navigate to the first frame → Click `Set Tracking Start`
5. Navigate to the last frame → Click `Set Tracking End`
6. Click `Run Tracking` (may take time)
7. Select `Target Object` number, then click `Add to Mask`
8. Use the checkboxes at the bottom to toggle mask visibility

---

### ✏️ Editing (Refinement)

* Draw on the image using mouse or stylus
* Choose `Add` or `Erase` to edit for the selected `Target Object`
* Pen color options: `Gray`, `White`, `Black`
* Drawing modes: `Free`, `Click`, `Click (Snap)`

---

### 💾 Save Mask Data

* Click `Save SVG` to save current mask state
* To resume editing later:

  * Load images with `Load Image Folder`
  * Load saved masks with `Load Mask Folder`

---

### 📏 Calibration (not required for DICOM)

* Input actual line length (mm) and Z spacing (mm)
* Click `Draw Calibration Line` and draw a line on the image

---

### 📐 3D Export

* Click `Export STL per Color` to generate STL files for each object
* View STL files with external software (e.g., 3D Slicer, MeshLab)

---

### 📊 Volume Measurement

* Click `Export Volume CSV` to generate volume measurements per object

---

## 🧩 Advanced Functions

### 🔁 Batch Tracking for Multiple Objects

1. For each object:

   * Define a Box Prompt
   * Set Tracking Start and End
   * Click `Add Object Prompt`
2. After setting all, click `Run Batch Tracking`

---

### 🎚️ Threshold-Based Extraction

* Set `Threshold min` and `max`
* Click `Extract by Threshold` to extract regions
* Assign to object using `Add to Mask`
* Presets available (e.g., CT Soft Tissue)

---

### 🧱 Change Drawing Order (Front/Back)

* Enter object number in `Reorder`
* Use `Bring to Front` or `Send to Back`

---

### 🧹 Remove Small Fragments

* Enter object number and area threshold in `Delete Object`
* Click `Remove Small Parts`

---

### ❌ Delete Masks

* `Delete Object CurrentImg`: Deletes from current image only
* `Delete Object AllImg`: Deletes from all images

---

### 💠 STL Smoothing

* Select `Smooth Mode`
* Choose between `z-interpolation`, `mesh smoothing`, or both

---


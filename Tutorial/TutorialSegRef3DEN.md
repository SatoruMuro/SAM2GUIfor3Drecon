# SegRef3D Tutorial (English)

---

## 🕹️ Basic Controls

- **🔄 Switch images**  
  - Next image: `PageDown`, `F`, or `J`  
  - Previous image: `PageUp`, `R`, or `U`

- **🔍 Zoom in/out**  
  - Zoom in: `E`, `I`, `+`, or `=`  
  - Zoom out: `Q`, `P`, or `-`  
  - You can also use `Ctrl` + scroll

- **🧭 Pan the image when zoomed**  
  - Move up: `W`, `O`, or `↑`  
  - Move down: `S`, `L`, or `↓`  
  - Move left: `A`, `K`, or `←`  
  - Move right: `D`, `;`, or `→`  
  - You can also use scroll, or `Shift` + scroll for horizontal panning

- **✏️ Drawing in Click mode**  
  - Confirm current drawing: `G` or `H`  
  - Undo the last click point: `T` or `Y`

- **↩️ Undo / Redo**  
  - Undo drawing line: `Undo Line`
  - Redo drawing line: `Redo Line`
  - Undo mask edit: `Undo Edit`
  - Redo mask edit: `Redo Edit`
  - Shortcut: `Ctrl + Z` if implemented

---

## 🔄 Basic Workflow

### 🤖 Automatic Segmentation

1. Click `Load Images` to import images.
2. Click `Prepare Tracking` to prepare the tracking process.
3. Use `Set Box Prompt` to define a rectangular region around the target.
4. Navigate to the start image for tracking, then click `Set Tracking Start`.
5. Navigate to the end image for tracking, then click `Set Tracking End`.
6. Click `Run Tracking`.  
   This may take some time depending on the number of images and your computer environment.
7. Select the `Target Object` number, then click `Add to Mask` to register the mask.
8. Use the checkboxes at the bottom of the window to show or hide each object mask.

---

### ✏️ Editing / Refinement

* Draw directly on the image using a mouse or stylus.
* Select the object number to edit using `Target Object`.
* To add the drawn region to the selected object, click `Add to Mask`.
* To remove the drawn region from the selected object, click `Erase from Mask`.
* Select the pen color using `Pen Color`.
* Select the drawing mode using `Draw Mode`.
* Drawing lines can be controlled using `Undo Line`, `Redo Line`, `Clear Lines`, and `Clear All Lines`.
* Mask editing operations can be undone or redone using `Undo Edit` and `Redo Edit`.

---

### 🔁 Transfer Masks Between Objects

* Select the source object using `Target Object`.
* Specify the destination object number using `Transfer To:`.
* This can be used to transfer an existing mask from one object to another when needed.

---

### 💾 Save Mask Data

* Click `Save Masks` to save the current mask data.
* To resume editing later, load the data in the following order:

  * Click `Load Images` to import the image sequence.
  * Click `Load Masks` to load the saved mask data.

---

### 📏 Calibration

* Enter the actual length of the reference line in `Line Length (mm)`.
* Enter the Z-direction interval between images in `Z Interval (mm)`.
* Click `Calibration Line` and draw a reference line on the image.
* After calibration, the scale is applied to distance measurement and 3D export.

---

### 📐 3D Export

* Set `Smooth Level` and `Smooth Mode` as needed.
* Click `Export 3D` to export 3D data.
* Use external software to view the exported 3D data.  
  Examples: 3D Slicer, MeshLab

---

### 📊 Volume Information

* Click `Load VolInfo` to load volume information.
* Click `Show VolInfo` to display volume information.
* Volume calculation reflects the calibration data and Z-direction interval.

---

### 📏 Distance Measurement Between Two Points

* Click `Measurement Line`.
* Click two points on the image to draw a measurement line.
* If calibration has been completed, the actual distance is displayed in millimeters.
* The measurement result is temporarily displayed on the screen.
* Click `Export Measurements` to export the measurement results.

---

## 🧩 Advanced Functions

The following functions are available from `Extensions` in the lower-left area of the window.

---

### 🔁 Batch Tracking for Multiple Objects

1. Select the batch tracking function from `Extensions`.
2. For each object, specify the following:

   * Box Prompt
   * Tracking Start and End
   * `Add Object Prompt`

3. After all target objects have been specified, click `Run Batch Tracking`.

---

### 🎚️ Threshold-Based Extraction

1. Select the threshold extraction function from `Extensions`.
2. Set `Threshold min` and `max`.
3. Click `Extract by Threshold` to extract regions within the specified threshold range.
4. Click `Add to Mask` to add the extracted region to the target object.
5. If preset options are available, you can select presets such as CT Soft Tissue.

---

### 🖍️ RGB Color Extraction

1. Select the RGB color extraction function from `Extensions`.
2. Specify the R/G/B values and tolerance range using `Target RGB` and `±Tol`.
3. Click `Extract by RGB` to extract regions close to the specified color.
4. Use `Pick Color` to click on the image and automatically retrieve RGB values.
5. Click `Add to Mask` to add the extracted region to the target object.

---

### 🧹 Remove Small Mask Fragments

1. Select the small-fragment removal function from `Extensions`.
2. Specify the target object number using `Delete Object`.
3. Enter the area threshold in `Threshold(px^2)`.
4. Click `Remove Small Parts` to remove small mask fragments below the specified area threshold.

---

### ❌ Delete Segmentation Masks

1. Select the mask deletion function from `Extensions`.
2. Click `Delete Object CurrentImg` to delete the target object mask only from the currently displayed image.
3. Click `Delete Object AllImg` to delete the target object mask from all images.

---

## 📝 Notes

* `Reorder`, `Bring to Front`, and `Send to Back` have been removed and are not used in ver.1.2.0.
* In ver.1.2.0, the internal image-processing workflow has been improved, and mask processing has been unified into a raster-based workflow.
* Functions that are not always visible in the main UI are generally available from `Extensions`.

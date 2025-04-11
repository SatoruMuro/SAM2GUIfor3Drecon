
import slicer
import qt
import csv
import os
import numpy as np
from PIL import Image

# =====================
# DICOM/NRRD → JPG 変換
# =====================
def convert_nrrd_to_jpg():
    file_dialog = qt.QFileDialog()
    file_dialog.setFileMode(qt.QFileDialog.Directory)
    output_folder = file_dialog.getExistingDirectory(None, "保存先フォルダを選んでください / Select Output Folder")

    if not output_folder:
        print("❌ 保存先の選択がキャンセルされました / Output folder selection was cancelled.")
        return

    volumeNode = None
    for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLScalarVolumeNode"):
        volumeNode = node
        break

    if volumeNode is None:
        print("❌ 画像データがロードされていません / No image data loaded.")
        return

    displayNode = volumeNode.GetDisplayNode()
    if not displayNode:
        print("❌ 表示ノードが見つかりません / Display node not found.")
        return

    window = displayNode.GetWindow()
    level = displayNode.GetLevel()
    print(f"📊 ウィンドウ: {window}, レベル: {level} / Window: {window}, Level: {level}")

    lower = level - (window / 2)
    upper = level + (window / 2)

    volume_array = slicer.util.arrayFromVolume(volumeNode)
    num_slices = volume_array.shape[0]
    height, width = volume_array.shape[1], volume_array.shape[2]

    print(f"📦 {num_slices} 枚のスライスを検出しました。保存先: {output_folder} / Detected {num_slices} slices. Saving to: {output_folder}")

    for i in range(num_slices):
        slice_data = volume_array[i, :, :]
        slice_data_clipped = np.clip(slice_data, lower, upper)
        slice_data_normalized = ((slice_data_clipped - lower) / (upper - lower) * 255).astype(np.uint8)

        img = Image.fromarray(slice_data_normalized)
        filename = os.path.join(output_folder, f"image{i+1:04d}.jpg")
        img.save(filename, "JPEG")

    print(f"✅ {num_slices} 枚の画像を {width}×{height} 解像度で保存しました / Saved {num_slices} images at resolution {width}×{height} to {output_folder}")

# =====================
# Volume 情報の保存
# =====================
def save_volume_info():
    file_dialog = qt.QFileDialog()
    file_dialog.setAcceptMode(qt.QFileDialog.AcceptSave)
    file_dialog.setNameFilter("CSV Files (*.csv)")
    file_dialog.setDefaultSuffix("csv")
    selected_file = file_dialog.getSaveFileName(None, "Volume情報を保存 / Save Volume Info", "", "CSV Files (*.csv)")

    if selected_file:
        volumeNode = None
        for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLScalarVolumeNode"):
            volumeNode = node
            break

        if volumeNode:
            dims = volumeNode.GetImageData().GetDimensions()
            spacing = volumeNode.GetSpacing()
            origin = volumeNode.GetOrigin()

            with open(selected_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Width", "Height", "Depth"])
                writer.writerow(dims)
                writer.writerow(["X Spacing", "Y Spacing", "Z Spacing"])
                writer.writerow(spacing)
                writer.writerow(["X Origin", "Y Origin", "Z Origin"])
                writer.writerow(origin)

            print(f"✅ Volume情報を保存しました: {selected_file} / Volume info saved to: {selected_file}")
        else:
            print("❌ Volumeデータがロードされていません / No volume data loaded.")
    else:
        print("❌ 保存がキャンセルされました / Save cancelled.")

# =====================
# Volume 情報の読込
# =====================
def load_volume_info():
    file_dialog = qt.QFileDialog()
    file_dialog.setAcceptMode(qt.QFileDialog.AcceptOpen)
    file_dialog.setNameFilter("CSV Files (*.csv)")
    selected_file = file_dialog.getOpenFileName(None, "Volume情報を読み込み / Load Volume Info", "", "CSV Files (*.csv)")

    if selected_file:
        volumeNode = None
        for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLScalarVolumeNode"):
            volumeNode = node
            break

        if volumeNode and os.path.exists(selected_file):
            with open(selected_file, mode="r") as file:
                reader = list(csv.reader(file))
                spacing = list(map(float, reader[3]))
                origin = list(map(float, reader[5]))

                volumeNode.SetSpacing(spacing)
                volumeNode.SetOrigin(origin)
                print(f"✅ Volume情報を適用しました: {selected_file} / Applied volume info from: {selected_file}")
        else:
            print("❌ Volumeが見つからない、またはCSVが存在しません / Volume not found or CSV does not exist.")
    else:
        print("❌ 読み込みがキャンセルされました / Load cancelled.")

# =====================
# ツールバーにボタン追加
# =====================
toolbar = slicer.util.findChildren(name='ModuleToolBar')[0]

# JPG変換ボタン
action = qt.QAction("DICOM/NRRD→JPG", slicer.util.mainWindow())
action.setToolTip("画像をJPEG形式に保存 / Export image as JPEG")
action.triggered.connect(convert_nrrd_to_jpg)
toolbar.addAction(action)

# Volume情報保存ボタン
save_action = qt.QAction("SaveVolumeInf", slicer.util.mainWindow())
save_action.setToolTip("Volume情報をCSVに保存 / Save volume info to CSV")
save_action.triggered.connect(save_volume_info)
toolbar.addAction(save_action)

# Volume情報読込ボタン
load_action = qt.QAction("ApplyVolumeInf", slicer.util.mainWindow())
load_action.setToolTip("CSVからVolume情報を読み込み / Load volume info from CSV")
load_action.triggered.connect(load_volume_info)
toolbar.addAction(load_action)

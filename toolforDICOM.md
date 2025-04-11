## 🧰 3D Slicer用 DICOM処理ツール  
  
3D Slicerのツールバーに以下のボタンを**自動追加**する `.slicerrc.py` スクリプトです：  
  
- 📷 **DICOM/NRRD → JPG**：読み込んだボリュームスライスを、ウィンドウ/レベル設定に従ってJPEG画像として出力  
- 💾 **Volume情報を保存**：ボリュームの寸法・間隔・原点などのメタデータをCSV形式で保存  
- 📂 **Volume情報を読み込み**：保存済みのCSVから情報を読み込んで、現在のボリュームに適用  
  
**医用画像の前処理、データ共有、可視化に便利なツールセットです。**  
  
📎 スクリプトはこちらから入手できます：    
🔗 [`.slicerrc.py`（GitHubリンク）](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/.slicerrc.py)  
  
### 🛠 使用方法：  
1. 上記リンクから `.slicerrc.py` をダウンロード  
2. 以下のフォルダに置きます：  C:\Users\<ユーザー名>  
3. 3D Slicer を再起動  
4. ツールバーに新しい3つのボタンが自動で追加されます  
  
3D Slicer内でのDICOM処理が簡単・スピーディになります！  

  
## 🧰 DICOM Processing Tools for 3D Slicer

This `.slicerrc.py` script **automatically adds buttons** to the 3D Slicer toolbar:

- 📷 **DICOM/NRRD → JPG**: Export volume slices as JPEG images using the current window/level settings.
- 💾 **Save Volume Info**: Save volume metadata (dimensions, spacing, origin) as a CSV file.
- 📂 **Load Volume Info**: Load metadata from a CSV file and apply it to the currently loaded volume.

**A convenient toolset for medical image preprocessing, data sharing, and visualization.**

📎 Download the script here:  
🔗 [`.slicerrc.py` on GitHub](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/.slicerrc.py)

### 🛠 How to use:
1. Download `.slicerrc.py` from the link above.
2. Place it in the following folder: `C:\Users\<YourUsername>`
3. Restart 3D Slicer.
4. Three new buttons will appear in the toolbar automatically.

Enjoy faster and easier DICOM processing inside 3D Slicer!

## 🧰 3D Slicer用 DICOM処理ツール  
  
3D Slicerのツールバーに以下のボタンを**自動追加**する `.slicerrc.py` スクリプトです：  
  
- 📷 **DICOM/NRRD→JPG**：読み込んだボリュームスライスを、ウィンドウ/レベル設定に従ってJPEG画像として出力  
- 💾 **SaveVolumeInf**：ボリュームの寸法・間隔・原点などのメタデータをCSV形式で保存  
- 📂 **ApplyVolumeInf**：保存済みのCSVから情報を読み込んで、現在のボリュームに適用  
  
**医用画像の前処理、データ共有、可視化に便利なツールセットです。**  
  
📎 スクリプトはこちらから入手できます：    
🔗 [`.slicerrc.py`（GitHubリンク）](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/.slicerrc.py)  
  
### 🛠 使用方法：  
1. 上記リンクから `.slicerrc.py` をダウンロードし、ファイル名を確認・変更する（※）  
2. 以下のフォルダに置きます：  C:\Users\<ユーザー名>  
3. 3D Slicer を再起動  
4. ツールバーに新しい3つのボタンが自動で追加されます  
  
3D Slicer内でのDICOM処理が簡単・スピーディになります！  

※ ダウンロード後、ファイル名が `slicerrc.py` などに変わっている場合は、必ず先頭に「.（ドット）」をつけて `.slicerrc.py` に変更してください。  
→ 正しいファイル名でないと、3D Slicer起動時に自動で読み込まれません。  
※ Windowsではドットから始まるファイル名が入力できない場合があります。その場合は、  
- メモ帳で保存時に `"`.slicerrc.py`"`（ダブルクォーテーション付き）と入力  
- または、エクスプローラーでリネームして `.txt` を削除してください。  
  

  
## 🧰 DICOM Processing Tools for 3D Slicer

This `.slicerrc.py` script **automatically adds the following buttons** to the 3D Slicer toolbar:

- 📷 **DICOM/NRRD → JPG**: Exports volume slices as JPEG images based on the current window/level settings.
- 💾 **Save Volume Info**: Saves volume metadata (dimensions, spacing, origin) to a CSV file.
- 📂 **Load Volume Info**: Loads metadata from a CSV file and applies it to the currently loaded volume.

**A convenient toolset for medical image preprocessing, data sharing, and visualization.**

📎 Download the script here:  
🔗 [`.slicerrc.py` on GitHub](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/.slicerrc.py)

### 🛠 How to use:
1. Download the `.slicerrc.py` file from the link above and verify/rename it if needed (see notes below).
2. Place the file in the following folder: `C:\Users\<YourUsername>`
3. Restart 3D Slicer.
4. Three new buttons will automatically appear in the toolbar.

This will enable fast and easy DICOM processing inside 3D Slicer!

---

**Notes:**

- After downloading, the filename may appear as `slicerrc.py` without the leading dot.  
  Be sure to rename it to `.slicerrc.py` (with a dot at the beginning).  
  → Without the correct filename, 3D Slicer will not load the script automatically.

- On Windows, creating a filename starting with a dot can be tricky.  
  If needed:
  - Save the file in Notepad as `"`.slicerrc.py`"` (with double quotes)
  - Or rename it manually in File Explorer and remove any `.txt` extension.


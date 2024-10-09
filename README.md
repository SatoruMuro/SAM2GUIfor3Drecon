# SAM2 GUI for 3D reconstruction

## AI-Powered Segmentation and Interactive Refinement for Labor-Saving 3D Reconstruction  

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/01newmethod.JPG" alt="newmethod" width="80%">

Segment Anything Model 2 (SAM2)を活用した**連続切片（連続断層画像）のセグメンテーションの半自動化ツール**です。組織連続切片、解剖断面、CT、MRI、超音波画像などに応用できます。SAM2による学習不要の自動セグメンテーション（ゼロショットセグメンテーション）で**大まかなセグメンテーション**を行い、それをユーザーが**確認・修正**する、というのが基本的なコンセプトです。SAM2による自動セグメンテーションについては、連続画像（イメージシークエンス）に対応したGUI（グラフィカルユーザーインターフェース）を作成しました（SAM2 GUI for Img Seq）。ユーザーによる確認・修正作業には、Microsoft Powerpointに複数のマクロ（Visual Basic for Applications [VBA]）を導入し、UIとして活用しました。最終的にマスク画像が得られるので、3D再構築はおおむねどのソフトでも可能だと思います。ここではフリーソフトの3D Slicerを用いたやり方を紹介しています。以下の3 Stepに全体の流れをまとめました。Tutorialにやり方を解説していきます。  

This is a **semi-automated tool for segmenting serial sections (sequential tomographic images)** using the Segment Anything Model 2 (SAM2). It can be applied to various types of images, including histological serial sections, anatomical cross-sections, CT, MRI, and ultrasound images. The basic concept involves performing **coarse segmentation** with SAM2's training-free automatic segmentation (zero-shot segmentation), which the user then **reviews and modifies** as needed.A GUI (Graphical User Interface) compatible with image sequences was created for automatic segmentation using SAM2 (SAM2 GUI for Image Sequences). For the user review and modification process, multiple macros (Visual Basic for Applications [VBA]) were incorporated into Microsoft PowerPoint, which serves as the user interface (UI).Finally, the mask images obtained can be used for 3D reconstruction, which should be possible with most software. Here, we introduce a method using the free software 3D Slicer. The overall workflow is summarized in the following 3 steps.The tutorial will explain the procedure in detail.

組織連続切片の場合、セグメンテーションの前に位置合わせが必要です。位置合わせの方法は[こちら](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/RegistrationJP.md)をご参照ください。  

In the case of serial sections of histology, registration is required prior to segmentation. For detailed instructions on the registration process, please refer to [this page](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/RegistrationJP.md).  

## 3 Steps

**Step 1. AI-Powered Segmentation**  
(optional) preparation: [JPG Converter](https://colab.research.google.com/drive/1eMO7cU1i63Z8ftnkuzwoSDXdWUyFzsN2?usp=sharing)  
[SAM2 GUI for Img Seq](https://colab.research.google.com/drive/1At6ZcPM8dEHAVVYvjyuUVjKxUwFKH2cy?usp=sharing)  

**Step 2. Interactive Refinement**  
(optional) preparation: [ColorChanger](https://colab.research.google.com/drive/1Jwlghv5zdJuB8PC-QpPYpB8eOxum_yub?usp=sharing)  
preparation: [Vectorizer Colab](https://colab.research.google.com/drive/1GKhSyR0zwri5OcwivF4DK3HLpuIa8Bad?usp=sharing)  
[Segment Editor PP](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/SegmentEditorPPv1.1.pptm) (with [Graphic2shape](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/graphic2shape_v1.2.exe))  

**Step 3. 3D reconstruction**  
preparation: [Object Mask Splitter](https://colab.research.google.com/drive/1516VL6LmuczVHk0BBdtpaIyGboeYSPXD?usp=sharing)  
[3D slicer](https://www.slicer.org/)  

## Tutorial
### Step 1: AI-Powered Segmentation
まず、連続切片画像（連続断層画像）をjpg形式で用意してください。jpg形式でない場合、何かしらの変換ソフトでjpg形式に変換してください。こちらの[JPG Converter](https://colab.research.google.com/drive/1eMO7cU1i63Z8ftnkuzwoSDXdWUyFzsN2?usp=sharing)もお使いいただけます。  
画像ファイル名は、番号順にソートが可能な名前にしてください（image0001.jpg, image0002.jpgなど）。画像ファイルの大きさは一辺が1000px以下を推奨します。複数の画像ファイルの一括編集にはフリーソフトの[IrfanView](https://www.irfanview.com/)が便利です。  

First, prepare the image sequence (consecutive tomographic images) in JPG format. If they are not in JPG format, convert them using a conversion software. You can also use this [JPG Converter](https://colab.research.google.com/drive/1eMO7cU1i63Z8ftnkuzwoSDXdWUyFzsN2?usp=sharing).
Name the image files in a way that allows them to be sorted in numerical order (e.g., image0001.jpg, image0002.jpg, etc.). It is recommended that the image size does not exceed 1000px on any side. For batch editing multiple image files, the free software [IrfanView](https://www.irfanview.com/) can be convenient.

次に、こちら[SAM2 GUI for Img Seq](https://colab.research.google.com/drive/1At6ZcPM8dEHAVVYvjyuUVjKxUwFKH2cy?usp=sharing)にアクセスしてgoogle colabのノートブックを開いてください（googleのログインが必要）。  
ノートブックが開いたら、ランタイム>すべてのセルを実行（ショートカット：**Ctrl+F9**）によりすべてのセルを実行し、セル[2]の最後に生成された**URL（Running on public URL）をクリック**して開いてください。GUIが新しいタブで開かれます。セル[1]は実行完了までに約5分、セル[2]は5秒程度を要します。GUIが新しいタブで開かれても、colabのノートブックの画面（タブ）は閉じないでください。  

Next, access this [SAM2 GUI for Img Seq](https://colab.research.google.com/drive/1At6ZcPM8dEHAVVYvjyuUVjKxUwFKH2cy?usp=sharing) to open the Google Colab notebook (Google login is required).  
Once the notebook is open, execute all cells by selecting Runtime > Run all (Shortcut: Ctrl+F9). Then, click on the URL generated at the end of Cell [2] (Running on public URL) to open it. The GUI will open in a new tab. Please do not close the Colab notebook screen (tab) even after the GUI has opened in a new tab. It takes about 5 minutes for Cell [1] to complete execution, and approximately 5 seconds for Cell [2].  

GUIを開いたら、以下の手順で操作します。  
1. 画像（複数枚）のアップロード  
2. セグメンテーションの基準として用いる画像の選択  
3. 対象物のセグメンテーション（対象物の左上と右下をそれぞれ指定する）を行い、１つ目の対象物のセグメンテーションを完了する  
4. 次の対象物のセグメンテーションを行い、２つ目の対象物のセグメンテーションを完了する（すべての対象物が完了するまで繰り返す）（一度に扱える対象物は最大20個まで）  
5. すべての対象物のセグメンテーションが完了したら、トラッキングを開始  
6. セグメンテーション結果の確認  
7. 生成されたファイルのダウンロード

Once the GUI is open, follow the steps below:  
1. Upload the images (multiple images).  
2. Select the image to be used as a reference for segmentation.  
3. Perform segmentation of the target object (specify the top-left and bottom-right corners of the target object) to complete the segmentation of the first target object.  
4. Proceed to the segmentation of the next target object, and complete the segmentation of the second target object (repeat until all target objects are completed). You can handle up to 20 target objects at a time.  
5. Once the segmentation of all target objects is complete, start the tracking process.  
6. Confirm the segmentation results.  
7. Download the generated files.  



デモ動画（複数オブジェクト）は[こちら](https://youtu.be/Xz-YpWa89G4)  
A demonstration video can be found [here](https://youtu.be/Xz-YpWa89G4).  
[![YouTubeサムネイル](https://img.youtube.com/vi/Xz-YpWa89G4/hqdefault.jpg)](https://youtu.be/Xz-YpWa89G4)  

デモ動画（一つのオブジェクト）は[こちら](https://youtu.be/tXG23oDyItk)  
A demonstration video can be found [here](https://youtu.be/tXG23oDyItk).  
[![YouTubeサムネイル](https://img.youtube.com/vi/tXG23oDyItk/hqdefault.jpg)](https://youtu.be/tXG23oDyItk)  

生成されるファイルは以下の２種類です。  

**segmented_images**：オリジナル画像とマスク画像の重ね合わせ画像です。確認用やプレゼンテーション用にお使いください。  
**mask_color_images**：マスク画像です。こちらをStep 2で使います。  

The generated files consist of the following two types:  
**segmented_images**: These are the overlay images combining the original image and the mask image. They can be used for confirmation or presentation purposes.  
**mask_color_images**: These are the mask images that will be used in Step 2.  

マスク画像では、セグメンテーションを行った順番に、対象物に対して以下の色ラベルがあてられます（最大20個）。  
In the mask images, color labels are assigned to the segmented objects in the order in which segmentation is performed (up to a maximum of 20 objects). The color labels correspond to the object numbers as follows:  

（R,G,B）: オブジェクト番号  object number  
    (255, 0, 0): 1,     # 赤  Red  
    (0, 0, 255): 2,     # 青  Blue  
    (0, 255, 0): 3,     # 緑  Green  
    (255, 255, 0): 4,   # 黄  Yellow  
    (128, 0, 128): 5,   # 紫  Purple  
    (255, 165, 0): 6,   # オレンジ  Orange  
    (0, 255, 255): 7,   # 水色  Light Blue  
    (173, 255, 47): 8,  # 黄緑  Yellow-Green  
    (128, 128, 128): 9, # グレー  Gray  
    (0, 128, 128): 10,  # 青緑  Teal  
    (255, 192, 203): 11,# ピンク  Pink  
    (255, 20, 147): 12, # ローズ  Rose  
    (0, 128, 0): 13,    # オリーブ  Olive  
    (128, 0, 0): 14,    # マルーン  Maroon  
    (0, 255, 230): 15,  # シアン  Cyan  
    (255, 215, 0): 16,  # ゴールド  Gold  
    (255, 69, 0): 17,   # インディアンレッド  Indian Red  
    (0, 0, 128): 18,    # ネイビーブルー  Navy Blue  
    (220, 20, 60): 19,  # クリムゾンレッド  Crimson Red  
    (128, 128, 0): 20   # オリーブグリーン  Olive Green  
  
### Step 2: Interactive Refinement
Step 2では、Step 1で生成されたセグメンテーションマスク画像（mask_color_images）（PNGファイル）を用います。 

In Step 2, use the segmentation mask images (mask_color_images) generated in Step 1 (in PNG format).  

SAM2 GUIによる自動セグメンテーションを１回だけ行った場合は、マスク画像は１シリーズのみです。  
もし、SAM2 GUIによる自動セグメンテーションを複数回にわけて行った場合、マスク画像を２シリーズ以上取得していることになります。その場合、複数のシリーズ間で異なる対象物に同じ色がついているため、[ColorChanger](https://colab.research.google.com/drive/1Jwlghv5zdJuB8PC-QpPYpB8eOxum_yub?usp=sharing) を用いて色ラベルを変換し、１つの対象物に１つの色が対応するようにしてください。SAM2 GUIによる自動セグメンテーションを１回だけ行った場合は色変換の操作は必要ありません。  

If you have performed automatic segmentation using the SAM2 GUI only once, there will be just one series of mask images.  
However, if you have performed the automatic segmentation multiple times using the SAM2 GUI, you will have obtained more than one series of mask images. In such cases, the same color may be assigned to different objects across multiple series. To ensure that each object is assigned a unique color, use [ColorChanger](https://colab.research.google.com/drive/1Jwlghv5zdJuB8PC-QpPYpB8eOxum_yub?usp=sharing) to convert the color labels. This process is not necessary if the automatic segmentation was done only once.  

セグメンテーションマスク画像（PNGファイル）を、[Vectorizer Colab](https://colab.research.google.com/drive/1GKhSyR0zwri5OcwivF4DK3HLpuIa8Bad?usp=sharing)を用いてベクター形式（SVGファイル）に変換します。  
Colabのノートブックを開いたら、ランタイム>すべてのセルを実行（Ctrl+F9）によりすべてのセルを実行し、セル[2]の最後に生成された「ファイルを選択」ボタンから、マスク画像をアップロードしてください。ベクター変換が行われ、最後にベクター変換後のマスク画像がzipでまとめてダウンロードされます。ベクター変換を行う画像の枚数に応じて所要時間が異なります。  
SVG形式のファイルは、Chromeなどのウェブブラウザで開くことができます。  
変換に失敗する画像が含まれることがあります。変換に失敗したら、その画像だけ再度トライしてください。（変換失敗画像は、Windowsのエクスプローラーでサムネイル画像が全然表示されないこと、Chromeなどで開いてもエラーが出てしまうことにより、変換失敗画像だと判断できます。）  

Convert the segmentation mask images (PNG files) into vector format (SVG files) using [Vectorizer Colab](https://colab.research.google.com/drive/1GKhSyR0zwri5OcwivF4DK3HLpuIa8Bad?usp=sharing).  
Open the Colab notebook and execute all cells by going to Runtime > Run all (Ctrl+F9). At the end of Cell [2], use the "Choose Files" button that appears to upload your mask images. The vector conversion will be performed, and the converted mask images will be downloaded as a zip file. The time required will vary depending on the number of images being converted.  
SVG files can be viewed in web browsers such as Chrome.  
There might be instances where some images fail to convert. If a conversion fails, please try again for that specific image. You can identify a failed conversion if the thumbnail does not display properly in Windows Explorer, or if an error appears when trying to open the image in a browser like Chrome.  

いよいよ、セグメンテーションマスクの確認・修正作業を行います。こちらから[Segment Editor PP](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/SegmentEditorPPv1.1.pptm)と [Graphic2shape](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/graphic2shape_v1.2.exe)をダウンロードしてください。    
Segment Editor PPのマクロ有効パワーポイントファイル（pptm）を開いて下さい。マクロが無効になっている場合はマクロを許可し有効にしてください。  
作業にはタッチペン、ペンタブレット等の使用を推奨しますが、マウス操作でも可能です。  

Now, we will proceed with the reviewing and modifying of the segmentation mask. Please download [Segment Editor PP](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/SegmentEditorPPv1.1.pptm) and [Graphic2shape](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/graphic2shape_v1.2.exe) from the provided links.  
Open the Segment Editor PP macro-enabled PowerPoint file (.pptm). If macros are disabled, please allow and enable them.  
We recommend using a stylus pen or pen tablet for this task, but mouse operation is also possible.  
  
Segment Editor PPは９個のマクロを搭載しています。  
**AaAddImages**：連続断層画像の画像ファイルを配置します。（フォルダ選択）  
**AbAddMasks**：ベクター変換後のマスク画像（SVG形式）を連続断層画像の上に重ねます。（ファイル選択）  
**AcDeleteBlackShapesWith70PercentTransparent**：マスク画像に含まれていた余分な黒背景を削除し、マスクを70%透過にします。  
**BaSelectShapeAndRecord**：選択中のマスクを記憶し編集可能な状態にします。  
**BbCutimageWithPreviousShapeAndApplyColor**：フリーフォームや曲線ツールで描いた曲線をもとに、マスクの範囲を削ります（減算）。  
**BcMergeWithPreviousShapeAndApplyColor**：フリーフォームや曲線ツールで描いた曲線をもとに、マスクの範囲を広げます（加算）。  
**CaFinalizeMasks**：背景の連続断層画像を非表示にし、黒背景のマスク画像にします。  
**CbExportToPDF**：PDFファイルとして出力します。  
**CcReturnToMaskEditing**：マスクを編集する状態に戻します。  

Segment Editor PP includes nine macros:  
**AaAddImages**: Places the image files of serial tomographic images. (Folder selection)  
**AbAddMasks**: Overlays the vector-converted mask images (in SVG format) onto the serial tomographic images. (File selection)  
**AcDeleteBlackShapesWith70PercentTransparent**: Removes any unnecessary black backgrounds included in the mask image and makes the mask 70% transparent.  
**BaSelectShapeAndRecord**: Saves the selected mask, making it editable.  
**BbCutImageWithPreviousShapeAndApplyColor**: Trims the mask area based on freeform or curve-drawn lines (subtraction).  
**BcMergeWithPreviousShapeAndApplyColor**: Expands the mask area based on freeform or curve-drawn lines (addition).  
**CaFinalizeMasks**: Hides the serial tomographic background images, leaving the mask image with a black background.  
**CbExportToPDF**: Exports the file as a PDF.  
**CcReturnToMaskEditing**: Returns the mask to an editable state.  

マクロは３つずつのグループにわかれており、Aグループは編集作業前のデータの入力、Bグループは編集作業、Cグループは編集後の出力に用います。  

The macros are divided into three groups:  
Group A is used for data input before editing tasks.  
Group B is used for editing tasks.  
Group C is used for output after editing.  

最初にやるべきことが２つあります。１）スライドのサイズの調整と、２）クイックアクセスツールバーへのマクロの配置です。  
１）スライドのサイズの調整：連続断層画像のピクセルサイズのアスペクト比（幅：高さ）をファイルのプロパティ等で確認し、スライドのアスペクト比をそれに合わせてください。幅と高さの比率が同じになれば大丈夫です。  
２）クイックアクセスツールバーへのマクロの配置：マクロのBグループをクイックアクセスツールバーの最初の３つに配置してください。クイックアクセスツールバーにあるコマンドは「Alt＋数字」のショートカットが有効になります。（数字は配置されている順番）  

There are two things you should do first:  
1) Adjust the slide size and 2) Add the macros to the Quick Access Toolbar.  
1) Adjust the slide size: Check the aspect ratio (width: height) of the pixel size of the serial tomographic images in the file properties or other relevant information, and adjust the slide's aspect ratio to match. As long as the width and height ratio are the same, it will be fine.  
2) Add the macros to the Quick Access Toolbar: Place the macros from Group B in the first three slots of the Quick Access Toolbar. Commands placed in the Quick Access Toolbar can be accessed using the "Alt + number" shortcuts, with the number corresponding to their position.  

続いて、マクロAグループを使ってデータの入力です。マクロAa、Abを使って、連続断層画像とマスク画像を配置します。  
マクロAbで配置したマスク画像を編集可能にするために、[Graphic2shape](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/graphic2shape_v1.2.exe)を用いて、グラフィックス形式から図形に変換します。Graphic2shapeのexeファイルを起動し、メッセージボックスの指示通りに操作してください。  
図形に変換できたら、マクロAcを使って、編集前の準備完了です。  

Next, we will input the data using the Group A macros. Use macros Aa and Ab to place the serial tomographic images and the mask images.  
To make the mask images placed with macro Ab editable, use Graphic2shape to convert the graphics format into shapes. Launch the Graphic2shape executable file and follow the instructions in the message box.  
Once the conversion to shapes is complete, use macro Ac to finish preparing for editing.  

続いて、セグメンテーションマスクの確認・編集作業です。  
作業はタッチペンやペンタブレットを用いて、右手にタッチペン（またはマウス）、左手でキーボード操作、を推奨します。キーボード操作には、[Windows Power Toys](https://github.com/microsoft/PowerToys/releases/tag/v0.85.0)のKeyboard Managerの「キーの再マップ」を使って、以下のような配置で作業するのがおすすめです。  

Next is the verification and editing of the segmentation mask.  
It is recommended to use a stylus pen or pen tablet for the task, with the stylus (or mouse) in your right hand and the keyboard in your left hand for keyboard operations. For keyboard operations, it is recommended to use the "Key Remapping" feature in Keyboard Manager from [Windows Power Toys](https://github.com/microsoft/PowerToys/releases/tag/v0.85.0), setting up the keys in the following layout for more efficient work.  

![Key Remapping](images/KeyRemapping.jpg)

作業としては、PgUpとPgDnでスライドを行き来し、セグメンテーション結果を確認し、必要があれば編集します。特定のマスクを選択しながら「Ctrl＋マウスのスクロール」で表示の拡大縮小ができます。マクロのBグループと、タッチペンでのフリーフォーム入力（マウス操作の場合は曲線ツールがおすすめ）を駆使しながら、マスクの輪郭を微修正していきます。  

In this task, use PgUp and PgDn to navigate between slides and review the segmentation results, editing them as needed. You can zoom in and out while selecting a specific mask by holding Ctrl and using the mouse scroll wheel. Utilize the macros from Group B along with freeform input using the stylus (or the curve tool if using a mouse) to make fine adjustments to the mask contours.  

全てのセグメンテーションマスクの確認・修正が完了したら、マクロCグループを使って、修正後のマスクカラー画像をPDF形式で出力します。  

Once the reviewing and modifying  of all segmentation masks are complete, use the Group C macros to export the corrected mask color images in PDF format.  

デモ動画は[こちら](https://youtu.be/HToh0SFPtZw)  
A demonstration video can be found [here](https://youtu.be/HToh0SFPtZw).  
[![YouTubeサムネイル](https://img.youtube.com/vi/HToh0SFPtZw/hqdefault.jpg)](https://youtu.be/HToh0SFPtZw)  

### Step 3: 3D reconstruction  

ここでは、フリーソフトの[3D slicer](https://www.slicer.org/)を用いたやりかたを紹介します。3D slicerのダウンロードが必要です。  
また、セグメンテーションを行っている連続断層画像における実測1mmあたりのpxサイズ（px/mm）を求めておいてください。画像中にスケールが写しておいたり、標本サイズを実測しておくことで、px/mmを求めることができます。  

セグメンテーションした対象物が複数の場合、マスクカラー画像をオブジェクトごとに分割する必要があります。Step 2で出力したマスクカラーのPDFファイルと、もとの連続断層画像ファイル１つ（サイズを参照するために用いる）を用意して、[Object Mask Splitter](https://colab.research.google.com/drive/1516VL6LmuczVHk0BBdtpaIyGboeYSPXD?usp=sharing)を用いてオブジェクトごとのマスク画像シリーズを取得してください。  
セグメンテーションした対象物が一つの場合はこの作業は必要ありません。  

続いて、3D slicerでの作業です。3D slicerを立ち上げて、画面上のツールバーから、表示をconventionalにしておきます。  
Add data > Choose Directory to Addでマスク画像のフォルダを選択してください。マスク画像は、オブジェクトごとに分割されたものです。  
Volumes > Volume Informationの画面に行き、Image spacingのz軸の値を修正します（左からx軸、ｙ軸、ｚ軸の順に並んでいます）。z軸のImage spacingには、（画像のpx/mm）×（切片の間隔mm）の値を入力してください。x軸、y軸のImage spacingは1mmのままでよいです。入力値を変えると断層画像の表示がずれることがありますが、Center Viewボタンで画像を画面の中央に配置できます。  

Segment Editorの画面に行き、Addボタンを押します。Threshholdボタンを押して、選択範囲を確認し、Applyを押します。  
Show 3D ボタンを押します。右側の▼を展開すると、smoothingの有り無しを設定できます。  
3Dの構築像を確認します。Center Viewボタンでオブジェクトを画面の中央に配置できます。  
Show 3Dボタンの右にある右矢印ボタン（→）の右にある▼を展開し、Export to filesを選択します。出力先のフォルダを指定して、Exportを押します。  

上記の手順で、各構造物ごとにSTLファイルを作成します。一つのフォルダにまとめておくと便利です。  
全ての構造物のSTLファイルを取得できたら、それらを3D slicerで開き、観察します。改めて3D slicerを立ち上げてください。

今度は、表示を3D onlyにしておきます。  
Add data > Choose Files to Addで作成したSTLファイルをすべて選択します。  
Modelsの画面に行き、各Nodeの色と透明度を変更します。  
SaveでMRML Sceneとして保存しておけば、また同じ状態を開くことができます。  

以下、表示の設定方法やスクリーンショットの取得方法について説明します。  
3D像の背景を黒にするには、View controllers > 3D View Controllersの眼のマーク> Black background。
cubeとlabelの表示をオフにするには、View controllers > 3D View Controllersの眼のマーク>3D cubeと3D axis labelのチェックを外す。
スクリーンショットの取得は、上のツールバーのカメラのマーク>３DViewを選択して、Save Asで保存先のフォルダとファイル名を指定>OKです。

デモ動画は[こちら](https://youtu.be/CLrHR_u2Ru0)  
A demonstration video can be found [here](https://youtu.be/CLrHR_u2Ru0).  
[![YouTubeサムネイル](https://img.youtube.com/vi/CLrHR_u2Ru0/hqdefault.jpg)](https://youtu.be/CLrHR_u2Ru0)  
  
※Tutorialは作成途中です。  
*This tutorial is currently in progress.

## License
The code for the JPG Converter, SAM2 GUI for Img Seq, ColorChanger, Vectorizer Colab, Segment Editor PP, Graphic2shape, and Object Mask Splitter is licensed under the [Apache 2.0 License](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/LICENSE).

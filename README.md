# SAM2 GUI for 3D reconstruction

AI-Powered Segmentation and Interactive Refinement for Labor-Saving 3D Reconstruction  

Segment Anything Model 2 (SAM2)を活用した**連続切片（連続断層画像）のセグメンテーションの半自動化ツール**です。  
SAM2による学習不要の自動セグメンテーション（ゼロショットセグメンテーション）で**大まかなセグメンテーション**を行い、それをユーザーが**確認・修正**する、というのが基本的なコンセプトです。SAM2による自動セグメンテーションについては、連続画像（イメージシークエンス）に対応したGUI（グラフィカルユーザーインターフェース）を作成しました（SAM2 GUI for Img Seq）。ユーザーによる確認・修正作業には、Microsoft Powerpointに複数のマクロ（Visual Basic for Applications [VBA]）を導入し、UIとして活用しました。最終的にマスク画像が得られるので、3D再構築はおおむねどのソフトでも可能だと思います。ここではフリーソフトの3D Slicerを用いたやり方を紹介しています。  
以下の3 Stepに全体の流れをまとめました。Tutorialにやり方を解説していきます。  

This is a **semi-automated tool for segmenting serial sections (sequential tomographic images)** using the Segment Anything Model 2 (SAM2).  
The basic concept involves performing **coarse segmentation** with SAM2's training-free automatic segmentation (zero-shot segmentation), which the user then **reviews and modifies** as needed.A GUI (Graphical User Interface) compatible with image sequences was created for automatic segmentation using SAM2 (SAM2 GUI for Image Sequences).  
For the user review and modification process, multiple macros (Visual Basic for Applications [VBA]) were incorporated into Microsoft PowerPoint, which serves as the user interface (UI).Finally, the mask images obtained can be used for 3D reconstruction, which should be possible with most software. Here, we introduce a method using the free software 3D Slicer.  
The overall workflow is summarized in the following 3 steps.The tutorial will explain the procedure in detail.

## 3 Steps

**Step 1. AI-Powered Segmentation**  
[SAM2 GUI for Img Seq](https://colab.research.google.com/drive/1At6ZcPM8dEHAVVYvjyuUVjKxUwFKH2cy?usp=sharing)  
(optional) preparation: [JPG Converter](https://colab.research.google.com/drive/1eMO7cU1i63Z8ftnkuzwoSDXdWUyFzsN2?usp=sharing)

**Step 2. Interactive Refinement**  
[Segment Editor PP](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/SegmentEditorPPv1.1.pptm) (with [Graphic2shape](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/graphic2shape_v1.2.exe))  
(optional) preparation: [ColorChanger](https://colab.research.google.com/drive/1Jwlghv5zdJuB8PC-QpPYpB8eOxum_yub?usp=sharing)  
preparation: [Vectorizer Colab](https://colab.research.google.com/drive/1GKhSyR0zwri5OcwivF4DK3HLpuIa8Bad?usp=sharing)  

**Step 3. 3D reconstruction**  
[3D slicer](https://www.slicer.org/)  
preparation: [Object Mask Splitter](https://colab.research.google.com/drive/1r-Br00ZOcABH_HbSnZ16RnKf256pRIq3?usp=sharing)  

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



デモ動画は[こちら](https://youtu.be/Xz-YpWa89G4)  
A demonstration video can be found [here](https://youtu.be/Xz-YpWa89G4).  
[![YouTubeサムネイル](https://img.youtube.com/vi/Xz-YpWa89G4/hqdefault.jpg)](https://youtu.be/Xz-YpWa89G4)  

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
  
  
※Tutorialは作成途中です。  
*This tutorial is currently in progress.

## License

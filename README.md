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

1. [SAM2 GUI for Img Seq](https://colab.research.google.com/drive/1At6ZcPM8dEHAVVYvjyuUVjKxUwFKH2cy?usp=sharing)  
(optional) preparation: [JPG Converter](https://colab.research.google.com/drive/1eMO7cU1i63Z8ftnkuzwoSDXdWUyFzsN2?usp=sharing)

2. [Segment Editor PP](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/SegmentEditorPPv1.1.pptm) (with [Graphic2shape](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/graphic2shape_v1.2.exe))  
(optional) preparation: [ColorChanger](https://colab.research.google.com/drive/1Jwlghv5zdJuB8PC-QpPYpB8eOxum_yub?usp=sharing)  
preparation: [Vectorizer Colab](https://colab.research.google.com/drive/1GKhSyR0zwri5OcwivF4DK3HLpuIa8Bad?usp=sharing)  

3. 3D reconstruction using 3D slicer  
preparation: [Object Mask Splitter](https://colab.research.google.com/drive/1r-Br00ZOcABH_HbSnZ16RnKf256pRIq3?usp=sharing)  

## Tutorial
### Step 1: AI-Powered Segmentation
まず、連続切片画像（連続断層画像）をjpg形式で用意してください。jpg形式でない場合、何かしらの変換ソフトでjpg形式に変換してください。こちのJPG Converterもお使いいただけます。[JPG Converter](https://colab.research.google.com/drive/1eMO7cU1i63Z8ftnkuzwoSDXdWUyFzsN2?usp=sharing)  
画像ファイル名は、番号順にソートが可能な名前にしてください（image0001.jpg, image0002.jpgなど）。画像ファイルの大きさは一辺が1000px以下を推奨します。

次に、こちらにアクセスしてgoogle colabのノートブックを開いてください（googleのログインが必要）。  
[SAM2 GUI for Img Seq](https://colab.research.google.com/drive/1At6ZcPM8dEHAVVYvjyuUVjKxUwFKH2cy?usp=sharing)  
ノートブックが開いたら、ランタイム>すべてのセルを実行（ショートカット：**Ctrl+F9**）によりすべてのセルを実行し、セル[2]の最後に生成された**URL（Running on public URL）をクリック**して開いてください。GUIが新しいタブで開かれます。セル[1]は実行完了までに約5分、セル[2]は5秒程度を要します。GUIが新しいタブで開かれても、colabのノートブックの画面（タブ）は閉じないでください。

GUIを開いたら、以下の手順で操作します。  
1. 画像（複数枚）のアップロード  
2. セグメンテーションの基準として用いる画像の選択  
3. 対象物のセグメンテーション（対象物の左上と右下をそれぞれ指定する）を行い、１つ目の対象物のセグメンテーションを完了する  
4. 次の対象物のセグメンテーションを行い、２つ目の対象物のセグメンテーションを完了する（すべての対象物が完了するまで繰り返す）（一度に扱える対象物は最大20個まで）  
5. すべての対象物のセグメンテーションが完了したら、トラッキングを開始  
6. セグメンテーション結果の確認  
7. 生成されたファイルのダウンロード  

デモ動画は[こちら](https://youtu.be/Xz-YpWa89G4)  
[![YouTubeサムネイル](https://img.youtube.com/vi/Xz-YpWa89G4/hqdefault.jpg)](https://youtu.be/Xz-YpWa89G4)



## License

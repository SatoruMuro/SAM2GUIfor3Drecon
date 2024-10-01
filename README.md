# SAM2 GUI for 3D reconstruction

AI-Powered Segmentation and Interactive Refinement for Labor-Saving 3D Reconstruction  

Segment Anything Model 2 (SAM2)を活用した連続切片（連続断層画像）のセグメンテーションの半自動化ツールです。  
SAM2による学習不要の自動セグメンテーション（ゼロショットセグメンテーション）で大まかなセグメンテーションを行い、それをユーザーが確認・修正する、というのが基本的なコンセプトです。SAM2による自動セグメンテーションについては、連続画像（イメージシークエンス）に対応したGUI（グラフィカルユーザーインターフェース）を作成しました（SAM2 GUI for Img Seq）。ユーザーによる確認・修正作業には、Microsoft Powerpointに複数のマクロ（Visual Basic for Applications [VBA]）を導入し、UIとして活用しました。最終的にマスク画像が得られるので、3D再構築はおおむねどのソフトでも可能だと思います。ここではフリーソフトの3D Slicerを用いたやり方を紹介しています。  
以下の3 Stepに全体の流れをまとめました。Tutorialにやり方を解説していきます。  

This is a semi-automated tool for segmenting serial sections (sequential tomographic images) using the Segment Anything Model 2 (SAM2).  
The basic concept involves performing coarse segmentation with SAM2's training-free automatic segmentation (zero-shot segmentation), which the user then reviews and modifies as needed.A GUI (Graphical User Interface) compatible with image sequences was created for automatic segmentation using SAM2 (SAM2 GUI for Image Sequences).  
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

## License

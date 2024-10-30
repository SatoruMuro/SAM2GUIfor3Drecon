組織連続切片の場合、セグメンテーションの前に位置合わせ（Registration）が必要になります。  
ここでは、Image Jのプラグインである[MultiStackReg](https://github.com/miura/MultiStackRegistration)を用いた位置合わせの方法をご紹介します。  

In the case of serial sections of histology, registration is required prior to segmentation.  
Here, I introduce a method for registration using [MultiStackReg](https://github.com/miura/MultiStackRegistration), a plugin for ImageJ.  

## 操作デモ動画  Demo Videos
**ImageJ/Fiji Tutorial: Registration (Alignment) of Histological Serial Section using MultiStackReg (YouTube)** 
<a href="https://youtu.be/bWF2HW5yjOI">
  <img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/watchvideoicon1.png" alt="Open in YouTube" width="100">
</a>  

**ImageJ/Fiji  Tutorial: How to Easily Crop an Image Sequence (YouTube)** 
<a href="https://youtu.be/Rx8TdUN40ig">
  <img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/watchvideoicon1.png" alt="Open in YouTube" width="100">
</a>  

## Fijiのダウンロード  Downloading Fiji  
Fijiは、ImageJに最初から色々なプラグインが入っているソフトです。[こちら](https://fiji.sc/)からダウンロードしてください。  
ダウンロードしたファイルを解凍して得られた「Fiji.app」というフォルダをCドライブ直下においてください。フォルダ内の「ImageJ-win64.exe」（Windowsの場合のファイル名）というファイルでFijiが起動します。タスクバー等にピン止めしておくと良いでしょう。  

Fiji is a software package that includes various plugins pre-installed in ImageJ. You can download it from [here](https://fiji.sc/).  
After downloading, unzip the file and place the resulting “Fiji.app” folder directly under the C drive. You can launch Fiji by opening the file named “ImageJ-win64.exe” (the file name for Windows) within the folder. It’s recommended to pin this file to the taskbar for easy access.  

## MultiStackRegとTurboRegのインストール　Installation of MultiStackReg and TurboReg

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/MultiStackRegInstall.png" alt="インストール" width="70%">

Fijiを起動し、Help > Update... を選択します。少し待ってImageJ Updaterというウィンドウが開いたら、Manage Update Sitesを選択してください。Searchの検索窓に「multistackreg」と入力して出てきたMultiStackRegにチェックを付けます。Apply and Close、Apply Changesを押して完了です。  

MultiStackRegの機能には、TurboRegという別のプラグインも必要なので、TurboRegもインストールする必要があります。TurboRegは、「BIG-EPFL」という名前のパッケージに含まれていますので、上記と同様の方法で検索窓に「BIG-EPFL」と入力して探し出し、これをインストールします。

Fijiを一度閉じて、もう一度立ち上げるとインストールしたプラグインが反映されます。  
Plugins > Registration の中に、MultiStackRegとTurboRegが入っていることを確認してください。  

Launch Fiji, and select Help > Update.... After a short wait, a window titled “ImageJ Updater” will open. Select “Manage Update Sites”. In the Search bar, type “multistackreg,” and check the box for “MultiStackReg” once it appears. Click Apply and Close, then Apply Changes to complete the process.  

The functionality of MultiStackReg requires an additional plugin called “TurboReg”, which is included in a package named “BIG-EPFL”. Using the same method as above, type “BIG-EPFL” into the Search bar, locate the package, and install it.  

Afterward, close Fiji and restart it to ensure the newly installed plugins are loaded.  
Go to Plugins > Registration to confirm that both MultiStackReg and TurboReg are available.  



## 位置合わせの操作手順　Procedure for Registration

位置合わせを行う連続切片の画像を一つのフォルダにまとめておいてください。画像のファイル名は番号でソート可能なものにしておいてください（image0001, image0002...など）。  
Fijiを起動し、File > Import > Image Sequence... で連続切片をインポートします。Import Image Sequenceのウィンドウが開いたら、Brouseで連続切片画像が入っているフォルダを選択します。Countに表示される画像の枚数を確認し、Sorg names numericallyにチェックを付けて、OKを押します。  

MultiStackRegはカラー画像をそのまま扱うことはできないので、画像をRGBそれぞれのチャンネルに分割します。Image > Color > Split Channels により、色分割すると、フォルダ名の後に (red) (green) (blue) がそれぞれ名前の最後についた３つの画像群（Image Stackといいます）に分割されます。  

Please gather all the images of the serial sections that require registration into a single folder. Ensure that the file names are numerically sortable, such as image0001, image0002, and so on.  
Launch Fiji, then go to File > Import > Image Sequence... to import the serial sections. In the Import Image Sequence window, select the folder containing the serial section images by clicking Browse. Confirm the number of images displayed under Count, check the box for Sort names numerically, and then click OK.  

Since MultiStackReg cannot directly process color images, you need to split the image into separate RGB channels. To do this, go to Image > Color > Split Channels. This will split the color channels into three image stacks, each labeled with (red), (green), and (blue) appended to the folder name.  

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/MultiStackReg.png" alt="インストール" width="70%">

Plugins > Registration > MultiStackReg を選択し、MultiStackRegウィンドウを開きます。Stack 1の欄で位置合わせを行うスタックを選択します。どれでも良いですが、ここでは (blue) のスタックにしましょう。Action 1は Align （位置合わせを行うということ）、TransformationはRigid Bodyを選択してください。Transformationの種類の説明は以下です。  

Translation: 平行移動のみで画像を位置合わせ。  
Rigid Body: 回転と平行移動のみで画像を位置合わせ。  
Scaled Rotation: 回転に加えて拡大縮小も行う。  
Affine: 平行移動、回転、拡大縮小に加え、歪み（せん断）も含む複雑な変換。  

下から２番目のSave Transformation Fileにチェックをつけて、OKを押します。Save transformations atというウィンドウが開くので、保存場所を指定してください。ファイル名は変更しても大丈夫です（デフォルトはTransformationMatrices.txt）。位置合わせが実行されるので、完了するまで待ちます。完了したら、 (blue) のスタックをスクロールして見てみましょう。位置合わせされています。  

今度は、残りの２つのスタックに、 (blue) で行った位置合わせ情報（Transformation File）を適応して、位置合わせを行います。先ほどと同じようにMultiStackRegウィンドウを開き、Stack 1の欄で今度は (green) を選択します。そして、Action 1で、Load Transformation Fileを選択し、OKを押します。今度はSave Transformation Fileにチェックを付ける必要はありません。OKを押すとLoad transformation fileのウィンドウが開くので、先ほど作成された位置合わせ情報のファイル（TransformationMatrices.txtなど）を選択して開くを押します。(green) の位置合わせが実行されます。  
同様に、 (red) のスタックに対しても、同じ位置合わせ情報のファイルを適応して位置合わせを行ってください。 

Go to Plugins > Registration > MultiStackReg to open the MultiStackReg window. In the Stack 1 field, select the stack you want to register. Any stack is fine, but let's choose the (blue) stack here. For Action 1, select Align (which means to perform alignment), and for Transformation, choose Rigid Body. The different types of Transformation are explained below:  

Translation: Aligns the images using translation only.  
Rigid Body: Aligns the images using rotation and translation only.  
Scaled Rotation: Includes scaling along with rotation.  
Affine: A more complex transformation that includes translation, rotation, scaling, and shearing.  

Check the box for Save Transformation File, which is the second from the bottom, and then click OK. A window labeled Save transformations at will open, allowing you to specify the save location. You can change the file name if desired (the default is TransformationMatrices.txt). The registration process will begin, so please wait until it completes. Once finished, scroll through the (blue) stack to confirm that it is aligned.  

Next, apply the alignment information (Transformation File) from the (blue) stack to the remaining two stacks. Open the MultiStackReg window again, and this time select the (green) stack in the Stack 1 field. For Action 1, choose Load Transformation File, and click OK. There is no need to check Save Transformation File this time. Clicking OK will open the Load transformation file window. Select the previously saved transformation file (such as TransformationMatrices.txt) and click Open to apply it. The registration for the (green) stack will now be executed.  
Repeat this process for the (red) stack, using the same transformation file to complete its registration.  

これで、色チャンネルで分割した３つのスタックすべてで位置合わせが完了しました。最後に、これらの３つのスタックを結合し、カラー画像に戻します。  
Image > Color > Merge Channels を選択し、Merge Channelsのウィンドウを開きます。C1(red), C2(green), C3(blue)の欄で、それぞれ (red) (green) (blue) のスタックを選択してください。デフォルトでチェックが入っているCreate compositeのチェックを外し、Keep source imagesにチェックを付け、OKを押します。RGBという名前のスタックとして、位置合わせ済みのカラー画像が生成されます。  

File > Save As > Image Sequence... で保存のウィンドウを開き、Browseで保存先のフォルダを指定し、Formatでファイル形式（JPEGなど）を、Nameでファイル名（「image」など）を指定します。Star Atは1にすると良いでしょう。Digitsは3か4ぐらいが妥当でしょう。OKを押して保存します。  

位置合わせ完了です。お疲れ様でした！

With this, the alignment of all three stacks, split by color channels, is complete. Finally, you will merge these three stacks back into a single color image.  
Go to Image > Color > Merge Channels to open the Merge Channels window. In the fields C1 (red), C2 (green), and C3 (blue), select the corresponding stacks: (red), (green), and (blue). Uncheck Create composite (checked by default), check Keep source images, and click OK. An aligned color image will be generated as a stack labeled RGB.  

To save the image sequence, go to File > Save As > Image Sequence.... In the save window, select the destination folder by clicking Browse, specify the file format (e.g., JPEG) under Format, and choose a file name (e.g., "image") under Name. Set Start At to 1, and for Digits, 3 or 4 is recommended. Click OK to save.  

Registration is now complete. Well done!  

## MultiStackRegの研究での使用について　Regarding the use of MultiStackReg in research  
MultiStackRegに基づく結果を発表または公開する場合は、必ず引用または謝辞を含める必要があります。詳細は[こちら](https://github.com/miura/MultiStackRegistration)をご参照ください。  

If you plan to present or publish results based on MultiStackReg, you must include a citation or acknowledgment. For more details, please refer to [this page](https://github.com/miura/MultiStackRegistration).






組織連続切片の場合、セグメンテーションの前に位置合わせ（Registration）が必要になります。  
ここでは、Image JのプラグインであるMultiStackRegを用いた位置合わせの方法をご紹介します。  

## Fijiのダウンロード  
Fijiは、ImageJに最初から色々なプラグインが入っているソフトです。[こちら](https://fiji.sc/)からダウンロードしてください。  
ダウンロードしたファイルを解凍して得られた「Fiji.app」というフォルダをCドライブ直下においてください。フォルダ内の「ImageJ-win64.exe」（Windowsの場合のファイル名）というファイルでFijiが起動します。タスクバー等にピン止めしておくと良いでしょう。  
## MultiStackRegとTurboRegのインストール

![インストール](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/MultiStackRegInstall.png)

Fijiを起動し、Help > Update... を選択します。少し待ってImageJ Updaterというウィンドウが開いたら、Manage Update Sitesを選択してください。Searchの検索窓に「multistackreg」と入力して出てきたMultiStackRegにチェックを付けます。Apply and Close、Apply Changesを押して完了です。  

MultiStackRegの機能には、TurboRegという別のプラグインも必要なので、TurboRegもインストールする必要があります。TurboRegは、「BIG-EPFL」という名前のパッケージに含まれていますので、上記と同様の方法で検索窓に「BIG-EPFL」と入力して探し出し、これをインストールします。

Fijiを一度閉じて、もう一度立ち上げるとインストールしたプラグインが反映されます。  
Plugins > Registration の中に、MultiStackRegとTurboRegが入っていることを確認してください。  


## 位置合わせの操作手順
位置合わせを行う連続切片の画像を一つのフォルダにまとめておいてください。画像のファイル名は番号でソート可能なものにしておいてください（image0001, image0002...など）。  
Fijiを起動し、File > Import > Image Sequence... で連続切片をインポートします。Import Image Sequenceのウィンドウが開いたら、Brouseで連続切片画像が入っているフォルダを選択します。Countに表示される画像の枚数を確認し、Sorg names numericallyにチェックを付けて、OKを押します。  

MultiStackRegはカラー画像をそのまま扱うことはできないので、画像をRGBそれぞれのチャンネルに分割します。Image > Color > Split Channels により、色分割すると、フォルダ名の後に (red) (green) (blue) がそれぞれ名前の最後についた３つの画像群（Image Stackといいます）に分割されます。  

（画像）

Plugins > Registration > MultiStackReg を選択し、MultiStackRegウィンドウを開きます。Stack 1の欄で位置合わせを行うスタックを選択します。どれでも良いですが、ここでは (blue) のスタックにしましょう。Action 1は Align （位置合わせを行うということ）、下から２番目のSave Transformation Fileにチェックをつけて、OKを押します。Save transformations atというウィンドウが開くので、保存場所を指定してください。ファイル名は変更しても大丈夫です（デフォルトはTransformationMatrices.txt）。位置合わせが実行されるので、完了するまで待ちます。完了したら、 (blue) のスタックをスクロールして見てみましょう。位置合わせされています。  

今度は、残りの２つのスタックに、 (blue) で行った位置合わせ情報（Transformation File）を適応して、位置合わせを行います。先ほどと同じようにMultiStackRegウィンドウを開き、Stack 1の欄で今度は (green) を選択します。そして、Action 1で、Load Transformation Fileを選択し、OKを押します。今度はSave Transformation Fileにチェックを付ける必要はありません。OKを押すとLoad transformation fileのウィンドウが開くので、先ほど作成された位置合わせ情報のファイル（TransformationMatrices.txtなど）を選択して開くを押します。(green) の位置合わせが実行されます。  
同様に、 (red) のスタックに対しても、同じ位置合わせ情報のファイルを適応して位置合わせを行ってください。  

これで、色チャンネルで分割した３つのスタックすべてで位置合わせが完了しました。最後に、これらの３つのスタックを結合し、カラー画像に戻します。  
Image > Color > Merge Channels を選択し、Merge Channelsのウィンドウを開きます。C1(red), C2(green), C3(blue)の欄で、それぞれ (red) (green) (blue) のスタックを選択してください。デフォルトでチェックが入っているCreate compositeのチェックを外し、Keep source imagesにチェックを付け、OKを押します。RGBという名前のスタックとして、位置合わせ済みのカラー画像が生成されます。  

File > Save As > Image Sequence... で保存のウィンドウを開き、Browseで保存先のフォルダを指定し、Formatでファイル形式（JPEGなど）を、Nameでファイル名（「image」など）を指定します。Star Atは1にすると良いでしょう。Digitsは3か4ぐらいが妥当でしょう。OKを押して保存します。  

おわり






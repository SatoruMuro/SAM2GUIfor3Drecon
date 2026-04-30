# Seg on Web の使い方（日本語）

## Web版SegRef3D：AIによる自動セグメンテーション

---

## 🖼 使用する画像の準備

- **対象**：連続切片画像・連続断層画像
- **形式**：JPEG（`.jpg`）形式の画像
- **ファイル名**：`image0001.jpg`, `image0002.jpg`, ... のように連番で保存
- **推奨サイズ**：1辺が **1000ピクセル以下**  
  大きい画像も使用できますが、処理時間が長くなります。

一括リサイズには以下のツールが便利です。

- 🔗 [ImageJ（Mac/Windows対応）](https://imagej.net/ij/)
- 🔗 [IrfanView（Windows専用）](https://www.irfanview.com/)

---

## 🚀 Seg on Web の起動（Google Colab）

**ツール名**：Seg on Web  
🔗 [Seg on Web を開く](https://satorumuro.github.io/SAM2GUIfor3Drecon/ColabNotebooks/segonweb.html)

### 起動手順

1. Google Colab が開いたら、メニューから  
   **「ランタイム」＞「ランタイムのタイプを変更」** を選択します。

2. ハードウェアアクセラレータで **T4 GPU** を選択して保存します。

3. メニューから  
   **「ランタイム」＞「すべてのセルを実行」** を選択します。

4. 警告が表示された場合は、内容を確認したうえで  
   **「このまま実行」** を選択します。

5. 実行完了まで数分かかります。  
   ノートブックの最下部までスクロールし、セルの下に表示される  
   `Running on public URL` のリンクをクリックします。

6. Gradio GUI が開きます。

⚠️ **Colabノートブックの画面は閉じないでください。**  
Gradio GUI は、Colabノートブックが実行中の間だけ使用できます。

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/step1-01-2.PNG" alt="Colab launch" width="50%">

---

## 🖱 GUIの基本操作フロー

1. **Upload Images** から画像を複数枚アップロードします。
2. **Frame Selection** で、基準となる画像を選択します。
3. 対象物の範囲を指定します。
   - `X Coordinate (%)`
   - `Y Coordinate (%)`
   を調整しながら、対象物を囲む左上・右下の位置を指定します。
4. **Set Top Left** を押して左上を登録します。
5. **Set Bottom Right** を押して右下を登録し、セグメンテーションを実行します。
6. 結果を確認し、問題なければ  
   **Complete Segmentation or Add Next Object** を押します。
7. 2つ目以降の対象物がある場合は、同じ手順で追加します。  
   最大20個までのオブジェクトに対応しています。
8. すべての対象物を登録したら、**Start Tracking** を押します。
9. セグメンテーション結果を確認します。
10. 生成されたファイルをダウンロードします。

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/GUIimage.JPG" alt="Seg on Web GUI" width="50%">

---

## 📁 出力されるファイル

Seg on Web では、ローカル版SegRef3Dで読み込むための **正本PNGマスク** が標準出力されます。

### 標準出力

| 出力名 | 内容 | 形式 | 使用用途 |
|---|---|---|---|
| `Label mask PNGs (ZIP)` | 正本PNGマスク | PNG | ローカル版SegRef3Dでの修正・STL/NIfTI/CSV出力 |

正本PNGマスクは、**single-channel label image** です。

| ピクセル値 | 意味 |
|---|---|
| `0` | 背景 |
| `1` | Object 1 |
| `2` | Object 2 |
| `...` | ... |
| `20` | Object 20 |

通常はこの **Label mask PNGs (ZIP)** をダウンロードすれば十分です。

---

## 🧩 Optional Outputs

必要に応じて、`Optional Outputs` から追加出力を選択できます。

| オプション | 内容 | 形式 | 使用用途 |
|---|---|---|---|
| `Overlay images` | 元画像とマスクを重ねた確認用画像 | JPG/ZIP | 確認・記録・プレゼン |
| `Color preview masks` | 黒背景のカラー確認用マスク | PNG/ZIP | 確認・記録・プレゼン |
| `SVG vector masks` | ベクター形式マスク | SVG/ZIP | 旧ワークフローとの互換用 |
| `Grayscale masks` | グレースケールマスク | PNG/ZIP | 旧ワークフローとの互換用 |

⚠️ Optional Outputs を多く選択すると、処理時間とダウンロードファイルサイズが増加します。  
通常は、**Label mask PNGs (ZIP)** のみで問題ありません。

---

## 🎨 セグメンテーションの色ラベル

Web画面上のプレビューでは、各オブジェクトに以下の色ラベルが割り当てられます。

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/colorlabels1.jpg" alt="Color labels" width="50%">

---

## 🔁 ローカル版SegRef3Dへの取り込み

Web版で生成した正本PNGマスクは、ローカル版SegRef3Dで読み込んで修正できます。

### 手順

1. `Label mask PNGs (ZIP)` をダウンロードします。
2. ZIPファイルを展開します。
3. ローカル版SegRef3Dを起動します。
4. **Load Images** から、元画像フォルダを読み込みます。
5. **Load Masks** から、展開した正本PNGマスクフォルダを読み込みます。
6. 読み込まれたオブジェクトは自動的に表示ONになります。
7. 必要に応じて、手動でマスクを修正します。
8. STL / NIfTI / CSV などを出力します。

⚠️ 正本PNGマスクは、元画像と同じ画像サイズである必要があります。  
Seg on Web では、元画像サイズに合わせて正本PNGが出力されます。

---

## 🛠 ローカル版SegRef3Dで可能な作業

正本PNGを読み込んだ後は、ローカル版SegRef3Dで以下の作業が可能です。

- マスクの手動修正
- オブジェクトの追加・削除
- 不要領域の消去
- 色ラベルの変更
- STL出力
- NIfTI label map出力
- 体積・面積・脂肪浸潤率などの計測CSV出力

GPU非搭載環境では、ローカル版SegRef3D上のSAM2自動セグメンテーション機能は無効になります。  
ただし、Web版で作成した正本PNGを読み込めば、修正・計測・3D出力はローカルで実行できます。

---

## 🔁 ツールをリセットするには？

Gradio GUIの動作がおかしい場合は、以下の手順でリセットしてください。

1. Gradio GUI画面を閉じます。
2. Colabノートブック画面に戻ります。
3. メニューから  
   **「ランタイム」＞「ランタイムを接続解除して削除」**  
   を選択します。
4. 再度、  
   **「ランタイム」＞「すべてのセルを実行」**  
   を実行します。

---

## ▶️ 次のステップへ進む

Seg on Web で正本PNGを作成した後は、ローカル版 SegRef3D でマスクの修正・確認・出力を行います。

- 👉 [SegRef3Dでのマスク修正・3D出力手順](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/TutorialSegRef3DJP.md)

---

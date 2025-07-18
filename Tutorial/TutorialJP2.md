# Seg\&Refの使い方 - Step 2

## Step 2：セグメンテーションマスクの修正

このステップでは、**RefTool** を用いて自動セグメンテーション結果を修正します。RefTool は、医用画像に重ねたセグメンテーションマスク（SVG形式）を、直感的なペン操作で編集できるツールです。

---

# RefTool 操作マニュアル

## 概要

**RefTool** は、医用画像やマスク画像に対して、編集・可視化・変換・3D出力を行うためのツールです。マスクは20種類の色（オブジェクト）に分類され、それぞれの編集・変換・抽出・STL出力が可能です。

## インストール方法

### GitHubからダウンロード

GitHubリリースページから `RefToolPyQt.exe` をダウンロードします。
👉 [https://github.com/SatoruMuro/SAM2GUIfor3Drecon/releases/tag/RefTool](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/releases/tag/RefTool)

### ファイルを展開

任意のフォルダに `RefToolPyQt.exe` を配置してください（インストールは不要です）。

### 起動

`RefToolPyQt.exe` をダブルクリックして起動します。

---

## 基本操作

### 1. フォルダの読み込み

**Load Image Folder**

* 画像（.jpg/.png/.tif/.dcmなど）の入ったフォルダを読み込みます。
* DICOMは自動でJPEGに変換されます。

**Load Mask Folder**

* `.svg` 形式のマスクファイルが入ったフォルダを読み込みます。
* 既定の20色以外は自動で削除されます。

### 2. 描画と編集

**ペン色の選択（Pen Color）**

* 描画用の線色を「Gray / White / Black」から選びます。

**描画した線の操作**

* **Undo Line**: 最後の線を取り消し
* **Redo Line**: 取り消した線を再適用
* **Clear Lines**: 全ての線を削除

### 3. オブジェクト編集

**Target Object（1～20）** を選択後：

* **Add to Mask**：描画範囲をオブジェクトとして追加
* **Erase from Mask**：描画範囲を対象オブジェクトから削除
* **Transfer To**：描画範囲を別のオブジェクトに転送
* **Undo Edit / Redo Edit**：SVG編集のやり直し

### 4. 可視化と表示制御

* 各オブジェクトのチェックボックスで、表示・非表示を切り替え可能
* **Rescan Used Colors**：マスクファイル内の使用色を再スキャンしてUIを更新

### 5. オブジェクト変換・順序変更

**Convert Object Color**

* すべてのマスク内の色を一括で別の色に変換

**Bring to Front / Send to Back**

* 特定オブジェクトを前面／背面に表示変更（表示順制御）

### 6. キャリブレーションと3D出力

**Draw Calibration Line**

* 画像上に実寸線を描き、長さを入力してスケール（mm/px）を取得

**Line Length (mm) / Z Interval (mm)**

* 実線長・スライス間隔を設定（STL出力時に使用）

**Smooth Level**

* STL出力時の滑らかさ（Z方向補間レベル 0〜10）

**Export STL per Color**

* 色ごとに3D STLを一括出力。出力先フォルダは `stl_output_YYYYMMDD_HHMMSS`

### 7. マスクの画像出力

**Export TIFF**

* SVGマスクをグレースケールTIFFに変換して出力

**Export TIFF (Reversed)**

* 順番を逆にしてTIFF出力

出力先フォルダは自動生成されます（例：`tiff_output_YYYYMMDD_HHMMSS`）。

---

## ショートカットキー

| キー       | 動作                    |
| -------- | --------------------- |
| ↑ / R    | 前の画像へ                 |
| ↓ / F    | 次の画像へ                 |
| Ctrl + Z | 描画のUndo／編集のUndo（自動判定） |
| E / Q    | 拡大 / 縮小               |
| W/A/S/D  | 上下左右スクロール             |

---

## 出力ファイルの保存場所

* 編集済みマスク（SVG）: `masks_YYYYMMDD_HHMMSS`
* TIFF出力: `tiff_output_YYYYMMDD_HHMMSS`
* STL出力: `stl_output_YYYYMMDD_HHMMSS`
* キャリブレーション情報: `*_volinf.csv`

---

## 注意点

* `.svg` マスクは編集時に上書きされますが、元のファイルは変更されません。
* 編集対象外の色（黒背景など）は自動で削除されます。
* 全操作はローカルPC上で完結します（インターネット接続不要）。

---

### ▶️ 次のステップへ進む 🔗

- 👉 [Step 3：3D再構築はこちら](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/TutorialJP3.md)

---


---
---

以下は Segment Editor PP　（Step2の旧ver） の操作マニュアルです。

---

### ⚠️ 注意事項
**Segment Editor PP** および **Graphic2shape** は **Windows専用**です。他のOS（Mac/Linux）では動作に制限があります。

---

### 🧠 セグメンテーションを複数回行った方へ

自動セグメンテーション（Step 1）を複数回行った場合、**ラベルの重複を防ぐ**ために、以下のカラーツールでラベルを再整理してください：

🔗 [ColorChanger（Colab）](https://colab.research.google.com/github/SatoruMuro/SAM2GUIfor3Drecon/blob/main/ColabNotebooks/ColorChanger_v1_4.ipynb)  

---

### 🛠 使用するツール

- 🔽 [Segment Editor PP](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/releases/tag/ref2.0)（PowerPoint マクロ対応）
- 🔽 [Graphic2shape](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/releases/tag/gv1.2)（図形変換ツール）
- 🔁 入力するマスクファイル：Step 1で出力された `mask_svgs`（SVGファイル）

---

### ✅1️⃣ 作業開始前にやること1（ファイルの初期設定）

**(1) マクロを有効にする（pptmファイル）**  
ダウンロードした `.pptm` ファイル（Segment Editor PP）は、初回実行時にマクロが無効化されていることがあります。以下の手順でマクロを有効にしてください（Windows）：

1. ファイルを**右クリック**して「**プロパティ**」を選択  
2. 「全般」タブの下部に表示される  
　`□ 許可する（このファイルは他のコンピューターから取得したものです）` にチェックを入れる  
3. 「OK」をクリック  
4. PowerPoint でファイルを開き、「**コンテンツの有効化**」をクリックしてマクロを有効にする

**(2) スライドサイズの調整**  
連続断層画像のピクセルサイズのアスペクト比（幅：高さ）をファイルのプロパティ等で確認し、スライドのアスペクト比をそれに合わせる（幅と高さの比率が同じになればOK）。

**(3) クイックアクセスツールバーにマクロを追加**  
Bグループのマクロ（Ba / Bb / Bc）は、よく使うためクイックアクセスツールバーに登録しておくと便利です。

🔧 手順：

1. PowerPoint ウィンドウの左上にあるクイックアクセスツールバーの「▼」をクリック  
2. 「**その他のコマンド**」を選択  
3. 「コマンドの選択」で `マクロ` を選ぶ  
4. `BaSelectShapeAndRecord`, `BbCutimageWithPreviousShapeAndApplyColor`, `BcMergeWithPreviousShapeAndApplyColor` をそれぞれ選択して「追加」  
5. 上下のボタンを操作して、上から順に並ぶように配置する
6. 「OK」で確定

💡 配置した順番に応じて、`Alt + 数字キー` のショートカットで簡単にマクロを呼び出せます。

**(4) 「開発」タブの表示**  
マクロは「開発」または「表示」タブから実行できます。PowerPointの初期設定では「開発」タブは非表示なので、以下の手順で表示します：  
`ファイル > オプション > リボンのユーザー設定 > メインタブ > 開発` にチェックを入れてください。

---

### ✅2️⃣ 作業開始前にやること2（作業環境セッティング）


**(1) 作業姿勢と環境のセッティング**  
修正作業は、以下のような作業環境が推奨されます：

- タッチ対応PC（例：Microsoft Surface Book）＋Surfaceペン  
　　または  
- 外付けペンタブレット（例：Wacom Cintiq 22）＋キーボード  

基本的な作業姿勢は以下の通りです：

- **右手でペン操作、左手でキーボード操作**（ショートカット操作）を推奨  
- **左利きの場合は逆でもOK**  

💡 この姿勢により、片手でマスク修正、もう片手でマクロ実行やスライド移動がスムーズに行えます。

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/setting01.jpg" alt="Settig" width="50%">

**(2) キー配置の最適化（PowerToysの使用）**  
[Windows PowerToys](https://github.com/microsoft/PowerToys/releases/tag/v0.85.0) の `Keyboard Manager` を使用して、ショートカットキーの割り当てをカスタマイズすると、左手のキーボード操作がしやすくなります。

💡 たとえば、以下のように割り当てると快適です：  

| 機能                     | もとのキー        | 割り当て先       |
|--------------------------|-------------------|------------------------|
| マクロBa（対象を記録）   | Alt + 1           | A                     |
| マクロBb（マスクを削る） | Alt + 2           | S                     |
| マクロBc（マスクを広げる）| Alt + 3           | D                     |
| スライド戻る             | PgUp              | R                     |
| スライド進む             | PgDn              | F                     |
| Ctrl（拡大縮小用）       | Ctrl              | E                     |
| 削除                     | Delete            | Q                     |
| Esc（選択解除など）      | Esc               | W                     |

🖋 **このようなキー配置では：**
- **人差し指** → スライドの切り替え（`PgUp` / `PgDn`）  
- **中指** → `Ctrl` キーを押しながら  
- **反対の手でマウススクロール** → 拡大・縮小操作  
がスムーズに行えます。

🔁 **マクロ操作（Ba/Bb/Bc）についてはこのあと解説します。**

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/setting02.png" alt="Settig" width="50%">

---

### 🗂 マクロ構成と作業手順（Segment Editor PP）

---

#### 🔷 グループA：編集前のデータ入力

| マクロ名 | 機能 |
|----------|------|
| `AaAddImages` | 元画像（連続断層画像）をスライドに一括配置（1スライド1画像） |
| `AbAddMasks` | SVG形式のマスク画像を対応するスライド上に重ねて配置 |
| `AcDeleteBlackShapesWith70PercentTransparent` | 不要な黒背景を削除し、マスクを70%透過に設定 |

#### 📝 作業手順：グループAマクロの使用

1. PowerPointのウィンドウを**最前面**にしておく  
2. **マクロ `AaAddImages` を実行**：セグメンテーションを行う元画像（組織切片やCT画像）（例：image0001.jpg ～）が置かれているフォルダを選択  
   - 1枚ごとにスライドへ自動配置され、スライド数と画像数が一致する状態になります  
3. **マクロ `AbAddMasks` を実行**：Step 1で出力した `mask_svgs` フォルダを選択（個々のファイル名：mask0001.svg ～）  
   - 各スライド上の元画像に対応して、SVGマスクが上に重ねられます（mask0001等のファイル名で対応場所を検出します）  

4. SVGマスクはPowerPoint上でそのままでは**編集できません**  
   - マクロ `Ab` 実行直後に、[**Graphic2shape**](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/releases/tag/gv1.2)（Windows専用）を起動  
   - ダイアログの指示に従い、変換対象のスライド数を入力  
   - 各スライド上のSVGが自動的に**図形（Shape）に変換**され、編集可能になります
     ⚠️ 自動変換中はマウスやキーボード操作はできません（バックグラウンド動作非対応）  

5. **マクロ `AcDeleteBlackShapesWith70PercentTransparent` を実行**：  
   - マスク画像に含まれていた黒背景を削除  
   - 各マスクを70%の透過に設定し、元画像が見える状態になります  

✅ この状態で、**マスクが半透明に重なった状態で表示・編集可能**となり、次の「グループB：編集作業」へ進めます。

---

#### 🖊 グループB：編集作業（マスクの微修正）

| マクロ名 | 機能 |
|----------|------|
| `BaSelectShapeAndRecord` | 編集対象となるマスクを記録（選択状態に） |
| `BbCutimageWithPreviousShapeAndApplyColor` | 描画図形を使ってマスクを削る（減算） |
| `BcMergeWithPreviousShapeAndApplyColor` | 描画図形を使ってマスクを広げる（加算） |

#### 📝 作業手順：グループBマクロの使用

1. 編集したいマスク（図形）をクリックして選択  
2. マクロ `BaSelectShapeAndRecord` を実行（キー配置により小指でAを押すと実行されます）→　このマスクが編集対象になります  
3. PowerPointの「描画」ツールから **フリーフォーム（Scribble）** または **曲線ツール（Curve）** を選択  
4. 増減させたいマスクの形状をなぞるように描く（※描いた図形が選択されたままにしておく）  
5. 以下のいずれかを実行：  
   - `Bb` を実行 → マスク範囲を削る（減算） （キー配置により薬指でSを押すと実行されます）  
   - `Bc` を実行 → マスク範囲を広げる（加算） （キー配置により中指でDを押すと実行されます）  

<img src="https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/images/refine01.png" alt="Settig" width="80%">

---

#### 💾 グループC：編集後の出力

| マクロ名 | 機能 |
|----------|------|
| `CaFinalizeMasks` | 背景を非表示にし、マスクだけの画像に変換 |
| `CbExportToGrayPNG` | グレースケールPNGとして出力（→ Step 3で使用） |
| `CbExportToPNG` | RGBカラーマスクをPNG形式で出力 |
| `CcReturnToMaskEditing` | マスク編集モードに戻す（再編集したい場合） |

#### 📝 作業手順：グループCマクロの使用

1. すべてのマスク修正が完了したら、マクロ `CaFinalizeMasks` を実行  
   - 背景画像（連続断層画像）を非表示にし、黒背景上にマスクのみが残る状態にします  
2. 続いて、マクロ `CbExportToGrayPNG` を実行  
   - グレースケールPNGファイルとしてエクスポート  
   - ダイアログが表示されるので、画像サイズ（例：378 × 613 px）幅と高さをそれぞれを入力  
   - グレースケール画像は **3D Slicerでのセグメント抽出（Step 3）** に使用可能

💡 RGBベースの抽出を行う他ソフトを使用する場合は、マクロ `CbExportToPNG` を使ってカラー画像として出力してください。  
💡 マスク編集をやり直したい場合は、マクロ `CcReturnToMaskEditing` を実行すれば再編集が可能です。

---

#### 💡 出力ファイルの保存先と注意点

- 出力ファイルは、pptmファイルと同じフォルダ内に `edittedmasks` という名前のフォルダとして自動生成されます  
- すでに同名フォルダがある場合は**上書き保存される**ので、必要に応じて事前にバックアップを取ってください

---

### ▶️ 次のステップへ進む 🔗

- 👉 [Step 3：3D再構築はこちら](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/blob/main/Tutorial/TutorialJP3.md)

---

# Seg&Refの使い方 - Step 2

## セグメンテーションマスクの修正

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

### ✅ 作業開始前にやること（初期設定）

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

### 🗂 マクロ構成（Segment Editor PP）

#### 🔷 グループA：編集前のデータ入力

| マクロ名 | 説明 |
|---------|------|
| `AaAddImages` | 元画像（連続断層画像）を一括配置 |
| `AbAddMasks` | SVG形式のマスクを画像上に重ねる |
| `AcDeleteBlackShapesWith70PercentTransparent` | 黒背景を削除・マスクを70%透過化 |

✅ Ab 実行後は、**Graphic2shape** を使ってマスクを図形に変換してください。

---

#### 🖊 グループB：編集作業

| マクロ名 | 機能 |
|---------|------|
| `BaSelectShapeAndRecord` | 編集するマスクを選択＆記録 |
| `BbCutimageWithPreviousShapeAndApplyColor` | 領域の削除（減算） |
| `BcMergeWithPreviousShapeAndApplyColor` | 領域の追加（加算） |

📝 推奨操作環境：
- 右手：タッチペン or マウス
- 左手：キーボードショートカット（再割り当て推奨）
- [Windows PowerToys](https://github.com/microsoft/PowerToys/releases/tag/v0.85.0) を使ってキー配置を最適化可能

<img src="images/KeyRemapping.jpg" alt="KeyRemapping" width="75%">

#### 編集手順の例：

1. 修正したい図形を選択 → `Ba` 実行  
2. フリーフォームや曲線で新たな形状を描く  
3. 描画図形を選択したまま、`Bb` または `Bc` を実行

---

#### 💾 グループC：編集後の出力

| マクロ名 | 内容 |
|---------|------|
| `CaFinalizeMasks` | 背景を消してマスクのみの画像を作成 |
| `CbExportToGrayPNG` | **グレースケールPNG**として出力（→ Step 3で使用） |
| `CbExportToPNG` | カラーPNGとして出力 |
| `CcReturnToMaskEditing` | 編集モードに戻る |

グレースケールのラベル値：（各オブジェクトに割り当て）  
`255, 248, 237, 226, 215, 204, 193, 182, 171, 160, 149, 138, 127, 116, 105, 94, 83, 72, 61, 50`

---

### 💡 保存先と注意点

- 出力ファイルは `edittedmasks` フォルダに保存されます（Segment Editor PP と同じディレクトリに作成）  
- 既に `edittedmasks` が存在する場合は **上書きされる**ので注意

<img src="images/step1-06-2.PNG" alt="Segment Output" width="100%">

---

### ▶️ 次のステップへ進む 🔗

- 👉 [Step 3：3D再構築と解析はこちら](./README_Step3.md)

---

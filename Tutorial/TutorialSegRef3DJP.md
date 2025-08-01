# SegRef3D チュートリアル（日本語）

---

## 🕹️ 基本操作

- **🔄 画像の切り替え**  
  - 次の画像へ：`PageDown`, `F`, `J`  
  - 前の画像へ：`PageUp`, `R`, `U`

- **🔍 画像の拡大縮小**  
  - 拡大：`E`, `I`, `+`, `=`  
  - 縮小：`Q`, `P`, `-`  
  - （または `Ctrl` + スクロール）

- **🧭 拡大時の画像移動**  
  - 上へ移動：`W`, `O`, `↑`  
  - 下へ移動：`S`, `L`, `↓`  
  - 左へ移動：`A`, `K`, `←`  
  - 右へ移動：`D`, `;`, `→`  
  - （または スクロール、`Shift` + スクロールで左右移動）

- **✏️ 描画操作（クリックモード）**  
  - 描画を確定：`G`, `H`  
  - 直前のクリックポイントをUndo：`T`, `Y`

- **↩️ Undo（描画や編集の取り消し）**  
  - `Ctrl + Z`（別途実装されている場合）


---

## 🔄 基本ワークフロー

### 🤖 自動セグメンテーション（Segmentation）

1. `Load Image Folder` で画像を読み込み
2. `Prepare Tracking` でトラッキングの準備
3. `Set Box Prompt` で対象を囲む矩形を設定
4. トラッキングの開始位置の画像を表示 → `Set Tracking Start`
5. 終了位置の画像を表示 → `Set Tracking End`
6. `Run Tracking` を押す（※時間がかかる場合あり）
7. `Target Object` 番号を指定し、`Add to Mask` を押してマスクを登録
8. オブジェクト表示は画面下のチェックボックスでON/OFF可能

---

### ✏️ 編集（Refinement）

* マウスまたはタッチペンで画像上に描画
* `Target Object` に対して `Add` または `Erase` を選んでマスクを編集
* ペン色：`Gray`, `White`, `Black`
* 描画モード：`Free`, `Click`, `Click (Snap)`

---

### 💾 セグメンテーションデータの保存

* `Save SVG` で作業内容をSVG形式で保存
* 次回編集時は：

  * `Load Image Folder` で画像読み込み
  * `Load Mask Folder` で保存済みSVGフォルダを指定

---

### 📏 キャリブレーション（DICOM画像以外）

* 実寸長と切片間隔を入力
* `Draw Calibration Line` を押して、画像上に線を描画

---

### 📐 3D出力

* `Export STL per Color` を押すとオブジェクトごとにSTL出力
* STLの閲覧は外部ツール（例：3D Slicer, MeshLab）を使用

---

### 📊 計測

* `Export Volume CSV` でオブジェクトごとの体積をCSV出力

---

## 🧩 応用機能

### 🔁 複数オブジェクトの一括トラッキング

1. 各オブジェクトに対し：

   * Box Promptの指定
   * Tracking Start/End の指定
   * `Add Object Prompt` を押す
2. すべて指定後、`Run Batch Tracking` を押す

---

### 🎚️ 閾値抽出

* `Threshold min` と `max` を指定
* `Extract by Threshold` を押すと該当領域を抽出
* `Add to Mask` でターゲットオブジェクトに追加
* プリセット設定あり（例：CT Soft Tissue など）

---

### 🧱 オブジェクトの前面／背面移動

* 対象のオブジェクト番号を `Reorder` に指定
* `Bring to Front` または `Send to Back` を押す

---

### 🧹 小さいマスク片の削除

* `Delete Object` に対象番号と `Threshold(px^2)` を指定
* `Remove Small Parts` を押す

---

### ❌ セグメンテーションマスクの削除

* `Delete Object CurrentImg`：現在画像のマスク削除
* `Delete Object AllImg`：すべての画像で削除

---

### 💠 3D STLファイルのスムージング

* `Smooth mode` を選択
* z-interpolation／mesh smoothing のON/OFF選択可

---


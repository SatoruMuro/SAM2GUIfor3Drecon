# SAM2GUI\_local

## 概要

`SAM2GUI_local` は、Google Colab を使わずに、Windows PC 上で動作するオフライン版のセグメンテーションツールです。
AIモデル「SAM2」による画像セグメンテーションを、ローカル環境で実行できます。

---

## 🖥️ 推奨動作環境

* OS：Windows 10 / 11
* **GPU：NVIDIA CUDA対応GPU（推奨）**

  * CPU環境でも動作しますが、処理が大幅に遅くなります。
* Python：3.10系
* 必要ライブラリ：PyTorch、torchvision（事前インストールが必要）

---

## 🛠️ 実行前の準備

この `.exe` を起動する前に、**Python および PyTorch をインストールしておく必要があります**。

### ❶ Python のインストール

1. [Python公式サイト](https://www.python.org/downloads/windows/) から **Python 3.10.x** をダウンロード
2. インストール時に「**Add Python to PATH**」にチェックを入れてください

---

### ❷ PyTorch のインストール

コマンドプロンプトを開いて、下記のいずれかのコマンドを実行してください：

#### 🔹 CUDA対応GPU環境（推奨）

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### 🔹 CPU環境（非推奨）

```bash
pip install torch torchvision
```

> 🔍 お使いの環境に応じたインストールコマンドは [PyTorch公式サイト](https://pytorch.org/get-started/locally/) でも確認できます。

---

## ▶️ 実行方法（.exe版）

1. [Releases](https://github.com/SatoruMuro/SAM2GUIfor3Drecon/releases) から `SAM2GUI_local.zip` をダウンロード
2. ZIP を展開し、`SAM2GUI_local.exe` をダブルクリックして起動

   * 初回起動時は数十秒かかることがあります
3. ブラウザが自動で開かない場合は、表示された URL (例：[http://127.0.0.1:7860](http://127.0.0.1:7860)) をコピーしてブラウザに貼り付けてください

---

## ⚠️ 注意点

* `.exe` は PyInstaller でビルドされていますが、**Python と PyTorch が事前に実装されている必要があります**。
* GPUがないPCでも動作しますが、処理速度が大幅に低下します。
* セキュリティ警告が出る場合は「詳細情報」→「実行」を選んでください（自身でビルドした場合は問題ありません）。

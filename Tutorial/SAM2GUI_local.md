# SAM2GUI\_local

### Note: The English instructions are provided in the latter part of this page.

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

---

### PyTorch の搭載状況確認

#### PyTorch がすでにインストールされているか確認する方法

1. 「スタートメニュー」から「コマンドプロンプト（cmd）」を開きます。
2. 以下のコマンドを入力して、Enterキーを押してください。

```
python -c "import torch; print(torch.__version__)"
```

* バージョン番号（例：`2.1.0+cu118`）が表示された場合は、PyTorch がすでにインストールされています。
* エラーが表示された場合は、PyTorch が未インストールです。以下の手順に従ってPythonとPyTorchをインストールしてください。

---

### （PyTorch未搭載の場合）Python のインストール

1. [Python公式サイト](https://www.python.org/downloads/windows/) から **Python 3.10.x** をダウンロード
2. インストール時に「**Add Python to PATH**」にチェックを入れてください

---

### （PyTorch未搭載の場合）PyTorch のインストール

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

1. 下記リンクから `SAM2GUI_local.zip` をダウンロード
   　👉 [SAM2GUI\_local.zip をダウンロード（Dropbox）](https://www.dropbox.com/scl/fi/dg2xlo0ttt6b1scm4tied/SAM2GUI_local.zip?rlkey=09n4blxnl2nc66ay5429y6nvv&st=kexneowk&dl=1)

   > （注）Dropbox の共有リンクです。どなたでもダウンロード可能ですが、ファイル内容は変更できません。

2. ZIP を展開し、`SAM2GUI_local.exe` をダブルクリックして起動
   　\* 初回起動時は数十秒かかることがあります

3. ブラウザが自動で開かない場合は、表示された URL (例：[http://127.0.0.1:7860](http://127.0.0.1:7860)) をコピーしてブラウザに貼り付けてください

---

### 📂 解凍先フォルダについての推奨

解凍したフォルダは、**`Cドライブ直下（例：C:\SAM2GUI_local）` に置くことを推奨**します。
フォルダ階層が深すぎると、パスの長さ制限やアクセス権の問題により、実行時にエラーが発生する場合があります。

---

## ⚠️ 注意点

* `.exe` は PyInstaller でビルドされていますが、**Python と PyTorch が事前に実装されている必要があります**。
* GPUがないPCでも動作しますが、処理速度が大幅に低下します。
* セキュリティ警告が出る場合は「詳細情報」→「実行」を選んでください（自身でビルドした場合は問題ありません）。

---
---

# SAM2GUI_local -English instructions-

## Overview

SAM2GUI_local is an offline segmentation tool that runs directly on Windows PCs
without the need for Google Colab. It enables local execution of image
segmentation using the AI model SAM2.

------------------------------------------------------------

🖥️ Recommended System Requirements

- OS: Windows 10 / 11
- GPU: NVIDIA CUDA-enabled GPU (recommended)
    - Works on CPU, but processing will be significantly slower.
- Python: Version 3.10.x
- Required Libraries: PyTorch, torchvision (must be pre-installed)

------------------------------------------------------------

🛠️ Preparation Before Execution

⚠️ Python and PyTorch must be installed **before** running the `.exe`.

------------------------------------------------------------

🔍 Check if PyTorch is Installed

Open Command Prompt and enter:

```
python -c "import torch; print(torch.__version__)"
```

→ Version number shown = PyTorch installed  
→ Error shown = PyTorch not installed

------------------------------------------------------------

🐍 Installing Python (if needed)

1. Download Python 3.10.x from:  
   https://www.python.org/downloads/windows/

2. During install, check:  
   ✅ Add Python to PATH

------------------------------------------------------------

📦 Installing PyTorch

In Command Prompt, run one of the following:

🟢 CUDA GPU (Recommended):
```
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

🔴 CPU Only (Not Recommended):
```
pip install torch torchvision
```

More: https://pytorch.org/get-started/locally/

------------------------------------------------------------

▶️ How to Run the Executable (.exe)

1. Download:
   https://www.dropbox.com/scl/fi/dg2xlo0ttt6b1scm4tied/SAM2GUI_local.zip?rlkey=09n4blxnl2nc66ay5429y6nvv&st=kexneowk&dl=1

2. Unzip and double-click:
   SAM2GUI_local.exe  
   (First launch may take several seconds)

3. If the browser doesn't open, paste this into it:
   http://127.0.0.1:7860

------------------------------------------------------------

📂 Recommended Extraction Folder

→ Extract to:
   C:\SAM2GUI_local

Avoid deep paths to prevent errors due to Windows limits.

------------------------------------------------------------

⚠️ Notes

- The .exe is built with PyInstaller  
  → Python and PyTorch must be installed beforehand  
- Runs without GPU but is much slower  
- If a SmartScreen warning appears:  
  Click "More info" → "Run anyway"

------------------------------------------------------------



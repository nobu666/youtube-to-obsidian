# youtube-recipe-pipeline

YouTube料理動画の音声を文字起こしし、Obsidianのレシピノートに自動変換するツール。

## 仕組み

1. **transcribe.py** — yt-dlp で音声抽出 → mlx-whisper でローカル文字起こし → `_transcripts/` に保存
2. **recipe** — transcribe.py を実行後、Claude CLI (`claude -p`) で文字起こしをレシピ形式に変換

## 必要なもの

- macOS（Apple Silicon）
- Python 3.10+
- [Claude Code](https://docs.claude.com/en/docs/claude-code) (`claude` コマンド)
- Obsidian Vault（レシピの保存先）

## セットアップ

```bash
# ツールのインストール
brew install yt-dlp ffmpeg python@3.12

# venv 作成と mlx-whisper インストール
python3.12 -m venv ~/scripts/.venv
source ~/scripts/.venv/bin/activate
pip install mlx-whisper

# スクリプトを配置
cp transcribe.py ~/scripts/
cp recipe ~/scripts/
chmod +x ~/scripts/recipe
```

`recipe` 内のパスを自分の環境に合わせて編集:

```bash
SCRIPT="$HOME/scripts/transcribe.py"                                          # transcribe.py のパス
RECIPE_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Obsidian/Vault/レシピ"  # Obsidian Vault のパス
```

`transcribe.py` 内の `OBSIDIAN_RECIPE_DIR` も同様に変更。

## 使い方

```bash
# 再生リストをまとめて処理
~/scripts/recipe https://www.youtube.com/playlist?list=XXXXX

# 単体の動画
~/scripts/recipe https://www.youtube.com/watch?v=XXXXX

# 文字起こしだけ（レシピ変換なし）
~/scripts/.venv/bin/python3 ~/scripts/transcribe.py https://www.youtube.com/watch?v=XXXXX
```

## 出力形式

```markdown
---
created: 2026-06-16 19:00
updated: 2026-06-16 19:00
source: https://www.youtube.com/watch?v=XXXXX
---

# 料理名

* 材料1 分量
* 材料2 分量

1. 手順1
2. 手順2
```

## 注意点

- mlx-whisper は Apple Silicon 専用。Intel Mac では動かない
- Whisper medium モデル（750MB）を使用。初回実行時にダウンロードされる
- 処理済みの動画はスキップされるので、中断しても再開可能
- `MallocStackLogging` の警告が出ることがあるが無害

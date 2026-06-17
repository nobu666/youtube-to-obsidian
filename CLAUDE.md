# CLAUDE.md

YouTube動画やWeb記事をObsidianの構造化ノートに自動変換するツール。

## プロジェクト構成

```
youtube-to-obsidian    # メインスクリプト（bashラッパー、claude -p を呼ぶ）
transcribe.py          # 文字起こし / Web記事テキスト抽出
prompts/               # プロンプトファイル（-p オプションで切り替え）
tests/                 # pytest テスト
install.sh             # curl一発セットアップ
SKILL.md               # Claude Code スキル定義
```

## インストール・シンボリックリンク

`install.sh` が以下を作成する:
- `~/scripts/youtube-to-obsidian` → このリポジトリの `youtube-to-obsidian`
- `~/scripts/transcribe.py` → このリポジトリの `transcribe.py`
- `~/scripts/.venv/` — Python venv（mlx-whisper 等）

## テスト

```bash
~/scripts/.venv/bin/python3 -m pytest tests/ -v
```

外部依存（yt-dlp, mlx-whisper, ファイルシステム）はすべてモック。mlx-whisper は Apple Silicon 専用のため CI 上ではインストールしない。

## 注意事項

- `mlx-whisper` を `openai-whisper` に差し替えないこと（Apple Silicon 最適化が前提）
- プロンプトファイルは `output_dir:` ヘッダ + `---` + 本文の形式
- コメントとプロンプトは日本語で書くこと

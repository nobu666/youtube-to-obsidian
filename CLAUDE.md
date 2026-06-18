# CLAUDE.md

YouTube動画・Web記事・ドキュメント（PDF/スライド等）をObsidianの構造化ノートに自動変換するツール。

## プロジェクト構成

```
obsidian-import        # メインスクリプト（bashラッパー、claude -p を呼ぶ）
transcribe.py          # YouTube文字起こし / Web記事テキスト抽出
convert.py             # ドキュメント変換（MarkItDown: PDF, PPTX, DOCX, URL等）
prompts/               # プロンプトファイル（-p オプションで切り替え）
tests/                 # pytest テスト
install.sh             # curl一発セットアップ
SKILL.md               # Claude Code スキル定義
```

## インストール・シンボリックリンク

`install.sh` が以下を作成する:
- `~/scripts/obsidian-import` → このリポジトリの `obsidian-import`
- `~/scripts/transcribe.py` → このリポジトリの `transcribe.py`
- `~/scripts/convert.py` → このリポジトリの `convert.py`
- `~/scripts/.venv/` — Python venv（mlx-whisper, markitdown 等）

## テスト

```bash
~/scripts/.venv/bin/python3 -m pytest tests/ -v
```

外部依存（yt-dlp, mlx-whisper, ファイルシステム）はすべてモック。mlx-whisper は Apple Silicon 専用のため CI 上ではインストールしない。

## 注意事項

- `mlx-whisper` を `openai-whisper` に差し替えないこと（Apple Silicon 最適化が前提）
- プロンプトファイルは `output_dir:` ヘッダ + `---` + 本文の形式
- コメントとプロンプトは日本語で書くこと

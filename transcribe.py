#!/usr/bin/env python3
"""
YouTube再生リストの動画を音声ダウンロード → Whisperで文字起こし。
文字起こし結果はObsidianレシピフォルダ内の _transcripts/ に保存される。
レシピへの変換はCoworkスキルが担当する。

事前準備:
  brew install yt-dlp ffmpeg
  pip3 install mlx-whisper

使い方:
  python3 transcribe.py <再生リストURL>
  python3 transcribe.py <動画URL>
  python3 transcribe.py  # デフォルトの再生リストを使用
"""

import subprocess
import json
import sys
import time
from pathlib import Path

# === 設定 ===
OBSIDIAN_RECIPE_DIR = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/Obsidian/Vault/レシピ"
TRANSCRIPT_DIR = OBSIDIAN_RECIPE_DIR / "_transcripts"
AUDIO_TMP_DIR = Path("/tmp/yt_recipe_audio")
WHISPER_MODEL = "mlx-community/whisper-medium-mlx"


def setup_dirs():
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_TMP_DIR.mkdir(parents=True, exist_ok=True)


def get_videos(url):
    """URLから動画情報を取得（再生リストでも単体でもOK）"""
    print("動画情報を取得中...")
    result = subprocess.run(
        ["yt-dlp", "--flat-playlist", "-J", url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"エラー: 動画情報の取得失敗\n{result.stderr}")
        sys.exit(1)

    data = json.loads(result.stdout)

    # 単体動画の場合
    if "entries" not in data:
        return [{
            "id": data.get("id", "unknown"),
            "title": data.get("title", "unknown"),
            "url": url
        }]

    # 再生リストの場合
    videos = []
    for entry in data.get("entries", []):
        videos.append({
            "id": entry["id"],
            "title": entry.get("title", "unknown"),
            "url": f"https://www.youtube.com/watch?v={entry['id']}"
        })
    return videos


def download_audio(video):
    """動画の音声をダウンロード"""
    output_path = AUDIO_TMP_DIR / f"{video['id']}.mp3"
    if output_path.exists():
        print(f"  音声キャッシュあり")
        return output_path

    print(f"  音声ダウンロード中...")
    result = subprocess.run(
        ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "5",
         "-o", str(output_path), video["url"]],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ダウンロード失敗: {result.stderr[:200]}")
        return None
    return output_path


def transcribe_audio(audio_path, video):
    """Whisperで文字起こし"""
    transcript_path = TRANSCRIPT_DIR / f"{video['id']}.txt"
    if transcript_path.exists():
        print(f"  文字起こし済み")
        return transcript_path

    print(f"  文字起こし中...")
    try:
        import mlx_whisper
        result = mlx_whisper.transcribe(
            str(audio_path),
            path_or_hf_repo=WHISPER_MODEL,
            language="ja",
            verbose=False
        )
        text = result["text"]
    except ImportError:
        print("  エラー: pip3 install mlx-whisper を実行してください。")
        return None
    except Exception as e:
        print(f"  文字起こしエラー: {e}")
        return None

    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(f"title: {video['title']}\n")
        f.write(f"video_id: {video['id']}\n")
        f.write(f"url: {video['url']}\n")
        f.write(f"---\n")
        f.write(text)

    return transcript_path


def main():
    setup_dirs()

    # URLの決定
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("使い方: python3 transcribe.py <YouTubeのURLまたは再生リストURL>")
        sys.exit(1)

    videos = get_videos(url)
    print(f"\n{len(videos)}本の動画が見つかりました。\n")

    done = 0
    failed = 0
    skipped = 0

    for i, video in enumerate(videos, 1):
        print(f"[{i}/{len(videos)}] {video['title'][:60]}")

        transcript_path = TRANSCRIPT_DIR / f"{video['id']}.txt"
        if transcript_path.exists():
            print(f"  スキップ（処理済み）\n")
            skipped += 1
            continue

        audio_path = download_audio(video)
        if not audio_path:
            failed += 1
            print()
            continue

        result = transcribe_audio(audio_path, video)
        if result:
            done += 1
            audio_path.unlink(missing_ok=True)
        else:
            failed += 1
        print()

    print(f"\n{'='*50}")
    print(f"完了！ 新規: {done}本 / スキップ: {skipped}本 / 失敗: {failed}本")

    if failed > 0 and done == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

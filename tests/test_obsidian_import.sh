#!/bin/bash
# obsidian-import シェルスクリプトのファイル名パース・バリデーションのテスト
# 実行: bash tests/test_obsidian_import.sh

PASS=0
FAIL=0

assert_eq() {
  local desc="$1" expected="$2" actual="$3"
  if [ "$expected" = "$actual" ]; then
    echo "  ✓ ${desc}"
    PASS=$((PASS + 1))
  else
    echo "  ✗ ${desc}"
    echo "    expected: '${expected}'"
    echo "    actual:   '${actual}'"
    FAIL=$((FAIL + 1))
  fi
}

# --- FILENAME抽出テスト ---
echo "=== FILENAME抽出 ==="

extract_filename() {
  echo "$1" | grep -m1 '^FILENAME: ' | sed 's/^FILENAME: //' | sed 's/^`//;s/`$//'
}

assert_eq "通常のファイル名" \
  "テスト.md" \
  "$(extract_filename "FILENAME: テスト.md")"

assert_eq "バッククォート付き" \
  "テスト.md" \
  "$(extract_filename 'FILENAME: `テスト.md`')"

assert_eq "前置テキストがある場合" \
  "ノート.md" \
  "$(extract_filename "$(printf '内容を変換しました。\nFILENAME: ノート.md\n---\n本文')")"

assert_eq "FILENAME行がない場合は空" \
  "" \
  "$(extract_filename "ただのテキスト出力")"

# --- ファイル名バリデーションテスト ---
echo ""
echo "=== ファイル名バリデーション ==="

validate_filename() {
  local f="$1"
  if [[ "$f" == *.md ]] && [[ "$f" != */* ]] && [[ "$f" != *..* ]]; then
    echo "valid"
  else
    echo "invalid"
  fi
}

assert_eq "正常なファイル名" "valid" "$(validate_filename "テスト.md")"
assert_eq "英語ファイル名" "valid" "$(validate_filename "test-note.md")"
assert_eq "スペース含むファイル名" "valid" "$(validate_filename "Claude Code まとめ.md")"
assert_eq "拡張子なし → 拒否" "invalid" "$(validate_filename "テスト")"
assert_eq ".txt拡張子 → 拒否" "invalid" "$(validate_filename "テスト.txt")"
assert_eq "パス区切り含む → 拒否" "invalid" "$(validate_filename "../../.zshrc.md")"
assert_eq "パス区切り含む(絶対パス) → 拒否" "invalid" "$(validate_filename "/etc/passwd.md")"
assert_eq "..含む → 拒否" "invalid" "$(validate_filename "..test.md")"
assert_eq "隠しファイル風の..含む → 拒否" "invalid" "$(validate_filename "..zshrc.md")"

# --- 本文抽出テスト ---
echo ""
echo "=== 本文抽出 ==="

extract_content() {
  echo "$1" | sed -n '/^FILENAME: /,$p' | tail -n +2
}

OUTPUT="$(printf 'コメント行\nFILENAME: テスト.md\n---\ncreated: 2026-01-01\n---\n# 本文')"
CONTENT="$(extract_content "$OUTPUT")"

assert_eq "FILENAME行の前のテキストが除去される" \
  "" \
  "$(echo "$CONTENT" | grep 'コメント行')"

assert_eq "frontmatterが含まれる" \
  "---" \
  "$(echo "$CONTENT" | head -1)"

assert_eq "本文が含まれる" \
  "# 本文" \
  "$(echo "$CONTENT" | tail -1)"

# --- 結果 ---
echo ""
echo "=== 結果: ${PASS} passed / ${FAIL} failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1

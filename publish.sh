#!/bin/bash
# 홈페이지 변경사항을 GitHub에 올립니다.
#   사용법:  ./publish.sh            (커밋 메시지 자동)
#            ./publish.sh "설명"     (커밋 메시지 직접 지정)
set -e
cd "$(dirname "$0")"

echo "▸ 사진 정리 중 (크기 축소 · 위치정보 제거)..."
./.venv/bin/python tools/optimize_images.py

echo
echo "▸ 변경된 파일:"
if [ -z "$(git status --porcelain)" ]; then
  echo "  (없음) — 올릴 변경사항이 없습니다."
  exit 0
fi
git status --short

echo
echo "▸ GitHub에 올리는 중..."
git add -A
git commit -q -m "${1:-Update site ($(date '+%Y-%m-%d %H:%M'))}"
git push -q origin main

echo
echo "✓ 완료. 1~2분 뒤 반영됩니다: https://hyungyuo3sonde.github.io"
echo "  (브라우저에서 Cmd+Shift+R 로 새로고침하세요)"

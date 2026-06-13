#!/bin/bash
# 변경 사항을 감지하여 커밋 및 푸시하는 스크립트

# 변경 사항이 있는지 확인
if [ -n "$(git status --porcelain)" ]; then
    echo "변경 사항 감지됨. 자동 커밋 및 푸시를 진행합니다..."
    git add .
    git commit -m "auto: 변경 사항 자동 커밋 ($(date '+%Y-%m-%d %H:%M:%S'))"
else
    echo "변경 사항이 없습니다."
fi

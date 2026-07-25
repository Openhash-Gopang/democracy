#!/usr/bin/env python3
"""
fix_desktop_bills_subtitle_wording.py

대상 저장소: democracy
목적: 이전 패치(fix_desktop_dawn_live_bulletin.py)에서 "심사 중" 필터
      버튼은 제거했지만, 같은 패널 상단 부제목 텍스트("동의 확보 중 ·
      심사 중 · 의결 중인 안건을 확인합니다")에 남아있던 동일 문구는
      고치는 걸 빠뜨렸다. 이번 파이프라인엔 별도 심사 단계가 없으므로
      (동의 임계치 달성 시 곧바로 투표로 회부) 문구를 정정한다.

실행 위치: democracy 저장소 루트 (desktop.html이 있는 폴더)
"""
import sys

TARGET = "desktop.html"
OLD = '<div class="ph-sub">동의 확보 중 · 심사 중 · 의결 중인 안건을 확인합니다.</div>'
NEW = '<div class="ph-sub">동의 확보 중 · 의결 중인 안건을 확인합니다.</div>'


def main():
    try:
        with open(TARGET, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"오류: {TARGET} 파일을 찾을 수 없습니다. democracy 저장소 루트에서 실행하세요.")
        sys.exit(1)

    count = content.count(OLD)
    if count == 0:
        if NEW in content:
            print("이미 정정된 상태입니다. 변경 없이 종료합니다.")
            sys.exit(0)
        print("오류: 대상 문자열을 찾지 못했습니다. desktop.html이 예상과 다르게 변경됐을 수 있습니다.")
        sys.exit(1)
    if count != 1:
        print(f"오류: 대상 문자열이 {count}번 발견됐습니다(1번이어야 안전). 수동 확인이 필요합니다.")
        sys.exit(1)

    content = content.replace(OLD, NEW, 1)
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"완료: {TARGET}의 안건 목록 부제목에서 미구현 '심사 중' 언급을 제거했습니다.")


if __name__ == "__main__":
    main()

"""
BMI 건강관리 프로그램 - 실행 진입점

실행 방법
    python main.py          → GUI 실행 (13주차 모듈 3, 기본)
    python main.py module3  → GUI 실행 (위와 같음)
    python main.py console  → 콘솔 APP 실행 (12주차 모듈 2 테스트용)
    python main.py module1  → 파일 저장/읽기 검증 (11주차 모듈 1 테스트용)

모듈 구성
    modules/health_db.py    : 모듈 1 - 레코드 구조와 JSON/CSV/TXT/Pickle 파일 입출력
    modules/health_logic.py : 모듈 2 - 등록/검색/수정/삭제/통계 비즈니스 로직
    modules/health_gui.py   : 모듈 3 - tkinter GUI
"""

import sys
import tempfile

from modules.health_db import HealthDB
from modules.health_gui import run_gui
from modules.health_logic import run_console


# [AI 사용]
# - AI 종류   : Claude (Claude Code)
# - 사용 목적 : 모듈 1 저장/읽기 결과를 검증하는 main() 작성
# - 프롬프트  : "main()에서 저장하기 전 값과 저장된 값을 읽어서 일치하는지 검증해줘"
# - 사용자    : Yunjongha
# - 날짜      : 2026-11-11
#
# [AI 사용]
# - AI 종류   : Claude (Claude Code)
# - 사용 목적 : 검증용 파일을 임시 폴더에 저장하도록 변경 (GUI에서 쓰는 data 폴더 보호)
# - 프롬프트  : "메인도 그에 맞게 변경해줘"
# - 사용자    : Yunjongha
# - 날짜      : 2026-11-24
def test_module1():
    """모듈 1 검증: 샘플 데이터를 4가지 형식으로 저장하고 다시 읽어 원본과 비교한다.

    실제 data 폴더를 덮어쓰지 않도록 임시 폴더에 저장하고, 끝나면 임시 폴더는 삭제된다.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. 임의의 데이터 입력 후 출력
        db = HealthDB(temp_dir)
        sample_data = [
            ("홍길동", 1995, "남", 175.0, 72.5),
            ("김영희", 1998, "여", 162.0, 52.0),
            ("이철수", 1988, "남", 180.0, 95.0),
            ("박민지", 2001, "여", 158.0, 44.0),
            ("최준호", 1992, "남", 170.0, 70.0),
        ]
        for name, birth_year, gender, height, weight in sample_data:
            db.add_record(name, birth_year, gender, height, weight)

        db.print_records("원본 데이터")

        # 2. 4가지 파일 형식으로 저장
        db.save_json()
        db.save_csv()
        db.save_txt()
        db.save_pickle()
        print(f"\n4가지 형식으로 저장 완료 → {db.data_dir} (임시 폴더)")

        # 3. 각 파일을 읽어 출력하고 원본과 비교
        original = list(db.records)
        formats = [
            ("JSON", "load_json"),
            ("CSV", "load_csv"),
            ("TXT", "load_txt"),
            ("Pickle", "load_pickle"),
        ]

        results = []
        for fmt, method_name in formats:
            loaded_db = HealthDB(temp_dir)
            getattr(loaded_db, method_name)()
            loaded_db.print_records(f"{fmt} 파일에서 읽은 데이터")
            results.append((fmt, loaded_db.records == original))

    # 4. 검증 결과 요약
    print("\n[검증 결과]")
    for fmt, ok in results:
        print(f"  {fmt:<7}: {'일치' if ok else '불일치'}")

    if all(ok for _, ok in results):
        print("\n모든 파일의 데이터가 원본과 일치합니다.")
    else:
        print("\n일부 파일의 데이터가 원본과 다릅니다.")


# [AI 사용]
# - AI 종류   : Claude (Claude Code)
# - 사용 목적 : 13주차 모듈 3 GUI를 기본 실행으로 하고, 콘솔 APP·모듈 1 검증은 인자로 선택
# - 프롬프트  : "리드미를 읽고 모듈 3을 완성해줘", "메인함수를 실행하면 gui가 실행이 안돼"
# - 사용자    : Yunjongha
# - 날짜      : 2026-11-24
def main():
    """실행 인자에 따라 GUI / 콘솔 APP / 모듈 1 검증 중 하나를 실행한다."""
    mode = sys.argv[1] if len(sys.argv) > 1 else "gui"   # 인자가 없으면 GUI

    if mode == "module1":
        test_module1()
    elif mode == "console":
        run_console()
    elif mode in ("gui", "module3"):
        run_gui()
    else:
        print(f"알 수 없는 실행 모드입니다: {mode}")
        print("사용법: python main.py [gui | module3 | console | module1]")


if __name__ == "__main__":
    main()

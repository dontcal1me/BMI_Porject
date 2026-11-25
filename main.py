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
#
# [AI 사용]
# - AI 종류   : Claude (Claude Code)
# - 사용 목적 : 1학년 수준 리팩토링 (getattr 동적 호출 제거, 형식별 검증을 순서대로 작성)
# - 프롬프트  : "현제 작성된 코드를 컴퓨터공학과 1학년 대학생 수준으로 전면 리팩토링해줘"
# - 사용자    : Yunjongha
# - 날짜      : 2026-11-25
def to_dict_list(records):
    """레코드 리스트를 딕셔너리 리스트로 바꾼다. (두 목록이 같은지 비교할 때 사용)"""
    result = []
    for r in records:
        result.append(r.to_dict())
    return result


def test_module1():
    """모듈 1 검증: 샘플 데이터를 4가지 형식으로 저장하고 다시 읽어 원본과 비교한다.

    실제 data 폴더를 덮어쓰지 않도록 임시 폴더에 저장하고, 끝나면 임시 폴더는 삭제된다.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. 임의의 데이터 입력 후 출력
        db = HealthDB(temp_dir)
        db.add_record("홍길동", 1995, "남", 175.0, 72.5)
        db.add_record("김영희", 1998, "여", 162.0, 52.0)
        db.add_record("이철수", 1988, "남", 180.0, 95.0)
        db.add_record("박민지", 2001, "여", 158.0, 44.0)
        db.add_record("최준호", 1992, "남", 170.0, 70.0)
        db.print_records("원본 데이터")
        original = to_dict_list(db.records)

        # 2. 4가지 파일 형식으로 저장
        db.save_json()
        db.save_csv()
        db.save_txt()
        db.save_pickle()
        print("\n4가지 형식으로 저장 완료 (임시 폴더)")

        # 3. 각 파일을 새 HealthDB로 읽어서 원본과 비교
        results = {}

        loaded = HealthDB(temp_dir)
        loaded.load_json()
        loaded.print_records("JSON 파일에서 읽은 데이터")
        results["JSON"] = to_dict_list(loaded.records) == original

        loaded = HealthDB(temp_dir)
        loaded.load_csv()
        loaded.print_records("CSV 파일에서 읽은 데이터")
        results["CSV"] = to_dict_list(loaded.records) == original

        loaded = HealthDB(temp_dir)
        loaded.load_txt()
        loaded.print_records("TXT 파일에서 읽은 데이터")
        results["TXT"] = to_dict_list(loaded.records) == original

        loaded = HealthDB(temp_dir)
        loaded.load_pickle()
        loaded.print_records("Pickle 파일에서 읽은 데이터")
        results["Pickle"] = to_dict_list(loaded.records) == original

    # 4. 검증 결과 요약
    print("\n[검증 결과]")
    all_ok = True
    for fmt in results:
        if results[fmt]:
            print(f"  {fmt:<7}: 일치")
        else:
            print(f"  {fmt:<7}: 불일치")
            all_ok = False

    if all_ok:
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

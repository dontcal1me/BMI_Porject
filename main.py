"""
BMI 건강관리 프로그램 - 실행 진입점

11주차(모듈 1) 검증:
1. 임의의 건강정보 레코드를 입력하고 화면에 출력한다.
2. 이 데이터를 JSON / CSV / TXT / Pickle 4가지 파일로 저장한다.
3. 저장된 파일을 각각 다시 읽어 출력하고, 원래 정보와 일치하는지 검증한다.
"""

# [AI 사용]
# - AI 종류   : Claude (Claude Code)
# - 사용 목적 : 모듈 1 저장/읽기 결과를 검증하는 main() 작성
# - 프롬프트  : "main()에서 저장하기 전 값과 저장된 값을 읽어서 일치하는지 검증해줘"
# - 사용자    : Yunjongha
# - 날짜      : 2026-11-11

from modules.health_db import HealthDB


def main():
    # 1. 임의의 데이터 입력 후 출력
    db = HealthDB()
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
    print(f"\n4가지 형식으로 저장 완료 → {db.data_dir}")

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
        loaded_db = HealthDB()
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


if __name__ == "__main__":
    main()

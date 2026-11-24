"""
모듈 2: 비즈니스 로직 (health_logic.py)

- HealthManager : 모듈 1(HealthDB)을 이용해 건강정보 레코드의
                  등록(중복 체크) / 조회·검색 / 수정(BMI 재계산) / 삭제 / 통계를 처리하는 클래스
- run_console   : HealthManager 기능을 시험하기 위한 콘솔 APP

모든 변경(등록·수정·삭제)은 성공하면 즉시 파일에 저장(동기화)된다.
잘못된 입력은 ValueError(사용자에게 보여줄 메시지 포함)로 알려주므로,
GUI(모듈 3)에서는 try-except로 잡아 messagebox에 메시지를 그대로 띄우면 된다.
"""

# [AI 사용]
# - AI 종류   : Claude (Claude Code)
# - 사용 목적 : 모듈 2(HealthManager 클래스: CRUD, 중복 체크, 검색, BMI 재계산, 통계, CSV 일괄 등록) 및 콘솔 테스트 APP 작성
# - 프롬프트  : "리드미를 읽고 모듈 2를 제작해줘"
# - 사용자    : Yunjongha
# - 날짜      : 2026-11-18 

import csv
from datetime import datetime

try:
    from modules.health_db import HealthDB, HealthRecord
except ImportError:  # modules 폴더 안에서 직접 실행할 때
    from health_db import HealthDB, HealthRecord

GENDERS = ("남", "여")
STATUSES = ("저체중", "정상", "과체중", "비만")


class HealthManager:
    """건강정보 관리의 핵심 비즈니스 로직을 담당하는 클래스."""

    # 파일 형식 → (저장 메서드 이름, 읽기 메서드 이름)
    FORMATS = {
        "json": ("save_json", "load_json"),
        "csv": ("save_csv", "load_csv"),
        "txt": ("save_txt", "load_txt"),
        "pickle": ("save_pickle", "load_pickle"),
    }

    def __init__(self, db=None, file_format="json", autoload=True):
        """db를 지정하지 않으면 기본 data 폴더를 쓰는 HealthDB를 만든다.

        autoload=True이면 시작할 때 file_format 파일에서 레코드를 읽어온다.
        """
        self.db = db if db is not None else HealthDB()
        self.file_format = self._check_format(file_format)
        if autoload:
            self.load()

    # ------------------------------------------------------------
    # 파일 동기화
    # ------------------------------------------------------------
    def _check_format(self, file_format):
        file_format = str(file_format).lower()
        if file_format not in self.FORMATS:
            raise ValueError(f"지원하지 않는 파일 형식입니다: {file_format} "
                             f"(가능: {', '.join(self.FORMATS)})")
        return file_format

    def set_format(self, file_format):
        """기본 저장/읽기 파일 형식을 바꾼다."""
        self.file_format = self._check_format(file_format)

    def load(self, file_format=None):
        """지정한 형식(없으면 현재 형식)의 파일에서 레코드를 읽어온다."""
        fmt = self._check_format(file_format or self.file_format)
        return getattr(self.db, self.FORMATS[fmt][1])()

    def save(self, file_format=None):
        """지정한 형식(없으면 현재 형식)의 파일로 레코드를 저장한다. 성공 여부를 반환."""
        fmt = self._check_format(file_format or self.file_format)
        return getattr(self.db, self.FORMATS[fmt][0])()

    def save_all(self):
        """4가지 형식 모두로 저장한다. {형식: 성공여부} 딕셔너리를 반환."""
        return {fmt: self.save(fmt) for fmt in self.FORMATS}

    # ------------------------------------------------------------
    # 입력값 검증
    # ------------------------------------------------------------
    @staticmethod
    def validate(name, birth_year, gender, height, weight):
        """입력값을 검사하고 알맞은 타입으로 변환해 반환한다.

        문제가 있으면 사용자에게 보여줄 메시지를 담은 ValueError를 발생시킨다.
        """
        name = str(name).strip()
        if not name:
            raise ValueError("이름을 입력하세요.")

        try:
            birth_year = int(str(birth_year).strip())
        except ValueError:
            raise ValueError("생년은 정수(예: 1995)로 입력하세요.")
        this_year = datetime.now().year
        if not 1900 <= birth_year <= this_year:
            raise ValueError(f"생년은 1900 ~ {this_year} 사이로 입력하세요.")

        gender = str(gender).strip()
        if gender not in GENDERS:
            raise ValueError("성별은 '남' 또는 '여'로 입력하세요.")

        try:
            height = float(str(height).strip())
            weight = float(str(weight).strip())
        except ValueError:
            raise ValueError("키와 몸무게는 숫자로 입력하세요.")
        if not 0 < height <= 300:
            raise ValueError("키는 0보다 크고 300cm 이하인 숫자로 입력하세요.")
        if not 0 < weight <= 500:
            raise ValueError("몸무게는 0보다 크고 500kg 이하인 숫자로 입력하세요.")

        return name, birth_year, gender, height, weight

    # ------------------------------------------------------------
    # F1.1 / F1.3 등록 및 중복 체크
    # ------------------------------------------------------------
    def is_duplicate(self, name, birth_year, gender, exclude_id=None):
        """이름·생년·성별이 모두 같은 레코드가 이미 있으면 True.

        exclude_id: 수정할 때 자기 자신은 비교에서 제외하기 위해 사용.
        """
        for r in self.db.records:
            if r.id == exclude_id:
                continue
            if (r.name, r.birth_year, r.gender) == (name, birth_year, gender):
                return True
        return False

    def add(self, name, birth_year, gender, height, weight, save=True):
        """새 레코드를 등록하고 반환한다. 식별번호는 자동 생성된다.

        입력값이 잘못되었거나 중복이면 ValueError를 발생시킨다.
        """
        name, birth_year, gender, height, weight = self.validate(
            name, birth_year, gender, height, weight)
        if self.is_duplicate(name, birth_year, gender):
            raise ValueError(f"이미 등록된 사람입니다: {name} ({birth_year}, {gender})")

        record = self.db.add_record(name, birth_year, gender, height, weight)
        if save:
            self.save()
        return record

    # ------------------------------------------------------------
    # F1.2 CSV 파일 일괄 등록
    # ------------------------------------------------------------
    def import_csv(self, path):
        """외부 CSV 파일의 여러 행을 한 번에 등록한다.

        필요한 열: name, birth_year, gender, height, weight (id/bmi/status 열은 무시하고 새로 계산)
        반환값: (등록된 레코드 리스트, [(행 번호, 실패 사유), ...])
        """
        added, failed = [], []
        try:
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                required = {"name", "birth_year", "gender", "height", "weight"}
                missing = required - set(reader.fieldnames or [])
                if missing:
                    raise ValueError(f"CSV에 필요한 열이 없습니다: {', '.join(sorted(missing))}")
                # 첫 행은 헤더이므로 데이터는 2행부터
                for line_no, row in enumerate(reader, start=2):
                    try:
                        added.append(self.add(row["name"], row["birth_year"], row["gender"],
                                              row["height"], row["weight"], save=False))
                    except ValueError as e:
                        failed.append((line_no, str(e)))
        except (OSError, UnicodeDecodeError, csv.Error) as e:
            raise ValueError(f"CSV 파일을 읽을 수 없습니다: {e}")

        if added:
            self.save()
        return added, failed

    # ------------------------------------------------------------
    # F1.4 ~ F1.6 조회 및 검색
    # ------------------------------------------------------------
    def get_all(self):
        """전체 레코드 리스트(복사본)를 반환한다."""
        return list(self.db.records)

    def find_by_id(self, record_id):
        """식별번호로 레코드를 찾아 반환한다. 없으면 None."""
        record_id = str(record_id).strip().upper()
        for r in self.db.records:
            if r.id.upper() == record_id:
                return r
        return None

    def search(self, name=None, record_id=None, status=None, gender=None):
        """조건에 맞는 레코드 리스트를 반환한다. (지정한 조건은 모두 만족해야 함)

        - name      : 이름 일부만 입력해도 검색 (부분 일치)
        - record_id : 식별번호 일부만 입력해도 검색 (대소문자 무시)
        - status    : 비만도 상태 (저체중/정상/과체중/비만)
        - gender    : 성별 (남/여)
        """
        results = []
        for r in self.db.records:
            if name and name.strip() not in r.name:
                continue
            if record_id and record_id.strip().upper() not in r.id.upper():
                continue
            if status and r.status != status.strip():
                continue
            if gender and r.gender != gender.strip():
                continue
            results.append(r)
        return results

    # ------------------------------------------------------------
    # F1.7 수정 및 BMI 재계산
    # ------------------------------------------------------------
    def update(self, record_id, **changes):
        """식별번호로 레코드를 찾아 정보를 수정하고, 수정된 레코드를 반환한다.

        수정 가능한 키: name, birth_year, gender, height, weight
        값이 None이거나 빈 문자열인 항목은 기존 값을 유지한다.
        키나 몸무게가 바뀌면 BMI와 비만도 상태가 자동으로 다시 계산된다.
        """
        record = self.find_by_id(record_id)
        if record is None:
            raise ValueError(f"식별번호 {record_id} 인 레코드가 없습니다.")

        allowed = ("name", "birth_year", "gender", "height", "weight")
        unknown = set(changes) - set(allowed)
        if unknown:
            raise ValueError(f"수정할 수 없는 항목입니다: {', '.join(sorted(unknown))}")

        # 바뀌지 않는 항목은 기존 값으로 채운 뒤 전체를 다시 검증
        merged = {}
        for key in allowed:
            value = changes.get(key)
            merged[key] = getattr(record, key) if value is None or str(value).strip() == "" else value
        name, birth_year, gender, height, weight = self.validate(**merged)

        if self.is_duplicate(name, birth_year, gender, exclude_id=record.id):
            raise ValueError(f"같은 정보의 사람이 이미 있습니다: {name} ({birth_year}, {gender})")

        record.name = name
        record.birth_year = birth_year
        record.gender = gender
        record.height = height
        record.weight = weight
        record.calculate_bmi()  # BMI, 비만도 재계산
        self.save()
        return record

    # ------------------------------------------------------------
    # F1.8 삭제
    # ------------------------------------------------------------
    def delete(self, record_id):
        """식별번호로 레코드를 삭제하고 파일에 반영한다. 삭제된 레코드를 반환."""
        record = self.find_by_id(record_id)
        if record is None:
            raise ValueError(f"식별번호 {record_id} 인 레코드가 없습니다.")
        self.db.records.remove(record)
        self.save()
        return record

    # ------------------------------------------------------------
    # F2.1 통계
    # ------------------------------------------------------------
    def get_statistics(self, records=None):
        """요약 통계를 딕셔너리로 반환한다. records를 주면 그 목록만 대상으로 계산.

        반환 키: count, avg_height, avg_weight, avg_bmi, max_bmi, min_bmi,
                 status_counts {상태: 인원}, gender_counts {성별: 인원}
        레코드가 없으면 평균/최대/최소 값은 0.0이다.
        """
        records = self.db.records if records is None else records
        count = len(records)
        stats = {
            "count": count,
            "avg_height": 0.0,
            "avg_weight": 0.0,
            "avg_bmi": 0.0,
            "max_bmi": 0.0,
            "min_bmi": 0.0,
            "status_counts": {s: 0 for s in STATUSES},
            "gender_counts": {g: 0 for g in GENDERS},
        }
        if count == 0:
            return stats

        bmis = [r.bmi for r in records]
        stats["avg_height"] = round(sum(r.height for r in records) / count, 2)
        stats["avg_weight"] = round(sum(r.weight for r in records) / count, 2)
        stats["avg_bmi"] = round(sum(bmis) / count, 2)
        stats["max_bmi"] = max(bmis)
        stats["min_bmi"] = min(bmis)
        for r in records:
            stats["status_counts"][r.status] = stats["status_counts"].get(r.status, 0) + 1
            stats["gender_counts"][r.gender] = stats["gender_counts"].get(r.gender, 0) + 1
        return stats


# ================================================================
# 콘솔 APP (모듈 2 테스트용)
# ================================================================
def print_table(records, title="건강정보 목록"):
    """레코드 리스트를 표 형태로 출력한다."""
    print(f"\n[{title}] (총 {len(records)}명)")
    print("-" * 78)
    print(f"{'식별번호':<11}{'이름':<6}{'생년':>6}{'성별':>4}"
          f"{'키(cm)':>9}{'몸무게(kg)':>11}{'BMI':>8}  {'상태'}")
    print("-" * 78)
    for r in records:
        print(f"{r.id:<15}{r.name:<6}{r.birth_year:>8}{r.gender:>5}"
              f"{r.height:>10.1f}{r.weight:>12.1f}{r.bmi:>10.2f}  {r.status}")
    print("-" * 78)


def print_detail(r):
    """한 사람의 정보를 상세하게 출력한다."""
    age = datetime.now().year - r.birth_year
    print("\n[상세 정보]")
    print(f"  식별번호 : {r.id}")
    print(f"  이름     : {r.name}")
    print(f"  생년     : {r.birth_year} (만 {age}세 내외)")
    print(f"  성별     : {r.gender}")
    print(f"  키       : {r.height:.1f} cm")
    print(f"  몸무게   : {r.weight:.1f} kg")
    print(f"  BMI      : {r.bmi:.2f}")
    print(f"  비만도   : {r.status}")


def print_statistics(stats):
    """통계 딕셔너리를 보기 좋게 출력한다."""
    print("\n[건강정보 통계]")
    print(f"  총 인원수     : {stats['count']}명")
    if stats["count"] == 0:
        return
    print(f"  평균 키       : {stats['avg_height']:.2f} cm")
    print(f"  평균 몸무게   : {stats['avg_weight']:.2f} kg")
    print(f"  평균 BMI      : {stats['avg_bmi']:.2f}")
    print(f"  최대/최소 BMI : {stats['max_bmi']:.2f} / {stats['min_bmi']:.2f}")
    print("  비만도 분포   :")
    for status, n in stats["status_counts"].items():
        bar = "■" * n
        print(f"    {status:<4} {n:>3}명 {bar}")
    genders = ", ".join(f"{g} {n}명" for g, n in stats["gender_counts"].items())
    print(f"  성별 분포     : {genders}")


def _ask_record_id(manager):
    """식별번호를 입력받아 레코드를 반환한다. 없으면 None."""
    record_id = input("식별번호 입력 (예: P2026-0001): ").strip()
    record = manager.find_by_id(record_id)
    if record is None:
        print(f"[알림] 식별번호 '{record_id}' 인 레코드가 없습니다.")
    return record


def run_console(manager=None):
    """메뉴를 반복 출력하며 사용자의 선택에 따라 기능을 실행한다."""
    manager = manager if manager is not None else HealthManager()
    menu = """
========== BMI 건강관리 (콘솔) ==========
 1. 건강정보 등록         2. CSV 파일 일괄 등록
 3. 전체 목록 보기        4. 검색하기
 5. 상세 보기             6. 정보 수정
 7. 정보 삭제             8. 통계 보기
 9. 저장 형식 변경        10. 4가지 형식 모두 저장
 0. 종료
=========================================="""

    while True:
        print(menu)
        print(f"(현재 저장 형식: {manager.file_format}, 등록 인원: {len(manager.db.records)}명)")
        choice = input("메뉴 선택: ").strip()

        try:
            if choice == "1":
                print("\n[건강정보 등록]")
                record = manager.add(
                    input("이름: "), input("생년(예: 1995): "), input("성별(남/여): "),
                    input("키(cm): "), input("몸무게(kg): "))
                print(f"[완료] 등록되었습니다. 식별번호: {record.id}, "
                      f"BMI: {record.bmi:.2f} ({record.status})")

            elif choice == "2":
                path = input("CSV 파일 경로: ").strip().strip('"')
                added, failed = manager.import_csv(path)
                print(f"[완료] {len(added)}명 등록, {len(failed)}건 실패")
                for line_no, reason in failed:
                    print(f"  - {line_no}행: {reason}")

            elif choice == "3":
                print_table(manager.get_all(), "전체 목록")

            elif choice == "4":
                print("\n[검색] 조건을 입력하세요. (건너뛰려면 Enter)")
                results = manager.search(
                    name=input("이름(일부): "),
                    record_id=input("식별번호(일부): "),
                    status=input("비만도(저체중/정상/과체중/비만): "),
                    gender=input("성별(남/여): "))
                print_table(results, "검색 결과")

            elif choice == "5":
                record = _ask_record_id(manager)
                if record:
                    print_detail(record)

            elif choice == "6":
                record = _ask_record_id(manager)
                if record:
                    print_detail(record)
                    print("\n수정할 값을 입력하세요. (그대로 두려면 Enter)")
                    record = manager.update(
                        record.id,
                        name=input(f"이름 [{record.name}]: "),
                        birth_year=input(f"생년 [{record.birth_year}]: "),
                        gender=input(f"성별 [{record.gender}]: "),
                        height=input(f"키 [{record.height}]: "),
                        weight=input(f"몸무게 [{record.weight}]: "))
                    print(f"[완료] 수정되었습니다. BMI: {record.bmi:.2f} ({record.status})")

            elif choice == "7":
                record = _ask_record_id(manager)
                if record:
                    answer = input(f"'{record.name}({record.id})' 을(를) 삭제할까요? (y/n): ")
                    if answer.strip().lower() == "y":
                        manager.delete(record.id)
                        print("[완료] 삭제되었습니다.")
                    else:
                        print("[취소] 삭제하지 않았습니다.")

            elif choice == "8":
                print_statistics(manager.get_statistics())

            elif choice == "9":
                fmt = input(f"저장 형식 ({'/'.join(manager.FORMATS)}): ")
                manager.set_format(fmt)
                if input("이 형식의 파일에서 데이터를 다시 불러올까요? (y/n): ").strip().lower() == "y":
                    manager.load()
                print(f"[완료] 저장 형식: {manager.file_format}")

            elif choice == "10":
                for fmt, ok in manager.save_all().items():
                    print(f"  {fmt:<7}: {'성공' if ok else '실패'}")

            elif choice == "0":
                print("프로그램을 종료합니다.")
                break

            else:
                print("[알림] 메뉴 번호를 다시 선택하세요.")

        except ValueError as e:
            print(f"[오류] {e}")


if __name__ == "__main__":
    run_console()

"""
모듈 2: 비즈니스 로직 (health_logic.py)

- HealthManager : 모듈 1(HealthDB)을 이용해
                  등록(중복 체크) / 검색 / 수정(BMI 재계산) / 삭제 / 통계 를 처리하는 클래스
- run_console   : HealthManager 기능을 시험해 보는 콘솔 APP

등록·수정·삭제가 성공하면 바로 파일에 저장한다.
입력이 잘못되면 ValueError(사용자에게 보여줄 메시지)를 발생시키므로,
GUI(모듈 3)에서는 try-except로 잡아서 메시지를 그대로 보여주면 된다.
"""

# [AI 사용]
# - AI 종류   : Claude (Claude Code)
# - 사용 목적 : 모듈 2(HealthManager 클래스: CRUD, 중복 체크, 검색, BMI 재계산, 통계, CSV 일괄 등록) 및 콘솔 테스트 APP 작성
# - 프롬프트  : "리드미를 읽고 모듈 2를 제작해줘"
# - 사용자    : Yunjongha
# - 날짜      : 2026-11-18
#
# [AI 사용]
# - AI 종류   : Claude (Claude Code)
# - 사용 목적 : 1학년 수준으로 전면 리팩토링 (getattr·**kwargs·staticmethod 제거,
#               if/elif 와 반복문 위주로 단순화, 검색/수정 함수 매개변수를 명확하게 변경)
# - 프롬프트  : "현제 작성된 코드를 컴퓨터공학과 1학년 대학생 수준으로 전면 리팩토링해줘"
# - 사용자    : Yunjongha
# - 날짜      : 2026-11-25

import csv
from datetime import datetime

from modules.health_db import HealthDB, print_table

FORMATS = ["json", "csv", "txt", "pickle"]      # 지원하는 파일 형식
GENDERS = ["남", "여"]
STATUSES = ["저체중", "정상", "과체중", "비만"]


class HealthManager:
    """건강정보 관리의 핵심 규칙을 담당하는 클래스."""

    def __init__(self, db=None):
        """db를 주지 않으면 기본 data 폴더를 쓰는 HealthDB를 만들고 JSON 파일을 읽는다."""
        if db is None:
            db = HealthDB()
        self.db = db
        self.file_format = "json"
        self.load()

    # ------------------------------------------------------------
    # 파일 저장 / 불러오기
    # ------------------------------------------------------------
    def set_format(self, file_format):
        """저장/읽기에 사용할 파일 형식을 바꾼다."""
        file_format = file_format.strip().lower()
        if file_format not in FORMATS:
            raise ValueError(f"지원하지 않는 파일 형식입니다: {file_format}")
        self.file_format = file_format

    def load(self):
        """현재 형식의 파일에서 레코드를 읽어온다."""
        if self.file_format == "json":
            return self.db.load_json()
        elif self.file_format == "csv":
            return self.db.load_csv()
        elif self.file_format == "txt":
            return self.db.load_txt()
        else:
            return self.db.load_pickle()

    def save(self):
        """현재 형식의 파일로 저장한다. 성공하면 True."""
        if self.file_format == "json":
            return self.db.save_json()
        elif self.file_format == "csv":
            return self.db.save_csv()
        elif self.file_format == "txt":
            return self.db.save_txt()
        else:
            return self.db.save_pickle()

    def save_all(self):
        """4가지 형식 모두로 저장한다. 결과는 {형식: 성공여부} 딕셔너리."""
        return {
            "json": self.db.save_json(),
            "csv": self.db.save_csv(),
            "txt": self.db.save_txt(),
            "pickle": self.db.save_pickle(),
        }

    # ------------------------------------------------------------
    # 입력값 검사
    # ------------------------------------------------------------
    def check_input(self, name, birth_year, gender, height, weight):
        """입력값(문자열)을 검사하고, 알맞은 자료형으로 바꿔서 돌려준다.

        문제가 있으면 사용자에게 보여줄 메시지와 함께 ValueError를 발생시킨다.
        """
        name = str(name).strip()
        if name == "":
            raise ValueError("이름을 입력하세요.")

        try:
            birth_year = int(birth_year)
        except ValueError:
            raise ValueError("생년은 정수(예: 1995)로 입력하세요.")
        this_year = datetime.now().year
        if birth_year < 1900 or birth_year > this_year:
            raise ValueError(f"생년은 1900 ~ {this_year} 사이로 입력하세요.")

        gender = str(gender).strip()
        if gender not in GENDERS:
            raise ValueError("성별은 '남' 또는 '여'로 입력하세요.")

        try:
            height = float(height)
            weight = float(weight)
        except ValueError:
            raise ValueError("키와 몸무게는 숫자로 입력하세요.")
        if height <= 0 or height > 300:
            raise ValueError("키는 0보다 크고 300cm 이하로 입력하세요.")
        if weight <= 0 or weight > 500:
            raise ValueError("몸무게는 0보다 크고 500kg 이하로 입력하세요.")

        return name, birth_year, gender, height, weight

    # ------------------------------------------------------------
    # F1.1 / F1.3 등록 + 중복 체크
    # ------------------------------------------------------------
    def is_duplicate(self, name, birth_year, gender, skip_id=""):
        """이름·생년·성별이 모두 같은 사람이 있으면 True.

        skip_id : 수정할 때 자기 자신은 비교하지 않도록 건너뛸 식별번호
        """
        for r in self.db.records:
            if r.id == skip_id:
                continue
            if r.name == name and r.birth_year == birth_year and r.gender == gender:
                return True
        return False

    def add(self, name, birth_year, gender, height, weight, save=True):
        """새 사람을 등록하고 그 레코드를 돌려준다. 식별번호는 자동으로 만들어진다."""
        name, birth_year, gender, height, weight = self.check_input(
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
        """CSV 파일의 여러 사람을 한 번에 등록한다.

        CSV에 name, birth_year, gender, height, weight 열이 있어야 한다.
        돌려주는 값: (등록된 레코드 리스트, 실패 메시지 리스트)
        """
        # 1) 파일을 읽어서 행(딕셔너리)들을 리스트에 담는다
        try:
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                columns = reader.fieldnames or []
        except Exception as e:
            raise ValueError(f"CSV 파일을 읽을 수 없습니다: {e}")

        # 2) 꼭 필요한 열이 있는지 확인한다
        for col in ["name", "birth_year", "gender", "height", "weight"]:
            if col not in columns:
                raise ValueError(f"CSV에 '{col}' 열이 없습니다.")

        # 3) 한 줄씩 등록한다. 실패한 줄은 이유를 기록하고 계속 진행
        added = []
        failed = []
        line_no = 1                        # 1행은 헤더
        for row in rows:
            line_no += 1
            try:
                record = self.add(row["name"], row["birth_year"], row["gender"],
                                  row["height"], row["weight"], save=False)
                added.append(record)
            except ValueError as e:
                failed.append(f"{line_no}행: {e}")

        if len(added) > 0:
            self.save()                    # 다 등록한 뒤 한 번만 저장
        return added, failed

    # ------------------------------------------------------------
    # F1.4 ~ F1.6 조회 / 검색
    # ------------------------------------------------------------
    def get_all(self):
        """전체 레코드 리스트를 돌려준다."""
        return self.db.records

    def find_by_id(self, record_id):
        """식별번호가 정확히 같은 레코드를 찾는다. 없으면 None."""
        record_id = record_id.strip().upper()
        for r in self.db.records:
            if r.id.upper() == record_id:
                return r
        return None

    def search(self, keyword="", status=""):
        """조건에 맞는 레코드 리스트를 돌려준다.

        keyword : 이름 또는 식별번호에 이 글자가 들어 있으면 찾는다 (빈 값이면 조건 없음)
        status  : 비만도(저체중/정상/과체중/비만)가 같은 사람만 찾는다 (빈 값이면 조건 없음)
        """
        keyword = keyword.strip()
        status = status.strip()

        results = []
        for r in self.db.records:
            if keyword != "":
                in_name = keyword in r.name
                in_id = keyword.upper() in r.id.upper()
                if not in_name and not in_id:
                    continue
            if status != "" and r.status != status:
                continue
            results.append(r)
        return results

    # ------------------------------------------------------------
    # F1.7 수정 + BMI 재계산
    # ------------------------------------------------------------
    def update(self, record_id, name, birth_year, gender, height, weight):
        """식별번호로 사람을 찾아 정보를 바꾸고, 바뀐 레코드를 돌려준다.

        빈 칸으로 넘어온 항목은 원래 값을 그대로 사용한다.
        """
        record = self.find_by_id(record_id)
        if record is None:
            raise ValueError(f"식별번호 {record_id} 인 사람이 없습니다.")

        # 빈 칸이면 원래 값 사용
        if str(name).strip() == "":
            name = record.name
        if str(birth_year).strip() == "":
            birth_year = record.birth_year
        if str(gender).strip() == "":
            gender = record.gender
        if str(height).strip() == "":
            height = record.height
        if str(weight).strip() == "":
            weight = record.weight

        name, birth_year, gender, height, weight = self.check_input(
            name, birth_year, gender, height, weight)

        if self.is_duplicate(name, birth_year, gender, skip_id=record.id):
            raise ValueError(f"같은 정보의 사람이 이미 있습니다: {name} ({birth_year}, {gender})")

        record.name = name
        record.birth_year = birth_year
        record.gender = gender
        record.height = height
        record.weight = weight
        record.calculate_bmi()       # 키·몸무게가 바뀌었을 수 있으니 BMI 다시 계산
        self.save()
        return record

    # ------------------------------------------------------------
    # F1.8 삭제
    # ------------------------------------------------------------
    def delete(self, record_id):
        """식별번호로 사람을 찾아 삭제하고 파일에 저장한다."""
        record = self.find_by_id(record_id)
        if record is None:
            raise ValueError(f"식별번호 {record_id} 인 사람이 없습니다.")
        self.db.records.remove(record)
        self.save()
        return record

    # ------------------------------------------------------------
    # F2.1 통계
    # ------------------------------------------------------------
    def get_statistics(self):
        """요약 통계를 딕셔너리로 돌려준다.

        키: count, avg_height, avg_weight, avg_bmi, max_bmi, min_bmi,
            status_counts {비만도: 인원}, gender_counts {성별: 인원}
        """
        records = self.db.records
        count = len(records)

        status_counts = {"저체중": 0, "정상": 0, "과체중": 0, "비만": 0}
        gender_counts = {"남": 0, "여": 0}
        stats = {
            "count": count,
            "avg_height": 0.0,
            "avg_weight": 0.0,
            "avg_bmi": 0.0,
            "max_bmi": 0.0,
            "min_bmi": 0.0,
            "status_counts": status_counts,
            "gender_counts": gender_counts,
        }
        if count == 0:              # 0으로 나누지 않도록 먼저 확인
            return stats

        total_height = 0
        total_weight = 0
        total_bmi = 0
        max_bmi = records[0].bmi
        min_bmi = records[0].bmi

        for r in records:
            total_height += r.height
            total_weight += r.weight
            total_bmi += r.bmi
            if r.bmi > max_bmi:
                max_bmi = r.bmi
            if r.bmi < min_bmi:
                min_bmi = r.bmi
            if r.status in status_counts:
                status_counts[r.status] += 1
            if r.gender in gender_counts:
                gender_counts[r.gender] += 1

        stats["avg_height"] = round(total_height / count, 2)
        stats["avg_weight"] = round(total_weight / count, 2)
        stats["avg_bmi"] = round(total_bmi / count, 2)
        stats["max_bmi"] = max_bmi
        stats["min_bmi"] = min_bmi
        return stats


# ================================================================
# 콘솔 APP (모듈 2 테스트용)
# ================================================================
def print_detail(r):
    """한 사람의 정보를 자세히 출력한다."""
    age = datetime.now().year - r.birth_year
    print("\n[상세 정보]")
    print(f"  식별번호 : {r.id}")
    print(f"  이름     : {r.name}")
    print(f"  생년     : {r.birth_year} (약 {age}세)")
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
    for status in STATUSES:
        n = stats["status_counts"][status]
        print(f"    {status:<4} {n:>3}명 " + "■" * n)
    print(f"  성별 분포     : 남 {stats['gender_counts']['남']}명, "
          f"여 {stats['gender_counts']['여']}명")


def ask_record(manager):
    """식별번호를 입력받아 레코드를 찾는다. 없으면 None."""
    record_id = input("식별번호 입력 (예: P2026-0001): ")
    record = manager.find_by_id(record_id)
    if record is None:
        print(f"[알림] 식별번호 '{record_id}' 인 사람이 없습니다.")
    return record


def run_console():
    """메뉴를 반복해서 보여주고, 고른 번호에 따라 기능을 실행한다."""
    manager = HealthManager()
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
        print(f"(현재 저장 형식: {manager.file_format}, 등록 인원: {len(manager.get_all())}명)")
        choice = input("메뉴 선택: ").strip()

        try:
            if choice == "1":
                print("\n[건강정보 등록]")
                name = input("이름: ")
                birth_year = input("생년(예: 1995): ")
                gender = input("성별(남/여): ")
                height = input("키(cm): ")
                weight = input("몸무게(kg): ")
                record = manager.add(name, birth_year, gender, height, weight)
                print(f"[완료] 등록되었습니다. 식별번호: {record.id}, "
                      f"BMI: {record.bmi:.2f} ({record.status})")

            elif choice == "2":
                path = input("CSV 파일 경로: ").strip().strip('"')
                added, failed = manager.import_csv(path)
                print(f"[완료] {len(added)}명 등록, {len(failed)}건 실패")
                for message in failed:
                    print("  - " + message)

            elif choice == "3":
                print_table(manager.get_all(), "전체 목록")

            elif choice == "4":
                print("\n[검색] 조건을 입력하세요. (건너뛰려면 Enter)")
                keyword = input("이름 또는 식별번호(일부): ")
                status = input("비만도(저체중/정상/과체중/비만): ")
                print_table(manager.search(keyword, status), "검색 결과")

            elif choice == "5":
                record = ask_record(manager)
                if record is not None:
                    print_detail(record)

            elif choice == "6":
                record = ask_record(manager)
                if record is not None:
                    print_detail(record)
                    print("\n수정할 값을 입력하세요. (그대로 두려면 Enter)")
                    name = input(f"이름 [{record.name}]: ")
                    birth_year = input(f"생년 [{record.birth_year}]: ")
                    gender = input(f"성별 [{record.gender}]: ")
                    height = input(f"키 [{record.height}]: ")
                    weight = input(f"몸무게 [{record.weight}]: ")
                    record = manager.update(record.id, name, birth_year, gender, height, weight)
                    print(f"[완료] 수정되었습니다. BMI: {record.bmi:.2f} ({record.status})")

            elif choice == "7":
                record = ask_record(manager)
                if record is not None:
                    answer = input(f"'{record.name}({record.id})' 을(를) 삭제할까요? (y/n): ")
                    if answer.strip().lower() == "y":
                        manager.delete(record.id)
                        print("[완료] 삭제되었습니다.")
                    else:
                        print("[취소] 삭제하지 않았습니다.")

            elif choice == "8":
                print_statistics(manager.get_statistics())

            elif choice == "9":
                manager.set_format(input("저장 형식 (json/csv/txt/pickle): "))
                answer = input("이 형식의 파일에서 데이터를 다시 불러올까요? (y/n): ")
                if answer.strip().lower() == "y":
                    manager.load()
                print(f"[완료] 저장 형식: {manager.file_format}")

            elif choice == "10":
                results = manager.save_all()
                for fmt in results:
                    if results[fmt]:
                        print(f"  {fmt:<7}: 성공")
                    else:
                        print(f"  {fmt:<7}: 실패")

            elif choice == "0":
                print("프로그램을 종료합니다.")
                break

            else:
                print("[알림] 메뉴 번호를 다시 선택하세요.")

        except ValueError as e:
            print(f"[오류] {e}")

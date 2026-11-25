"""
모듈 1: 데이터 & 저장소 (health_db.py)

- HealthRecord : 한 사람의 건강정보(레코드)를 담는 클래스
- HealthDB     : 레코드 목록(리스트)을 관리하고
                 JSON / CSV / TXT / Pickle 4가지 형식으로 저장·읽기 하는 클래스
"""

# [AI 사용]
# - AI 종류   : Claude (Claude Code)
# - 사용 목적 : 모듈 1(HealthRecord, HealthDB 클래스 및 4가지 파일 입출력) 작성
# - 프롬프트  : "지정프로젝트 요구사항(README)을 만족하는 모듈 1 코드를 작성해줘.
#               HealthRecord 클래스, 목록 관리 클래스, JSON/CSV/TXT/PICKLE 저장·읽기 메소드, 출력 메소드"
# - 사용자    : Yunjongha
# - 날짜      : 2026-11-11
#
# [AI 사용]
# - AI 종류   : Claude (Claude Code)
# - 사용 목적 : 1학년 수준으로 전면 리팩토링 (classmethod/staticmethod 제거,
#               식별번호 생성을 HealthDB로 이동, 반복문 위주로 단순화)
# - 프롬프트  : "현제 작성된 코드를 컴퓨터공학과 1학년 대학생 수준으로 전면 리팩토링해줘"
# - 사용자    : Yunjongha
# - 날짜      : 2026-11-25

import csv
import json
import os
import pickle
from datetime import datetime

# 파일에 저장할 항목 순서 (CSV 헤더, TXT 한 줄의 순서)
FIELDS = ["id", "name", "birth_year", "gender", "height", "weight", "bmi", "status"]

# 데이터 폴더 위치: 이 파일(modules/health_db.py)의 한 단계 위 폴더 안의 data 폴더
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(MODULE_DIR), "data")


class HealthRecord:
    """한 사람의 건강정보. 만들 때 BMI와 비만도를 자동으로 계산한다."""

    def __init__(self, record_id, name, birth_year, gender, height, weight):
        self.id = record_id
        self.name = name
        self.birth_year = int(birth_year)
        self.gender = gender
        self.height = float(height)
        self.weight = float(weight)
        self.bmi = 0.0
        self.status = ""
        self.calculate_bmi()

    def calculate_bmi(self):
        """BMI = 몸무게(kg) / 키(m)² 를 계산하고 비만도를 정한다."""
        height_m = self.height / 100
        self.bmi = round(self.weight / (height_m * height_m), 2)

        if self.bmi < 18.5:
            self.status = "저체중"
        elif self.bmi < 23:
            self.status = "정상"
        elif self.bmi < 25:
            self.status = "과체중"
        else:
            self.status = "비만"

    def to_dict(self):
        """레코드를 딕셔너리로 바꾼다. (JSON, CSV 저장에 사용)"""
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "height": self.height,
            "weight": self.weight,
            "bmi": self.bmi,
            "status": self.status,
        }

    def __repr__(self):
        return f"HealthRecord({self.id}, {self.name}, {self.height}, {self.weight})"


def dict_to_record(data):
    """딕셔너리 하나를 HealthRecord 객체로 바꾼다. (BMI와 비만도는 다시 계산)"""
    return HealthRecord(data["id"], data["name"], data["birth_year"],
                        data["gender"], data["height"], data["weight"])


class HealthDB:
    """건강정보 레코드 목록을 관리하고 파일로 저장/읽기 하는 클래스."""

    def __init__(self, data_dir=DATA_DIR):
        self.records = []        # HealthRecord 객체들을 담는 리스트
        self.data_dir = data_dir

    # ------------------------------------------------------------
    # 레코드 관리
    # ------------------------------------------------------------
    def make_new_id(self):
        """'P연도-일련번호' 형식의 새 식별번호를 만든다. (예: P2026-0001)

        지금 목록에 있는 일련번호 중 가장 큰 값 + 1 을 사용하므로 겹치지 않는다.
        """
        max_no = 0
        for record in self.records:
            # "P2026-0007" → "-" 뒤의 "0007" → 7
            parts = record.id.split("-")
            if len(parts) == 2 and parts[1].isdigit():
                no = int(parts[1])
                if no > max_no:
                    max_no = no

        year = datetime.now().year
        return f"P{year}-{max_no + 1:04d}"

    def add_record(self, name, birth_year, gender, height, weight):
        """새 레코드를 만들어 목록에 추가하고, 그 레코드를 돌려준다."""
        new_id = self.make_new_id()
        record = HealthRecord(new_id, name, birth_year, gender, height, weight)
        self.records.append(record)
        return record

    def print_records(self, title="건강정보 목록"):
        """현재 목록을 표 모양으로 화면에 출력한다."""
        print_table(self.records, title)

    def get_path(self, filename):
        """data 폴더 안의 파일 경로를 만든다. (폴더가 없으면 만든다)"""
        os.makedirs(self.data_dir, exist_ok=True)
        return os.path.join(self.data_dir, filename)

    # ------------------------------------------------------------
    # JSON : 딕셔너리 리스트 형태로 저장
    # ------------------------------------------------------------
    def save_json(self, filename="health_data.json"):
        data = []
        for record in self.records:
            data.append(record.to_dict())

        try:
            with open(self.get_path(filename), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except OSError as e:
            print(f"[오류] JSON 저장 실패: {e}")
            return False

    def load_json(self, filename="health_data.json"):
        records = []
        try:
            with open(self.get_path(filename), "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                records.append(dict_to_record(item))
        except Exception as e:   # 파일 없음, 형식 오류 등 모든 오류
            print(f"[오류] JSON 읽기 실패: {e}")
            records = []

        self.records = records
        return self.records

    # ------------------------------------------------------------
    # CSV : 첫 줄은 헤더, 나머지는 한 줄에 한 사람
    # ------------------------------------------------------------
    def save_csv(self, filename="health_data.csv"):
        try:
            # utf-8-sig : 엑셀에서 열어도 한글이 깨지지 않게 한다
            with open(self.get_path(filename), "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDS)
                writer.writeheader()
                for record in self.records:
                    writer.writerow(record.to_dict())
            return True
        except OSError as e:
            print(f"[오류] CSV 저장 실패: {e}")
            return False

    def load_csv(self, filename="health_data.csv"):
        records = []
        try:
            with open(self.get_path(filename), "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    records.append(dict_to_record(row))
        except Exception as e:
            print(f"[오류] CSV 읽기 실패: {e}")
            records = []

        self.records = records
        return self.records

    # ------------------------------------------------------------
    # TXT : 한 줄에 한 사람, 값은 쉼표(,)로 구분
    # ------------------------------------------------------------
    def save_txt(self, filename="health_data.txt"):
        try:
            with open(self.get_path(filename), "w", encoding="utf-8") as f:
                for r in self.records:
                    values = [r.id, r.name, r.birth_year, r.gender,
                              r.height, r.weight, r.bmi, r.status]
                    line = ",".join(str(v) for v in values)
                    f.write(line + "\n")
            return True
        except OSError as e:
            print(f"[오류] TXT 저장 실패: {e}")
            return False

    def load_txt(self, filename="health_data.txt"):
        records = []
        try:
            with open(self.get_path(filename), "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line == "":          # 빈 줄은 건너뛴다
                        continue
                    values = line.split(",")
                    if len(values) != len(FIELDS):
                        raise ValueError(f"잘못된 형식의 줄: {line}")
                    # values[0]=id, [1]=name, [2]=birth_year, [3]=gender, [4]=height, [5]=weight
                    record = HealthRecord(values[0], values[1], values[2],
                                          values[3], values[4], values[5])
                    records.append(record)
        except Exception as e:
            print(f"[오류] TXT 읽기 실패: {e}")
            records = []

        self.records = records
        return self.records

    # ------------------------------------------------------------
    # Pickle : 파이썬 객체 리스트를 그대로 이진 파일로 저장
    # ------------------------------------------------------------
    def save_pickle(self, filename="health_data.pkl"):
        try:
            with open(self.get_path(filename), "wb") as f:
                pickle.dump(self.records, f)
            return True
        except Exception as e:
            print(f"[오류] Pickle 저장 실패: {e}")
            return False

    def load_pickle(self, filename="health_data.pkl"):
        """주의: Pickle은 이 프로그램이 직접 저장한 파일만 읽어야 한다."""
        try:
            with open(self.get_path(filename), "rb") as f:
                self.records = pickle.load(f)
        except Exception as e:
            print(f"[오류] Pickle 읽기 실패: {e}")
            self.records = []
        return self.records


def print_table(records, title="건강정보 목록"):
    """레코드 리스트를 표 모양으로 출력한다. (콘솔 APP과 모듈 1 검증에서 같이 사용)"""
    print(f"\n[{title}] (총 {len(records)}명)")
    print("-" * 78)
    print(f"{'식별번호':<11}{'이름':<6}{'생년':>6}{'성별':>4}"
          f"{'키(cm)':>9}{'몸무게(kg)':>11}{'BMI':>8}  {'상태'}")
    print("-" * 78)
    for r in records:
        print(f"{r.id:<15}{r.name:<6}{r.birth_year:>8}{r.gender:>5}"
              f"{r.height:>10.1f}{r.weight:>12.1f}{r.bmi:>10.2f}  {r.status}")
    print("-" * 78)

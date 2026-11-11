"""
모듈 1: 데이터 & 저장소 (health_db.py)

- HealthRecord : 한 사람의 건강정보(레코드)를 표현하는 클래스
- HealthDB     : 건강정보 레코드 목록을 관리하고 JSON / CSV / TXT / Pickle
                 4가지 파일 형식으로 저장(save) 및 로드(load)하는 클래스
"""

# [AI 사용]
# - AI 종류   : Claude (Claude Code)
# - 사용 목적 : 모듈 1(HealthRecord, HealthDB 클래스 및 4가지 파일 입출력) 작성
# - 프롬프트  : "지정프로젝트 요구사항(README)을 만족하는 모듈 1 코드를 작성해줘.
#               HealthRecord 클래스, 목록 관리 클래스, JSON/CSV/TXT/PICKLE 저장·읽기 메소드, 출력 메소드"
# - 사용자    : Yunjongha
# - 날짜      : 2026-11-11

import csv
import json
import os
import pickle
from datetime import datetime

# 파일에 저장할 필드 순서 (CSV 헤더, TXT 열 순서로 사용)
FIELDS = ["id", "name", "birth_year", "gender", "height", "weight", "bmi", "status"]

# 프로젝트 루트의 data 폴더 경로
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


class HealthRecord:
    """한 사람의 건강정보 레코드.

    키(cm)와 몸무게(kg)로 BMI와 비만도 상태를 자동으로 계산한다.
    """

    def __init__(self, id, name, birth_year, gender, height, weight):
        height = float(height)
        weight = float(weight)
        if height <= 0 or weight <= 0:
            raise ValueError("키와 몸무게는 0보다 큰 숫자여야 합니다.")

        self.id = id
        self.name = name
        self.birth_year = int(birth_year)
        self.gender = gender
        self.height = height
        self.weight = weight
        self.bmi = 0.0
        self.status = ""
        self.calculate_bmi()

    def calculate_bmi(self):
        """BMI = 몸무게(kg) / (키(m))² 를 계산하고 비만도 상태를 판정한다."""
        height_m = self.height / 100
        self.bmi = round(self.weight / (height_m ** 2), 2)
        self.status = self.judge_status(self.bmi)

    @staticmethod
    def judge_status(bmi):
        """BMI 수치로 비만도 상태(저체중 / 정상 / 과체중 / 비만)를 반환한다.

        기준 (대한비만학회): 18.5 미만 저체중, 23 미만 정상, 25 미만 과체중, 25 이상 비만
        """
        if bmi < 18.5:
            return "저체중"
        elif bmi < 23:
            return "정상"
        elif bmi < 25:
            return "과체중"
        else:
            return "비만"

    def to_dict(self):
        """레코드를 딕셔너리로 변환한다."""
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

    @classmethod
    def from_dict(cls, data):
        """딕셔너리로부터 레코드 객체를 생성한다. (BMI와 상태는 다시 계산)"""
        return cls(
            data["id"],
            data["name"],
            data["birth_year"],
            data["gender"],
            data["height"],
            data["weight"],
        )

    def __eq__(self, other):
        """두 레코드의 모든 필드 값이 같으면 같은 레코드로 본다."""
        if not isinstance(other, HealthRecord):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def __repr__(self):
        return (f"HealthRecord(id={self.id!r}, name={self.name!r}, "
                f"height={self.height}, weight={self.weight})")


class HealthDB:
    """건강정보 레코드 목록을 관리하고 파일로 저장/로드하는 클래스."""

    def __init__(self, data_dir=DATA_DIR):
        self.records = []
        self.data_dir = data_dir

    # ------------------------------------------------------------
    # 레코드 관리
    # ------------------------------------------------------------
    def generate_id(self):
        """'P연도-일련번호' 형식의 고유한 환자식별번호를 생성한다. (예: P2026-0001)"""
        year = datetime.now().year
        prefix = f"P{year}-"
        max_no = 0
        for record in self.records:
            if record.id.startswith(prefix):
                try:
                    max_no = max(max_no, int(record.id[len(prefix):]))
                except ValueError:
                    pass
        return f"{prefix}{max_no + 1:04d}"

    def add_record(self, name, birth_year, gender, height, weight):
        """새 레코드를 만들어 목록에 추가하고, 추가된 레코드를 반환한다.

        식별번호는 자동으로 생성된다.
        """
        record = HealthRecord(self.generate_id(), name, birth_year, gender, height, weight)
        self.records.append(record)
        return record

    def print_records(self, title="건강정보 목록"):
        """현재 목록의 레코드를 표 형태로 화면에 출력한다."""
        print(f"\n[{title}] (총 {len(self.records)}명)")
        print("-" * 78)
        print(f"{'식별번호':<11}{'이름':<6}{'생년':>6}{'성별':>4}"
              f"{'키(cm)':>9}{'몸무게(kg)':>11}{'BMI':>8}  {'상태'}")
        print("-" * 78)
        for r in self.records:
            print(f"{r.id:<15}{r.name:<6}{r.birth_year:>8}{r.gender:>5}"
                  f"{r.height:>10.1f}{r.weight:>12.1f}{r.bmi:>10.2f}  {r.status}")
        print("-" * 78)

    def _path(self, filename):
        """data 폴더 안의 파일 경로를 만든다. (폴더가 없으면 생성)"""
        os.makedirs(self.data_dir, exist_ok=True)
        return os.path.join(self.data_dir, filename)

    # ------------------------------------------------------------
    # JSON
    # ------------------------------------------------------------
    def save_json(self, filename="health_data.json"):
        """목록을 딕셔너리 리스트 형태로 JSON 파일에 저장한다."""
        try:
            with open(self._path(filename), "w", encoding="utf-8") as f:
                json.dump([r.to_dict() for r in self.records], f,
                          ensure_ascii=False, indent=4)
            return True
        except OSError as e:
            print(f"[오류] JSON 저장 실패: {e}")
            return False

    def load_json(self, filename="health_data.json"):
        """JSON 파일을 읽어 목록을 교체하고, 읽은 레코드 리스트를 반환한다."""
        try:
            with open(self._path(filename), "r", encoding="utf-8") as f:
                data = json.load(f)
            self.records = [HealthRecord.from_dict(d) for d in data]
        except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            print(f"[오류] JSON 읽기 실패: {e}")
            self.records = []
        return self.records

    # ------------------------------------------------------------
    # CSV
    # ------------------------------------------------------------
    def save_csv(self, filename="health_data.csv"):
        """목록을 첫 행에 헤더가 있는 CSV 파일로 저장한다."""
        try:
            # utf-8-sig: 엑셀에서 열어도 한글이 깨지지 않도록 BOM 포함
            with open(self._path(filename), "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDS)
                writer.writeheader()
                for r in self.records:
                    writer.writerow(r.to_dict())
            return True
        except OSError as e:
            print(f"[오류] CSV 저장 실패: {e}")
            return False

    def load_csv(self, filename="health_data.csv"):
        """CSV 파일을 읽어 목록을 교체하고, 읽은 레코드 리스트를 반환한다."""
        try:
            with open(self._path(filename), "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                self.records = [HealthRecord.from_dict(row) for row in reader]
        except (OSError, csv.Error, KeyError, ValueError, TypeError) as e:
            print(f"[오류] CSV 읽기 실패: {e}")
            self.records = []
        return self.records

    # ------------------------------------------------------------
    # TXT
    # ------------------------------------------------------------
    def save_txt(self, filename="health_data.txt", sep=","):
        """목록을 한 줄에 한 레코드씩, 구분자로 연결한 텍스트 파일로 저장한다."""
        try:
            with open(self._path(filename), "w", encoding="utf-8") as f:
                for r in self.records:
                    d = r.to_dict()
                    f.write(sep.join(str(d[key]) for key in FIELDS) + "\n")
            return True
        except OSError as e:
            print(f"[오류] TXT 저장 실패: {e}")
            return False

    def load_txt(self, filename="health_data.txt", sep=","):
        """TXT 파일을 읽어 목록을 교체하고, 읽은 레코드 리스트를 반환한다."""
        records = []
        try:
            with open(self._path(filename), "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    values = line.split(sep)
                    if len(values) != len(FIELDS):
                        raise ValueError(f"잘못된 형식의 줄: {line}")
                    records.append(HealthRecord.from_dict(dict(zip(FIELDS, values))))
            self.records = records
        except (OSError, ValueError) as e:
            print(f"[오류] TXT 읽기 실패: {e}")
            self.records = []
        return self.records

    # ------------------------------------------------------------
    # Pickle
    # ------------------------------------------------------------
    def save_pickle(self, filename="health_data.pkl"):
        """HealthRecord 객체 리스트를 그대로 Pickle 이진 파일로 저장한다."""
        try:
            with open(self._path(filename), "wb") as f:
                pickle.dump(self.records, f)
            return True
        except (OSError, pickle.PicklingError) as e:
            print(f"[오류] Pickle 저장 실패: {e}")
            return False

    def load_pickle(self, filename="health_data.pkl"):
        """Pickle 파일을 읽어 목록을 교체하고, 읽은 레코드 리스트를 반환한다.

        주의: Pickle은 이 프로그램이 직접 저장한 파일만 읽어야 한다.
        """
        try:
            with open(self._path(filename), "rb") as f:
                self.records = pickle.load(f)
        except (OSError, pickle.UnpicklingError, EOFError, AttributeError) as e:
            print(f"[오류] Pickle 읽기 실패: {e}")
            self.records = []
        return self.records

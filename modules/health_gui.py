"""
모듈 3: 사용자 인터페이스 (health_gui.py)

tkinter로 만든 GUI 화면. 실제 처리는 모두 모듈 2(HealthManager)에 맡기고,
이 파일은 "화면 그리기"와 "버튼을 눌렀을 때 모듈 2 호출 → 결과를 messagebox로 안내"만 한다.

화면 구성
    1) 위   : 파일 형식 선택, 불러오기 / 저장 / CSV 일괄 등록 버튼
    2) 왼쪽 : 입력 폼(이름, 생년, 성별, 키, 몸무게)과 등록 / 수정 / 삭제 / 초기화 버튼
    3) 오른쪽: 검색창과 건강정보 표(Treeview + 스크롤바)
    4) 아래 : 통계 (총 인원, 평균 키, 평균 몸무게, 평균 BMI, 비만도별 인원)
"""

# [AI 사용]
# - AI 종류   : Claude (Claude Code)
# - 사용 목적 : 모듈 3(HealthApp 클래스: 입력 폼, Treeview 표, 검색, 행 클릭 이벤트,
#               messagebox 안내, 통계 표시) 작성 후 설명하기 쉽게 단순화
# - 프롬프트  : "리드미를 읽고 모듈 3을 완성해줘", "설명하기 쉽게 다운그레이드 해줘 gui"
# - 사용자    : Yunjongha
# - 날짜      : 2026-11-24
#
# [AI 사용]
# - AI 종류   : Claude (Claude Code)
# - 사용 목적 : 1학년 수준 리팩토링에 맞춰 모듈 2 호출 방식(update, search) 정리
# - 프롬프트  : "현제 작성된 코드를 컴퓨터공학과 1학년 대학생 수준으로 전면 리팩토링해줘"
# - 사용자    : Yunjongha
# - 날짜      : 2026-11-25

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from modules.health_logic import HealthManager

# 표의 열 이름(레코드 속성)과 화면에 보일 제목
COLUMNS = ["id", "name", "birth_year", "gender", "height", "weight", "bmi", "status"]
HEADINGS = ["식별번호", "이름", "생년", "성별", "키(cm)", "몸무게(kg)", "BMI", "비만도"]


class HealthApp:
    """BMI 건강관리 프로그램의 메인 창."""

    def __init__(self, root):
        self.root = root
        self.root.title("BMI 건강관리 프로그램")
        self.root.geometry("950x600")

        # 모듈 2: 시작할 때 JSON 파일에서 데이터를 읽어온다
        self.manager = HealthManager()

        self.make_top_bar()
        self.make_form()
        self.make_stats()  # 표보다 먼저 배치해야 표가 공간을 다 차지하지 않는다
        self.make_table()

        self.show_records(self.manager.get_all())

    # ============================================================
    # 1. 화면 만들기
    # ============================================================
    def make_top_bar(self):
        """위: 파일 형식 선택과 파일 관련 버튼."""
        frame = tk.Frame(self.root, pady=8)
        frame.pack(fill="x")

        tk.Label(frame, text="파일 형식:").pack(side="left", padx=5)
        self.format_box = ttk.Combobox(frame, values=["json", "csv", "txt", "pickle"],
                                       width=8, state="readonly")
        self.format_box.set("json")
        self.format_box.pack(side="left")

        tk.Button(frame, text="불러오기", command=self.load_file).pack(side="left", padx=5)
        tk.Button(frame, text="저장", command=self.save_file).pack(side="left")
        tk.Button(frame, text="CSV 일괄 등록", command=self.import_csv).pack(side="left", padx=5)

    def make_form(self):
        """왼쪽: 입력 폼과 등록/수정/삭제/초기화 버튼."""
        frame = tk.LabelFrame(self.root, text="건강정보 입력", padx=10, pady=10)
        frame.pack(side="left", fill="y", padx=10)

        # 입력칸: Label과 Entry를 한 줄씩 배치
        tk.Label(frame, text="식별번호").grid(row=0, column=0, sticky="w")
        tk.Label(frame, text="이름").grid(row=1, column=0, sticky="w")
        tk.Label(frame, text="생년").grid(row=2, column=0, sticky="w")
        tk.Label(frame, text="성별").grid(row=3, column=0, sticky="w")
        tk.Label(frame, text="키(cm)").grid(row=4, column=0, sticky="w")
        tk.Label(frame, text="몸무게(kg)").grid(row=5, column=0, sticky="w")

        self.id_entry = tk.Entry(frame, width=15)  # 식별번호는 자동 생성 → 표시만 한다
        self.name_entry = tk.Entry(frame, width=15)
        self.birth_entry = tk.Entry(frame, width=15)
        self.gender_box = ttk.Combobox(frame, values=["남", "여"], width=13, state="readonly")
        self.height_entry = tk.Entry(frame, width=15)
        self.weight_entry = tk.Entry(frame, width=15)

        self.id_entry.grid(row=0, column=1, pady=3)
        self.name_entry.grid(row=1, column=1, pady=3)
        self.birth_entry.grid(row=2, column=1, pady=3)
        self.gender_box.grid(row=3, column=1, pady=3)
        self.height_entry.grid(row=4, column=1, pady=3)
        self.weight_entry.grid(row=5, column=1, pady=3)

        # 선택한 사람의 BMI와 비만도 표시
        self.bmi_label = tk.Label(frame, text="BMI: -")
        self.bmi_label.grid(row=6, column=0, columnspan=2, pady=10)

        # 버튼
        tk.Button(frame, text="등록", width=8, command=self.add_record).grid(row=7, column=0, pady=3)
        tk.Button(frame, text="수정", width=8, command=self.update_record).grid(row=7, column=1, pady=3)
        tk.Button(frame, text="삭제", width=8, command=self.delete_record).grid(row=8, column=0, pady=3)
        tk.Button(frame, text="초기화", width=8, command=self.clear_form).grid(row=8, column=1, pady=3)

    def make_table(self):
        """오른쪽: 검색창과 건강정보 표."""
        frame = tk.Frame(self.root)
        frame.pack(side="top", fill="both", expand=True, padx=(0, 10))

        # 검색창
        search_frame = tk.Frame(frame)
        search_frame.pack(fill="x", pady=5)
        tk.Label(search_frame, text="이름 또는 식별번호:").pack(side="left")
        self.search_entry = tk.Entry(search_frame, width=15)
        self.search_entry.pack(side="left", padx=5)
        tk.Button(search_frame, text="검색", command=self.search).pack(side="left")
        tk.Button(search_frame, text="전체 보기", command=self.show_all).pack(side="left", padx=5)

        # 표(Treeview)
        self.tree = ttk.Treeview(frame, columns=COLUMNS, show="headings")
        for col, heading in zip(COLUMNS, HEADINGS):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=80, anchor="center")

        # 세로 스크롤바를 표와 연결
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # 이벤트: 표의 행을 클릭하면 on_select 실행
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def make_stats(self):
        """아래: 통계를 보여줄 라벨."""
        frame = tk.LabelFrame(self.root, text="통계", padx=10, pady=10)
        frame.pack(side="bottom", fill="x", padx=(0, 10), pady=10)
        self.stats_label = tk.Label(frame, text="", justify="left")
        self.stats_label.pack(anchor="w")

    # ============================================================
    # 2. 화면 갱신
    # ============================================================
    def show_records(self, records):
        """표를 비우고 records를 다시 채운 뒤, 통계도 갱신한다."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for r in records:
            # iid를 식별번호로 지정 → 클릭한 행의 식별번호를 바로 알 수 있다
            self.tree.insert("", "end", iid=r.id, values=(
                r.id, r.name, r.birth_year, r.gender, r.height, r.weight, r.bmi, r.status))

        self.show_stats()

    def show_stats(self):
        """모듈 2의 get_statistics() 결과를 글자로 보여준다."""
        s = self.manager.get_statistics()
        counts = ", ".join(f"{status} {n}명" for status, n in s["status_counts"].items())
        self.stats_label.config(text=(
            f"총 인원: {s['count']}명    평균 키: {s['avg_height']}cm    "
            f"평균 몸무게: {s['avg_weight']}kg    평균 BMI: {s['avg_bmi']}\n"
            f"비만도별 인원: {counts}"))

    def clear_form(self):
        """입력칸을 모두 비운다."""
        for entry in (self.id_entry, self.name_entry, self.birth_entry,
                      self.height_entry, self.weight_entry):
            entry.delete(0, "end")
        self.gender_box.set("")
        self.bmi_label.config(text="BMI: -")

    # ============================================================
    # 3. 이벤트 처리 (모듈 2 호출 → messagebox로 결과 안내)
    # ============================================================
    def on_select(self, event):
        """표의 행을 클릭하면 그 사람의 정보로 입력칸을 채운다."""
        selected = self.tree.selection()
        if not selected:
            return
        record = self.manager.find_by_id(selected[0])

        self.clear_form()
        self.id_entry.insert(0, record.id)
        self.name_entry.insert(0, record.name)
        self.birth_entry.insert(0, record.birth_year)
        self.gender_box.set(record.gender)
        self.height_entry.insert(0, record.height)
        self.weight_entry.insert(0, record.weight)
        self.bmi_label.config(text=f"BMI: {record.bmi} ({record.status})")

    def add_record(self):
        """등록 버튼: 입력값으로 새 레코드를 등록한다."""
        try:
            record = self.manager.add(self.name_entry.get(), self.birth_entry.get(),
                                      self.gender_box.get(), self.height_entry.get(),
                                      self.weight_entry.get())
        except ValueError as e:  # 잘못된 입력이나 중복이면 모듈 2가 ValueError를 보낸다
            messagebox.showwarning("등록 실패", str(e))
            return
        messagebox.showinfo("등록 완료", f"등록되었습니다.\n식별번호: {record.id}")
        self.clear_form()
        self.show_all()

    def update_record(self):
        """수정 버튼: 선택한 사람의 정보를 입력값으로 바꾼다. (BMI는 모듈 2가 다시 계산)"""
        record_id = self.id_entry.get()
        if record_id == "":
            messagebox.showwarning("수정 실패", "수정할 사람을 표에서 먼저 선택하세요.")
            return
        try:
            record = self.manager.update(record_id,
                                         self.name_entry.get(),
                                         self.birth_entry.get(),
                                         self.gender_box.get(),
                                         self.height_entry.get(),
                                         self.weight_entry.get())
        except ValueError as e:
            messagebox.showwarning("수정 실패", str(e))
            return
        messagebox.showinfo("수정 완료", f"수정되었습니다.\nBMI: {record.bmi} ({record.status})")
        self.clear_form()
        self.show_all()

    def delete_record(self):
        """삭제 버튼: 선택한 사람을 확인 후 삭제한다."""
        record_id = self.id_entry.get()
        if record_id == "":
            messagebox.showwarning("삭제 실패", "삭제할 사람을 표에서 먼저 선택하세요.")
            return
        if not messagebox.askyesno("삭제 확인", f"{record_id} 를 삭제할까요?"):
            return
        try:
            self.manager.delete(record_id)
        except ValueError as e:
            messagebox.showwarning("삭제 실패", str(e))
            return
        messagebox.showinfo("삭제 완료", "삭제되었습니다.")
        self.clear_form()
        self.show_all()

    def search(self):
        """검색 버튼: 이름 또는 식별번호에 검색어가 들어간 사람을 보여준다."""
        keyword = self.search_entry.get()
        results = self.manager.search(keyword)   # 모듈 2가 이름·식별번호 둘 다 검사한다
        self.show_records(results)

    def show_all(self):
        """전체 보기 버튼: 검색어를 지우고 전체 목록을 보여준다."""
        self.search_entry.delete(0, "end")
        self.show_records(self.manager.get_all())

    def load_file(self):
        """불러오기 버튼: 선택한 형식의 파일에서 데이터를 읽어온다."""
        self.manager.set_format(self.format_box.get())
        records = self.manager.load()
        self.clear_form()
        self.show_all()
        messagebox.showinfo("불러오기", f"{len(records)}명의 데이터를 불러왔습니다.")

    def save_file(self):
        """저장 버튼: 선택한 형식의 파일로 저장한다."""
        self.manager.set_format(self.format_box.get())
        if self.manager.save():
            messagebox.showinfo("저장 완료", f"{self.format_box.get()} 파일로 저장했습니다.")
        else:
            messagebox.showerror("저장 실패", "파일 저장에 실패했습니다.")

    def import_csv(self):
        """CSV 일괄 등록 버튼: CSV 파일을 골라 여러 명을 한 번에 등록한다."""
        path = filedialog.askopenfilename(filetypes=[("CSV 파일", "*.csv")])
        if path == "":  # 파일 선택을 취소한 경우
            return
        try:
            added, failed = self.manager.import_csv(path)
        except ValueError as e:
            messagebox.showerror("일괄 등록 실패", str(e))
            return
        messagebox.showinfo("일괄 등록 완료", f"{len(added)}명 등록, {len(failed)}건 실패")
        self.show_all()


def run_gui():
    """GUI 창을 띄운다. (main.py에서 호출)"""
    root = tk.Tk()
    HealthApp(root)
    root.mainloop()


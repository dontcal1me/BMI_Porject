# 모듈 3 `health_gui.py` 코드 설명

> 대상: 프로그래밍 Ⅱ를 듣는 컴퓨터공학과 1학년
> 목표: 이 문서만 읽고 GUI 코드를 처음부터 끝까지 말로 설명할 수 있게 하기

---

## 0. 한 문장 요약

**"화면(버튼, 입력칸, 표)을 만들고, 버튼이 눌리면 모듈 2(`HealthManager`)에게 일을 시킨 뒤, 그 결과를 표와 알림창으로 보여주는 코드"** 입니다.

GUI 파일은 **계산도, 파일 저장도 직접 하지 않습니다.**
BMI 계산은 모듈 1이, 등록·수정·삭제·검색 규칙은 모듈 2가 합니다.
GUI는 "화면 담당"일 뿐입니다. 이것을 **역할 분리(SoC)** 라고 합니다.

```
 사용자 ──클릭──▶ [모듈 3: GUI] ──호출──▶ [모듈 2: HealthManager] ──호출──▶ [모듈 1: HealthDB / HealthRecord]
                     ▲                         │                                    │
                     └──── 결과(레코드/오류) ──┘                         파일(json/csv/txt/pkl)
```

---

## 1. 꼭 알아야 할 tkinter 기초 5가지

### ① 창 만들기와 `mainloop()`

```python
root = tk.Tk()        # 빈 창 하나를 만든다
HealthApp(root)       # 그 창 안에 우리 화면을 채운다
root.mainloop()       # 창을 띄우고, 사용자가 무언가 할 때까지 계속 기다린다
```

`mainloop()`는 **무한 반복문**이라고 생각하면 됩니다.
"클릭이 있었나? 키보드 입력이 있었나?"를 계속 확인하다가, 일이 생기면 연결된 함수를 실행합니다. 창을 닫으면 반복이 끝납니다.

### ② 위젯(Widget) = 화면 부품

| 위젯 | 역할 | 이 코드에서 |
|------|------|-------------|
| `tk.Label` | 글자 표시 | "이름", "BMI: -", 통계 글자 |
| `tk.Entry` | 한 줄 입력칸 | 이름, 생년, 키, 몸무게 입력 |
| `ttk.Combobox` | 목록에서 고르기 | 성별(남/여), 파일 형식 |
| `tk.Button` | 버튼 | 등록, 수정, 삭제 … |
| `tk.Frame` / `tk.LabelFrame` | 부품을 담는 상자 | 왼쪽 폼, 아래 통계 영역 |
| `ttk.Treeview` | 엑셀 같은 표 | 건강정보 목록 |
| `ttk.Scrollbar` | 스크롤바 | 표 오른쪽 |

위젯을 만들 때 첫 번째 인자는 **"어느 상자 안에 넣을지"** 입니다.

```python
tk.Label(frame, text="이름")   # frame 상자 안에 "이름" 글자를 만든다
```

### ③ 배치: `pack` 과 `grid`

위젯은 만들기만 하면 화면에 안 보입니다. **배치**를 해야 보입니다.

- `pack(side="left")` : 남은 공간의 왼쪽/위/아래에 **차례로 쌓기**. 간단한 배치에 씁니다.
- `grid(row=1, column=0)` : **바둑판(행, 열)** 위치에 놓기. 입력 폼처럼 줄을 맞춰야 할 때 씁니다.

> 한 상자(Frame) 안에서는 `pack`과 `grid`를 섞어 쓰면 안 됩니다.
> 그래서 입력 폼 상자 안은 전부 `grid`, 나머지는 `pack`을 씁니다.

### ④ 버튼과 함수 연결: `command=`

```python
tk.Button(frame, text="등록", command=self.add_record)
```

"등록 버튼이 눌리면 `self.add_record` 함수를 실행해라" 라는 뜻입니다.
**괄호 `()`를 붙이지 않는 것**이 중요합니다.
`self.add_record()`라고 쓰면 버튼을 만드는 순간 함수가 바로 실행되어 버립니다. 괄호 없이 **함수 자체를 넘겨야** 나중에 클릭할 때 실행됩니다.

### ⑤ 이벤트 연결: `bind`

```python
self.tree.bind("<<TreeviewSelect>>", self.on_select)
```

버튼이 아닌 위젯에서 일어나는 일(이벤트)에 함수를 연결할 때 `bind`를 씁니다.
`<<TreeviewSelect>>`는 "표에서 행이 선택되었다"는 이벤트입니다.
`bind`로 연결된 함수는 이벤트 정보를 담은 `event`를 인자로 받기 때문에 `def on_select(self, event):` 처럼 `event` 매개변수가 있습니다.

---

## 2. 전체 구조

```
health_gui.py
├── COLUMNS, HEADINGS        ← 표의 열 이름 목록 (상수)
├── class HealthApp          ← 화면 전체를 담당하는 클래스
│   ├── __init__             ← 시작: 모듈 2 준비 + 화면 만들기 + 표 채우기
│   │
│   ├── [1. 화면 만들기]
│   │   ├── make_top_bar     ← 위: 파일 형식, 불러오기/저장/CSV 버튼
│   │   ├── make_form        ← 왼쪽: 입력칸과 등록/수정/삭제/초기화 버튼
│   │   ├── make_stats       ← 아래: 통계 글자
│   │   └── make_table       ← 오른쪽: 검색창과 표
│   │
│   ├── [2. 화면 갱신]
│   │   ├── show_records     ← 표를 지우고 다시 채움 (+ 통계 갱신)
│   │   ├── show_stats       ← 통계 글자 갱신
│   │   └── clear_form       ← 입력칸 비우기
│   │
│   └── [3. 이벤트 처리]  ← 사용자가 무언가 하면 실행되는 함수들
│       ├── on_select        ← 표의 행 클릭
│       ├── add_record       ← 등록 버튼
│       ├── update_record    ← 수정 버튼
│       ├── delete_record    ← 삭제 버튼
│       ├── search / show_all← 검색 / 전체 보기 버튼
│       └── load_file / save_file / import_csv ← 파일 버튼
│
└── run_gui()                ← 창을 띄우는 함수 (main.py가 호출)
```

**설명할 때는 "1. 화면 만들기 → 2. 화면 갱신 → 3. 이벤트 처리" 순서로 말하면 됩니다.**

### 화면 모습

```
┌──────────────────────────────────────────────────────────────┐
│ 파일 형식:[json▼] [불러오기] [저장] [CSV 일괄 등록]   ← make_top_bar
├───────────────┬──────────────────────────────────────────────┤
│ 건강정보 입력 │ 이름 또는 식별번호:[    ] [검색] [전체 보기] │
│ 식별번호 [  ] │ ┌──────────────────────────────────────┐▲│
│ 이름     [  ] │ │식별번호│이름│생년│성별│키│몸무게│BMI│..│ ││ ← make_table
│ 생년     [  ] │ │P2026-..│홍길동│...                   │ ││
│ 성별     [▼]  │ └──────────────────────────────────────┘▼│
│ 키       [  ] ├──────────────────────────────────────────────┤
│ 몸무게   [  ] │ 통계                                          │ ← make_stats
│  BMI: -       │ 총 인원: 9명  평균 키: ...                    │
│ [등록][수정]  │ 비만도별 인원: 저체중 1명, 정상 2명 ...       │
│ [삭제][초기화]│                                               │
└───────────────┴──────────────────────────────────────────────┘
   ↑ make_form
```

---

## 3. 코드 따라 읽기

### 3-1. 맨 위: import와 상수

```python
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from modules.health_logic import HealthManager
```

- `tkinter` : 파이썬에 기본으로 들어 있는 GUI 라이브러리 (따로 설치 필요 없음)
- `ttk` : 조금 더 예쁜 위젯(Combobox, Treeview 등) 모음
- `messagebox` : 알림창, `filedialog` : 파일 선택 창
- `HealthManager` : 모듈 2. 실제 일을 해주는 클래스

```python
COLUMNS  = ["id", "name", "birth_year", ...]          # 프로그램 내부에서 쓰는 열 이름
HEADINGS = ["식별번호", "이름", "생년", ...]           # 화면에 보이는 열 제목
```

두 리스트는 **순서가 서로 맞춰져 있습니다.** 나중에 `zip`으로 짝지어서 표 제목을 붙입니다.

### 3-2. `__init__` : 프로그램 시작

```python
def __init__(self, root):
    self.root = root
    self.root.title("BMI 건강관리 프로그램")   # 창 제목
    self.root.geometry("950x600")              # 창 크기 (가로x세로)

    self.manager = HealthManager()   # 모듈 2 객체 생성 → 이때 json 파일을 읽어옴

    self.make_top_bar()
    self.make_form()
    self.make_stats()   # 표보다 먼저!
    self.make_table()

    self.show_records(self.manager.get_all())   # 처음 화면에 전체 목록 표시
```

- `self.xxx = ...` 로 저장한 것은 **클래스의 다른 함수에서도 쓸 수 있습니다.**
  예: `self.manager`는 모든 버튼 함수에서 사용합니다.
  반대로 `self.` 없이 만든 변수(예: `frame`)는 그 함수 안에서만 씁니다.
  나중에 값을 읽어야 하는 입력칸(`self.name_entry`)에는 `self.`를 붙이고, 한 번 만들고 끝나는 Label에는 붙이지 않았습니다.

- **왜 `make_stats()`가 `make_table()`보다 먼저인가?**
  표는 `expand=True`로 "남은 공간을 다 차지해라"라고 설정되어 있습니다.
  `pack`은 **먼저 배치한 것부터 공간을 가져가므로**, 표를 먼저 놓으면 통계가 들어갈 자리가 없어집니다.

### 3-3. `make_form` : 입력 폼

```python
tk.Label(frame, text="이름").grid(row=1, column=0, sticky="w")   # 1행 0열에 글자
self.name_entry = tk.Entry(frame, width=15)                       # 입력칸 생성
self.name_entry.grid(row=1, column=1, pady=3)                     # 1행 1열에 배치
```

- 0열에는 제목(Label), 1열에는 입력칸(Entry)을 놓아 줄을 맞춥니다.
- `sticky="w"` : 칸 안에서 왼쪽(west)에 붙이기
- `pady=3` : 위아래 여백 3픽셀
- 성별은 아무 글자나 입력하지 못하게 `Combobox(state="readonly")`로 **남/여 중에서만 고르게** 했습니다.

### 3-4. `make_table` : 표(Treeview)와 스크롤바

```python
self.tree = ttk.Treeview(frame, columns=COLUMNS, show="headings")
for col, heading in zip(COLUMNS, HEADINGS):
    self.tree.heading(col, text=heading)              # 열 제목 붙이기
    self.tree.column(col, width=80, anchor="center")  # 열 너비, 가운데 정렬
```

- `show="headings"` : Treeview는 원래 폴더 트리 모양인데, 맨 왼쪽 트리 칸을 숨기고 **표처럼만** 보이게 합니다.
- `zip(COLUMNS, HEADINGS)` : `("id","식별번호")`, `("name","이름")` … 처럼 두 리스트를 짝지어 줍니다.

```python
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
self.tree.configure(yscrollcommand=scrollbar.set)
```

스크롤바와 표는 **양방향으로 연결**해야 합니다.
- `command=self.tree.yview` : 스크롤바를 움직이면 → 표가 움직임
- `yscrollcommand=scrollbar.set` : 표가 움직이면(마우스 휠 등) → 스크롤바 위치가 바뀜

### 3-5. `show_records` : 표 다시 그리기

```python
def show_records(self, records):
    for item in self.tree.get_children():   # 표에 있는 모든 행을
        self.tree.delete(item)               # 하나씩 지운다

    for r in records:                        # 받은 레코드를 한 줄씩
        self.tree.insert("", "end", iid=r.id, values=(r.id, r.name, ...))

    self.show_stats()                        # 통계도 같이 갱신
```

- 표를 "고치는" 대신 **다 지우고 새로 채우는** 방식입니다. 코드가 단순해지고 실수가 적습니다.
- `insert("", "end", ...)` : 맨 끝에 행 추가 (`""`는 "부모 없음", 즉 최상위 행)
- **`iid=r.id`가 핵심입니다.** 각 행의 이름표(iid)를 식별번호로 정해 두었기 때문에, 나중에 행을 클릭하면 바로 "P2026-0001"을 얻을 수 있습니다.

### 3-6. `show_stats` : 통계

```python
s = self.manager.get_statistics()   # 모듈 2가 계산한 통계 딕셔너리
counts = ", ".join(f"{status} {n}명" for status, n in s["status_counts"].items())
self.stats_label.config(text=f"총 인원: {s['count']}명 ...")
```

- 평균 계산은 모듈 2가 하고, GUI는 **받아서 글자로 보여주기만** 합니다.
- `", ".join(...)` : `["저체중 1명", "정상 2명"]`을 `"저체중 1명, 정상 2명"`으로 이어 붙입니다.
- `label.config(text=...)` : 이미 만든 Label의 글자를 바꿉니다.

### 3-7. `on_select` : 행을 클릭하면 입력칸 채우기

```python
def on_select(self, event):
    selected = self.tree.selection()          # 선택된 행의 iid 목록 → ("P2026-0001",)
    if not selected:                          # 선택이 없으면 아무것도 안 함
        return
    record = self.manager.find_by_id(selected[0])   # 모듈 2에게 식별번호로 레코드 찾기 요청

    self.clear_form()                         # 먼저 비우고
    self.name_entry.insert(0, record.name)    # 0번째 위치(맨 앞)에 이름 넣기
    ...
```

- `insert` 전에 `clear_form()`을 하는 이유: Entry의 `insert`는 **기존 글자 뒤에 덧붙이기 때문**입니다. 안 지우면 "홍길동김영희"처럼 됩니다.
- 이 기능 덕분에 사용자는 표에서 클릭만 하면 바로 수정·삭제를 할 수 있습니다. (README 비기능 요구사항)

### 3-8. `add_record` : 등록 버튼 ⭐ (가장 중요한 패턴)

```python
def add_record(self):
    try:
        record = self.manager.add(self.name_entry.get(), self.birth_entry.get(),
                                  self.gender_box.get(), self.height_entry.get(),
                                  self.weight_entry.get())
    except ValueError as e:
        messagebox.showwarning("등록 실패", str(e))
        return
    messagebox.showinfo("등록 완료", f"등록되었습니다.\n식별번호: {record.id}")
    self.clear_form()
    self.show_all()
```

모든 버튼 함수가 **똑같은 4단계 패턴**입니다.

1. **입력 읽기** : `entry.get()` 으로 입력칸의 글자를 가져옴 (항상 문자열 `str`)
2. **모듈 2 호출** : `self.manager.add(...)` 에게 등록을 부탁함
3. **실패하면** : 모듈 2가 `ValueError`를 던짐 → `except`에서 잡아 경고창 → `return`으로 함수 종료
4. **성공하면** : 안내창 → 입력칸 비우기 → 표 새로고침

> **입력값 검사는 어디서 하나요?**
> GUI가 아니라 **모듈 2의 `check_input()`** 에서 합니다.
> 키에 "abc"나 0을 넣으면 모듈 2가 `ValueError("키와 몸무게는 숫자로 입력하세요.")`를 발생시키고,
> GUI는 그 메시지를 `str(e)`로 꺼내 그대로 알림창에 보여줍니다.
> 그래서 잘못 입력해도 **프로그램이 꺼지지 않습니다.** (README 비기능 요구사항 1번)

### 3-9. `update_record` / `delete_record` : 수정, 삭제

```python
record_id = self.id_entry.get()
if record_id == "":
    messagebox.showwarning("수정 실패", "수정할 사람을 표에서 먼저 선택하세요.")
    return
```

- 식별번호 칸이 비어 있다 = 표에서 아무도 선택하지 않았다 → 경고 후 종료
- 수정은 `self.manager.update(record_id, 이름, 생년, 성별, 키, 몸무게)` 순서대로 입력칸 값을 넘깁니다.
  키·몸무게가 바뀌면 BMI 재계산은 모듈 2가 해줍니다.
- 삭제는 실수로 지우지 않도록 `messagebox.askyesno`로 한 번 더 묻습니다.
  "예"를 누르면 `True`, "아니오"면 `False`를 돌려줍니다.

### 3-10. `search` : 검색

```python
keyword = self.search_entry.get()
results = self.manager.search(keyword)   # 모듈 2가 이름·식별번호 둘 다 검사한다
self.show_records(results)
```

- 검색창 하나로 이름과 식별번호를 **둘 다** 찾습니다.
- 모듈 2의 `search()`가 레코드를 하나씩 보면서 "이름에 검색어가 있거나, 식별번호에 검색어가 있으면" 결과 리스트에 넣어 줍니다.

### 3-11. 파일 버튼

| 함수 | 하는 일 |
|------|---------|
| `load_file` | 콤보박스에서 고른 형식으로 `set_format` → `manager.load()` → 표 새로고침 |
| `save_file` | 고른 형식으로 `manager.save()` → 성공(`True`)/실패(`False`)에 따라 알림 |
| `import_csv` | `filedialog.askopenfilename`으로 파일 고르기 → `manager.import_csv(path)` → "n명 등록, m건 실패" 알림 |

파일 선택 창에서 "취소"를 누르면 빈 문자열 `""`이 돌아오므로 `if path == "": return` 으로 처리합니다.

> 참고: 등록·수정·삭제할 때마다 모듈 2가 **자동으로 파일에 저장**합니다.
> "저장" 버튼은 다른 형식(csv 등)으로 따로 저장하고 싶을 때 씁니다.

### 3-12. `run_gui` 와 `main.py`

```python
def run_gui():
    root = tk.Tk()
    HealthApp(root)
    root.mainloop()
```

`main.py`에서 `python main.py`로 실행하면 이 함수가 호출됩니다.

---

## 4. 실제 흐름 따라가기: "등록" 버튼을 누르면?

입력: 이름 `박지성`, 생년 `1990`, 성별 `남`, 키 `178`, 몸무게 `73`

```
① 사용자가 [등록] 클릭
② mainloop가 감지 → command로 연결된 add_record() 실행           (모듈 3)
③ entry.get()으로 "박지성", "1990", "남", "178", "73" 읽기         (모듈 3)
④ self.manager.add(...) 호출                                       (모듈 3 → 모듈 2)
⑤ check_input(): 문자열 "178" → 숫자 178.0 변환, 범위 검사            (모듈 2)
⑥ is_duplicate(): 같은 이름·생년·성별이 있는지 검사                (모듈 2)
⑦ db.add_record() → HealthRecord 생성                              (모듈 2 → 모듈 1)
⑧ 식별번호 자동 생성 "P2026-0010", BMI = 73 / 1.78² = 23.04, "과체중" (모듈 1)
⑨ save() → health_data.json 파일에 저장                            (모듈 2 → 모듈 1)
⑩ 레코드를 GUI로 돌려줌 → "등록 완료" 알림창                        (모듈 3)
⑪ show_all() → 표 다시 그리기 + 통계 갱신                           (모듈 3)
```

몸무게에 `0`을 넣었다면 ⑤에서 `ValueError`가 발생해 ⑥ 이후는 실행되지 않고,
바로 `except`로 가서 "몸무게는 0보다 크고 500kg 이하인 숫자로 입력하세요." 경고창이 뜹니다.

---

## 5. 예상 질문과 답변

**Q1. `command=self.add_record`에 왜 괄호가 없나요?**
괄호를 붙이면 버튼을 만드는 순간 함수가 실행되고, 그 **반환값**(None)이 command에 들어갑니다. 클릭할 때 실행되게 하려면 함수 자체를 넘겨야 합니다.

**Q2. `self`는 무엇인가요?**
지금 만들어진 `HealthApp` 객체 자신입니다. `self.name_entry`처럼 저장해 두면 다른 메서드(`add_record` 등)에서도 같은 입력칸을 쓸 수 있습니다.

**Q3. 키에 문자를 넣으면 왜 프로그램이 안 꺼지나요?**
모듈 2가 `float("abc")` 변환에 실패하면 `ValueError`를 발생시키고, GUI의 `try-except`가 그 오류를 잡아 경고창으로 보여주기 때문입니다.

**Q4. 행을 클릭했을 때 어떤 사람인지 어떻게 아나요?**
표에 행을 넣을 때 `iid=r.id`로 각 행의 이름을 식별번호로 정했습니다. `self.tree.selection()`이 그 식별번호를 돌려주고, `manager.find_by_id()`로 레코드를 찾습니다.

**Q5. BMI 계산은 GUI에서 하나요?**
아닙니다. 모듈 1의 `HealthRecord.calculate_bmi()`가 합니다. GUI는 결과를 보여주기만 합니다. 이렇게 역할을 나누면 GUI를 콘솔로 바꿔도 계산 코드는 그대로 쓸 수 있습니다. (실제로 콘솔 APP과 GUI가 같은 모듈 2를 사용합니다.)

**Q6. `pack`과 `grid`의 차이는?**
`pack`은 위·아래·왼쪽·오른쪽으로 차례로 쌓고, `grid`는 행·열 위치를 지정합니다. 입력 폼은 줄을 맞춰야 해서 `grid`, 나머지는 간단히 `pack`을 썼습니다. 한 Frame 안에서 둘을 섞으면 안 됩니다.

**Q7. 표를 갱신할 때 왜 전부 지우고 다시 넣나요?**
어떤 행이 바뀌었는지 일일이 찾는 것보다, 다 지우고 최신 목록으로 다시 채우는 것이 코드가 짧고 실수가 없습니다. 데이터가 수천 개 정도까지는 속도 차이도 거의 없습니다.

**Q8. 수정할 때 입력칸을 비우면 어떻게 되나요?**
모듈 2의 `update()`가 빈 값은 "기존 값 유지"로 처리하도록 만들어져 있어서, 그 항목은 바뀌지 않습니다.

---

## 6. 즉석 수정 요구에 대비한 연습

| 요구 | 고칠 곳 |
|------|---------|
| 창 크기를 바꿔라 | `__init__`의 `geometry("950x600")` |
| 버튼 글자를 바꿔라 | `make_form`의 `tk.Button(..., text="등록")` |
| 표 열 너비를 바꿔라 | `make_table`의 `self.tree.column(col, width=80)` |
| 시작 파일 형식을 csv로 | `make_top_bar`의 `self.format_box.set("json")` 와 `HealthManager(file_format="csv")` |
| 통계에 최대 BMI도 보여줘라 | `show_stats`의 글자에 `{s['max_bmi']}` 추가 (모듈 2가 이미 계산해 줌) |
| 삭제 확인창 문구를 바꿔라 | `delete_record`의 `askyesno(...)` 안의 글자 |

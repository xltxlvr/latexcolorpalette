import re
import sys, os
import subprocess, platform
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QTabWidget, QGridLayout, QLineEdit, QFrame, QHBoxLayout,
    QMessageBox, QComboBox, QCheckBox, QSpinBox, QInputDialog,
    QMenu
)
from PySide6.QtGui import (
    QColor, QPalette, QGuiApplication, QShortcut, 
    QKeySequence, QAction, QIcon
)
from PySide6.QtCore import Qt, QTimer
import colorsys
import random

def get_usercolordef_path():
    # 1. 현재 폴더에서 먼저 찾기
    local_path = os.path.join(os.path.abspath("."), "usercolordef.tex")
    if os.path.exists(local_path):
        return local_path

    env = os.environ.copy()
    if platform.system() == "Darwin":
        env["PATH"] = env.get("PATH", "") + ":/Library/TeX/texbin:/usr/local/bin:/opt/homebrew/bin"
    elif platform.system() == "Linux":
        env["PATH"] = env.get("PATH", "") + ":/usr/local/bin:/usr/local/texlive/2026/bin/x86_64-linux"

    # 운영체제가 윈도우일 경우에만 창 숨김 옵션을 적용하기 위한 설정
    kwargs = {}
    if sys.platform == "win32":
        kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

    # 2. 현재 폴더에 없으면 kpsewhich를 통해 찾기
    try:
        # kpsewhich 명령어 실행
        result = subprocess.run(
            ['kpsewhich', 'usercolordef.tex'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=5,
            **kwargs,
            env=env
        )
        
        # 결과값에서 공백 및 줄바꿈 제거 후 반환
        kpsewhich_path = result.stdout.strip()
        if kpsewhich_path:
            return kpsewhich_path
            
    except subprocess.CalledProcessError:
        # kpsewhich 명령어가 실행되었으나 파일을 찾지 못한 경우 (exit code 1)
        pass
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # 시스템 환경변수에 kpsewhich 명령어 자체가 없는 경우 (TeX 미설치 등)
        pass

    # 1, 2번 방법 모두 실패한 경우
    return None

# --- 1. 전역 색상 변환 함수 ---
def to255(v):
    """0~1 실수를 0~255 정수로 반올림 (int() 절삭 시 1씩 낮게 표시되는 문제 방지)"""
    return max(0, min(255, int(v * 255 + 0.5)))

def rgb_to_cmyk_calc(r, g, b):
    k = 1.0 - max(r, g, b)
    if k == 1.0: return (0.0, 0.0, 0.0, 1.0)
    c = (1.0 - r - k) / (1.0 - k)
    m = (1.0 - g - k) / (1.0 - k)
    y = (1.0 - b - k) / (1.0 - k)
    return (round(c, 3), round(m, 3), round(y, 3), round(k, 3))

def cmyk_to_rgb_calc(c, m, y, k):
    r = (1.0 - c) * (1.0 - k)
    g = (1.0 - m) * (1.0 - k)
    b = (1.0 - y) * (1.0 - k)
    return (round(r, 3), round(g, 3), round(b, 3))

# --- 2. 하드코딩 색상 사전 ---
BASE_COLORS = {
    "red": {'rgb': (1.0, 0.0, 0.0), 'cmyk': (0.0, 1.0, 1.0, 0.0), 'exact': 'both'},
    "green": {'rgb': (0.0, 1.0, 0.0), 'cmyk': (1.0, 0.0, 1.0, 0.0), 'exact': 'both'},
    "blue": {'rgb': (0.0, 0.0, 1.0), 'cmyk': (1.0, 1.0, 0.0, 0.0), 'exact': 'both'},
    "brown": {'rgb': (0.75, 0.5, 0.25), 'cmyk': (0.0, 0.25, 0.5, 0.25), 'exact': 'both'},
    "lime": {'rgb': (0.75, 1.0, 0.0), 'cmyk': (0.25, 0.0, 1.0, 0.0), 'exact': 'both'},
    "orange": {'rgb': (1.0, 0.5, 0.0), 'cmyk': (0.0, 0.5, 1.0, 0.0), 'exact': 'both'},
    "pink": {'rgb': (1.0, 0.75, 0.75), 'cmyk': (0.0, 0.25, 0.25, 0.0), 'exact': 'both'},
    "purple": {'rgb': (0.75, 0.0, 0.25), 'cmyk': (0.0, 0.75, 0.5, 0.25), 'exact': 'both'},
    "teal": {'rgb': (0.0, 0.5, 0.5), 'cmyk': (0.5, 0.0, 0.0, 0.5), 'exact': 'both'},
    "violet": {'rgb': (0.5, 0.0, 0.5), 'cmyk': (0.0, 0.5, 0.0, 0.5), 'exact': 'both'},
    "cyan": {'rgb': (0.0, 1.0, 1.0), 'cmyk': (1.0, 0.0, 0.0, 0.0), 'exact': 'both'},
    "magenta": {'rgb': (1.0, 0.0, 1.0), 'cmyk': (0.0, 1.0, 0.0, 0.0), 'exact': 'both'},
    "yellow": {'rgb': (1.0, 1.0, 0.0), 'cmyk': (0.0, 0.0, 1.0, 0.0), 'exact': 'both'},
    "olive": {'rgb': (0.5, 0.5, 0.0), 'cmyk': (0.0, 0.0, 1.0, 0.5), 'exact': 'both'},
    "black": {'rgb': (0.0, 0.0, 0.0), 'cmyk': (0.0, 0.0, 0.0, 1.0), 'exact': 'both'},
    "darkgray": {'rgb': (0.25, 0.25, 0.25), 'cmyk': (0.0, 0.0, 0.0, 0.75), 'exact': 'both'},
    "gray": {'rgb': (0.5, 0.5, 0.5), 'cmyk': (0.0, 0.0, 0.0, 0.5), 'exact': 'both'},
    "lightgray": {'rgb': (0.75, 0.75, 0.75), 'cmyk': (0.0, 0.0, 0.0, 0.25), 'exact': 'both'},
    "white": {'rgb': (1.0, 1.0, 1.0), 'cmyk': (0.0, 0.0, 0.0, 0.0), 'exact': 'both'}
}

# dvipsnames는 하드코딩하지 않고 dvipsnam.def(원본 이름·대소문자 유지)에서 읽습니다.

# --- 3. 커스텀 버튼 위젯 ---
class ColorButton(QPushButton):
    def __init__(self, display_name, actual_name, hexcode, color_data, parent_widget, full_pal_name=""):
        super().__init__(display_name)
        self.display_name = display_name
        self.actual_name = actual_name
        self.hexcode = hexcode
        self.color_data = color_data
        self.parent_widget = parent_widget

        # 1. 색상의 밝기(Luminance) 계산
        color = QColor(hexcode)
        r, g, b, _ = color.getRgb()
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
        
        # 2. 텍스트 색상 결정
        text_color = "white" if luminance < 0.5 else "black"

        # 3. QPalette 대신 Style Sheet 적용 (macOS 네이티브 스타일 무시하고 강제 적용)
        # macOS에서는 border를 같이 지정해주어야 배경색이 완벽하게 먹힙니다.
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {hexcode};
                color: {text_color};
                border: 1px solid #a0a0a0;
                border-radius: 4px;
                padding: 4px;
            }}
        """)

        # 툴팁 설정
        if full_pal_name:
            self.setToolTip(f"{actual_name} \n(출처: {full_pal_name})")
        else:
            self.setToolTip(actual_name)

        self.clicked.connect(lambda: self.parent_widget.show_color(
            self.actual_name, self.hexcode, self.color_data, self.display_name.replace('\n', ' ')
        ))

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.parent_widget.show_color(
            self.actual_name, self.hexcode, self.color_data, self.display_name.replace('\n', ' ')
        )

# --- 4. 유틸리티 및 파서 함수 ---
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def parse_tex_colors(path):
    colors = {}
    pattern = re.compile(r"\\definecolor\s*\{([^}]+)\}\s*\{(rgb|RGB|HTML|cmyk)\}\s*\{([^}]+)\}")
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                m = pattern.search(line)
                if m:
                    name = m.group(1).strip().replace("’", "'")
                    model = m.group(2)
                    val = m.group(3).strip()
                    try:
                        if model == "rgb":
                            r, g, b = (float(x.strip()) for x in val.split(","))
                            colors[name] = {'rgb': (r,g,b), 'cmyk': rgb_to_cmyk_calc(r,g,b), 'exact': 'rgb'}
                        elif model == "RGB":
                            r, g, b = (float(x.strip())/255.0 for x in val.split(","))
                            colors[name] = {'rgb': (r,g,b), 'cmyk': rgb_to_cmyk_calc(r,g,b), 'exact': 'RGB'}
                        elif model == "HTML":
                            val = val.lstrip("#").strip()
                            r, g, b = int(val[0:2], 16)/255.0, int(val[2:4], 16)/255.0, int(val[4:6], 16)/255.0
                            colors[name] = {'rgb': (r,g,b), 'cmyk': rgb_to_cmyk_calc(r,g,b), 'exact': 'HTML'}
                        elif model == "cmyk":
                            c, m_val, y, k = (float(x.strip()) for x in val.split(","))
                            colors[name] = {'rgb': cmyk_to_rgb_calc(c,m_val,y,k), 'cmyk': (c,m_val,y,k), 'exact': 'cmyk'}
                    except Exception:
                        continue
    except FileNotFoundError:
        pass
    return colors

def parse_def_file(path):
    colors = {}
    # 기존: 마지막이 반드시 ; 이어야 함
    # pattern = re.compile(r"([A-Za-z0-9]+)\s*,\s*([0-9\.]+)\s*,\s*([0-9\.]+)\s*,\s*([0-9\.]+)\s*;")
    # 💡 수정: 마지막이 ; 또는 } 중 하나로 끝나도록 처리
    pattern = re.compile(r"([A-Za-z0-9]+)\s*,\s*([0-9\.]+)\s*,\s*([0-9\.]+)\s*,\s*([0-9\.]+)\s*[;}]")

    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
            for m in pattern.finditer(content):
                name = m.group(1)
                r, g, b = float(m.group(2)), float(m.group(3)), float(m.group(4))
                colors[name] = {'rgb': (r,g,b), 'cmyk': rgb_to_cmyk_calc(r,g,b), 'exact': 'rgb'}
    except FileNotFoundError:
        pass
    return colors

def load_xkcd_palette(path):
    colors = {}
    # xkcdcolors.sty 형식: 앞뒤 공백 무시, "이름,Hex코드;" 형태 추출
    # 예: "    CloudyBlue,ACC2D9;%" -> group(1)="CloudyBlue", group(2)="ACC2D9"
    # pattern = re.compile(r"^\s*([A-Za-z]+),([A-Fa-f0-9]{6});")
    # 💡 수정: 마지막이 ; 또는 } 이면 매칭됨
    pattern = re.compile(r"^\s*([A-Za-z']+),([A-Fa-f0-9]{6})[;}]")

    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                m = pattern.search(line)
                if m:
                    # 추출한 이름 앞에 'xkcd'를 붙여서 최종 키값으로 사용
                    name = "xkcd" + m.group(1).strip()
                    val = m.group(2).strip()
                    
                    try:
                        r = int(val[0:2], 16) / 255.0
                        g = int(val[2:4], 16) / 255.0
                        b = int(val[4:6], 16) / 255.0
                        
                        colors[name] = {
                            'rgb': (r, g, b),
                            'cmyk': rgb_to_cmyk_calc(r, g, b),
                            'exact': 'HTML'
                        }
                    except Exception:
                        continue
    except FileNotFoundError:
        pass
        
    return colors

def parse_dvips_def(path):
    """dvipsnam.def의 \\DefineNamedColor{named}{Name}{cmyk}{c,m,y,k} 줄을 읽습니다.
    LaTeX 색상 이름은 대소문자를 구분하므로 원본 철자(Apricot 등)를 그대로 씁니다."""
    colors = {}
    pattern = re.compile(r"\\DefineNamedColor\{named\}\{([A-Za-z0-9]+)\}\s*\{cmyk\}\{([^}]+)\}")
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                m = pattern.search(line)
                if m:
                    try:
                        c, mm, y, k = (float(x) for x in m.group(2).split(","))
                    except ValueError:
                        continue
                    colors[m.group(1)] = {'rgb': cmyk_to_rgb_calc(c, mm, y, k),
                                          'cmyk': (c, mm, y, k), 'exact': 'cmyk'}
    except FileNotFoundError:
        pass
    return colors

def load_names(path):
    names = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                name = line.strip(" \n\r\t\ufeff").replace("’", "'")
                if name: names.append(name)
    except FileNotFoundError:
        pass
    return names

# --- 5. 메인 앱 위젯 ---
class LatexColorTabs(QWidget):
    def __init__(self, per_tab=70):
        super().__init__()
        self.setWindowTitle("LaTeX Colors Palette")
        self.per_tab = per_tab
        self.all_palettes = {}  # 모든 패널 데이터를 담는 캐시 공간
        self.current_color = None

        layout = QVBoxLayout()
        self.temp_usercolors = {}

        # 팔레트 선택 콤보박스
        self.combo_box = QComboBox()
        self.combo_box.addItems([
            "base (xcolor)",
            "dvipsnames (graphicx)",
            "x11names (xcolor)",
            "svgnames (xcolor)",
            "latexcolors",
            "xkcdcolors",
            "usercolordef (local)"
        ])
        self.combo_box.currentIndexChanged.connect(self.on_combo_changed)
        layout.addWidget(self.combo_box)

        # 상단 복사 버튼들
        btn_layout = QHBoxLayout()
        self.copy_name_btn = QPushButton("색상 이름 복사")
        self.copy_hex_btn = QPushButton("HEX 값 복사")
        self.copy_rgb_btn = QPushButton("RGB 값 복사")
        self.copy_cmyk_btn = QPushButton("CMYK 값 복사")

        self.copy_name_btn.clicked.connect(self.copy_name)
        self.copy_hex_btn.clicked.connect(self.copy_hex)
        self.copy_rgb_btn.clicked.connect(self.copy_rgb)
        self.copy_cmyk_btn.clicked.connect(self.copy_cmyk)

        btn_layout.addWidget(self.copy_name_btn)
        btn_layout.addWidget(self.copy_hex_btn)
        btn_layout.addWidget(self.copy_rgb_btn)
        btn_layout.addWidget(self.copy_cmyk_btn)
        layout.addLayout(btn_layout)

        # 검색 영역 (텍스트 + 체크박스)
        search_layout = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("색상명 검색...")
        self.search.textChanged.connect(self.trigger_search)
        search_layout.addWidget(self.search)

        self.global_search_cb = QCheckBox("모든 패널 검색")
        self.global_search_cb.stateChanged.connect(self.trigger_search)
        search_layout.addWidget(self.global_search_cb)
        layout.addLayout(search_layout)

        # RGB 검색창
        rgb_layout = QHBoxLayout()
        self.r_input = QLineEdit(); self.r_input.setPlaceholderText("R (0~255)")
        self.g_input = QLineEdit(); self.g_input.setPlaceholderText("G (0~255)")
        self.b_input = QLineEdit(); self.b_input.setPlaceholderText("B (0~255)")

        # 💡 오차 범위 조절 스핀박스 추가
        self.tol_input = QSpinBox()
        self.tol_input.setRange(0, 255) # 0부터 255까지 설정 가능
        self.tol_input.setValue(20)     # 기본값을 20으로 설정
        self.tol_input.setPrefix("오차 ± ")
        self.tol_input.setToolTip("검색 허용 오차 (0 = 정확히 일치)")

        self.rgb_button = QPushButton("RGB 검색")
        self.rgb_button.clicked.connect(self.rgb_search)
        self.rgb_button.setDefault(True)
        self.rgb_button.setAutoDefault(True)

        rgb_layout.addWidget(self.r_input)
        rgb_layout.addWidget(self.g_input)
        rgb_layout.addWidget(self.b_input)
        rgb_layout.addWidget(self.tol_input) # 스핀박스 배치
        rgb_layout.addWidget(self.rgb_button)
        layout.addLayout(rgb_layout)

        # 탭 위젯
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # 정보 + 미리보기 박스
        self.info = QLabel("색상을 클릭하세요")
        self.info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info)

        self.preview = QFrame()
        self.preview.setFixedHeight(100)
        self.preview.setFrameShape(QFrame.Box)
        layout.addWidget(self.preview)

        self.setLayout(layout)

        # # 💡 [추가] F9 단축키 설정 (현재 위젯 어디서든 작동)
        # self.shortcut_f4 = QShortcut(QKeySequence("F4"), self)
        # self.shortcut_f4.activated.connect(self.fill_and_search_rgb)

        # 상태바 기본 메시지
        self.default_status_msg = "단축키 - F4: 유사 색상 | F8: 보색 검색 | F5: 검색 초기화"
        self.status = QLabel(self.default_status_msg)
        self.status.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.status)

        # F4: 유사 색상 검색
        self.shortcut_f4 = QShortcut(QKeySequence("F4"), self)
        self.shortcut_f4.activated.connect(self.fill_and_search_rgb)

        # F5 & Ctrl+R: 앱 초기화 (기존에 만들어두신 reset_app 연결)
        self.shortcut_f5 = QShortcut(QKeySequence("F5"), self)
        self.shortcut_f5.activated.connect(self.reset_app)

        # F8: 보색 검색
        self.shortcut_f8 = QShortcut(QKeySequence("F8"), self)
        self.shortcut_f8.activated.connect(self.fill_and_search_complementary)

        self.shortcut_ctrl_r = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcut_ctrl_r.activated.connect(self.reset_app)

        # 앱 시작: 모든 파일 읽고 초기화
        self.load_all_palettes()
        self.on_combo_changed()

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        copy_name_action = QAction("색상 이름 복사", self)
        copy_hex_action = QAction("HEX 복사", self)
        copy_rgb_action = QAction("RGB 복사", self)
        copy_cmyk_action = QAction("CMYK 복사", self)

        copy_name_action.triggered.connect(self.copy_name)
        copy_hex_action.triggered.connect(self.copy_hex)
        copy_rgb_action.triggered.connect(self.copy_rgb)
        copy_cmyk_action.triggered.connect(self.copy_cmyk)

        menu.addAction(copy_name_action)
        menu.addAction(copy_hex_action)
        menu.addAction(copy_rgb_action)
        menu.addAction(copy_cmyk_action)

        menu.exec(event.globalPos())


    def load_all_palettes(self):
        """앱 구동 시 6개의 파일을 모두 읽어서 캐싱합니다. (정렬 순서 보장)"""
        self.all_palettes.clear()
        
        # 1. base, dvips, x11, svg는 알파벳순으로 정렬하여 저장
        self.all_palettes["base (xcolor)"] = dict(sorted(BASE_COLORS.items()))
        self.all_palettes["dvipsnames (graphicx)"] = dict(sorted(parse_dvips_def(resource_path("dvipsnam.def")).items(), key=lambda kv: kv[0].lower()))
        self.all_palettes["x11names (xcolor)"] = dict(sorted(parse_def_file(resource_path("x11nam.def")).items()))
        self.all_palettes["svgnames (xcolor)"] = dict(sorted(parse_def_file(resource_path("svgnam.def")).items()))

        # --- xkcdcolors 인기 순위 적용 로직 추가 ---
        xkcd_colors_data = load_xkcd_palette(resource_path("xkcdcolors.sty"))
        xkcd_names = load_names(resource_path("xkcd_popular.txt")) # 만들어둔 txt 읽기
        
        if xkcd_names:
            ordered_xkcd = {}
            for n in xkcd_names:
                # 1. 양옆의 공백, 줄바꿈, 쉼표(,)를 모두 제거
                clean_name = n.strip(" ,\n\r")
                
                # 2. 만약 txt 파일에 xkcd를 빼먹고 썼더라도 자동으로 붙여줌
                if not clean_name.startswith("xkcd"):
                    clean_name = "xkcd" + clean_name
                    
                # 3. 딕셔너리 키와 완벽하게 일치하는지 확인 후 삽입
                if clean_name in xkcd_colors_data:
                    ordered_xkcd[clean_name] = xkcd_colors_data[clean_name]
                    
            # 누락된 색상 뒤에 붙이기 (안전장치)
            for k, v in sorted(xkcd_colors_data.items()):
                if k not in ordered_xkcd: 
                    ordered_xkcd[k] = v
                    
            self.all_palettes["xkcdcolors"] = ordered_xkcd
        # -------------------------------------------

        # 2. latexcolors는 반드시 txt 파일(매뉴얼)의 순서를 우선하여 저장
        ltx_colors = parse_tex_colors(resource_path("latexcolors.sty"))
        ltx_names = load_names(resource_path("latexcolorsnames.txt"))
        if ltx_names:
            ordered_ltx = {}
            # txt 파일 순서대로 먼저 딕셔너리에 삽입
            for n in ltx_names:
                if n in ltx_colors:
                    ordered_ltx[n] = ltx_colors[n]
            # txt에 누락된 색상이 있다면 알파벳순으로 뒤에 추가 (안전장치)
            for k, v in sorted(ltx_colors.items()):
                if k not in ordered_ltx: 
                    ordered_ltx[k] = v
            self.all_palettes["latexcolors"] = ordered_ltx
        else:
            self.all_palettes["latexcolors"] = dict(sorted(ltx_colors.items()))

        # 3. 로컬 파일도 알파벳순 저장
        local_path = get_usercolordef_path()
        
        if local_path:
            self.all_palettes["usercolordef (local)"] = dict(sorted(parse_tex_colors(local_path).items()))
        else:
            # 파일을 찾지 못했을 때 앱이 튕기지 않도록 빈 딕셔너리로 초기화
            self.all_palettes["usercolordef (local)"] = {}
            print("안내: usercolordef.tex 파일을 찾을 수 없어 로컬 팔레트를 비워둡니다.")

        self.show_status("모든 팔레트 로드 완료")

    def on_combo_changed(self):
        # 콤보박스가 변경되면 기존 검색어를 바탕으로 다시 필터링합니다.
        self.trigger_search()

    def populate_tabs(self, items):
        """
        items: (화면표시이름, 실제색상이름, color_data, 원본패널이름) 형태의 튜플 리스트
        """
        self.tabs.clear()
        for i in range(0, len(items), self.per_tab):
            chunk = items[i:i+self.per_tab]
            tab = QWidget()
            grid = QGridLayout()
            row, col = 0, 0
            
            # 언패킹에 pal_name 추가
            for display_name, actual_name, color_data, pal_name in chunk:
                r, g, b = color_data['rgb']
                hexcode = "#{:02X}{:02X}{:02X}".format(to255(r), to255(g), to255(b))
                
                # 버튼 생성 시 pal_name도 같이 넘겨줌
                btn = ColorButton(display_name, actual_name, hexcode, color_data, self, pal_name)
                grid.addWidget(btn, row, col)
                
                col += 1
                if col > 6:
                    col = 0
                    row += 1
                    
            tab.setLayout(grid)
            self.tabs.addTab(tab, f"Page {i//self.per_tab + 1}")

    def show_color(self, actual_name, hexcode, color_data, display_name):
        r, g, b = color_data['rgb']
        # 0.0이나 1.0처럼 정수로 딱 떨어지면 int로 변환
        c, m, y, k = [int(v) if v == int(v) else round(v, 4) for v in color_data['cmyk']]
        
        exact = color_data['exact']
        r_i, g_i, b_i = to255(r), to255(g), to255(b)

        # 출처 문자열 설정
        if exact == "cmyk": source_txt = "[원본: CMYK]"
        elif exact == "both": source_txt = "[원본: 혼합정의(RGB/CMYK)]"
        else: source_txt = f"[원본: {exact.upper()}] (CMYK 근사변환값)"

        # 💡 1. 맨 앞에 "xkcd"가 있으면 잘라내기 (4글자 슬라이싱)
        clean_display = display_name[4:] if display_name.startswith("xkcd") else display_name

        # 💡 2. <b> 태그를 써서 두껍게 만들고, HTML 모드에 맞춰 \n 대신 <br> 사용
        self.info.setText(
            f"<b>{clean_display}</b>: {hexcode} → {{{actual_name}}} {source_txt}<br>"
            f"RGB=({r_i},{g_i},{b_i})  CMYK=({c},{m},{y},{k})"
        )
        
        pal = self.preview.palette()
        pal.setColor(QPalette.Window, QColor(hexcode))
        self.preview.setPalette(pal)
        self.preview.setAutoFillBackground(True)
        
        # 복사 기능을 위해 actual_name 과 원본 값을 상태로 저장
        self.current_color = (actual_name, (r_i, g_i, b_i), (c, m, y, k))

    def copy_name(self):
        if self.current_color:
            name = self.current_color[0]
            QGuiApplication.clipboard().setText(f"{name}")
            self.show_status(f"색상 이름 복사: {name}")

    def copy_hex(self):
        # '#' 없이 복사: \\definecolor{이름}{HTML}{RRGGBB} 에 바로 붙여넣을 수 있습니다.
        if self.current_color:
            r, g, b = self.current_color[1]
            hex_str = "{:02X}{:02X}{:02X}".format(r, g, b)
            QGuiApplication.clipboard().setText(hex_str)
            self.show_status(f"HEX 값 복사 완료: {hex_str}")

    def copy_rgb(self):
        if self.current_color:
            r, g, b = self.current_color[1]
            rgb_str = f"{r},{g},{b}"
            QGuiApplication.clipboard().setText(rgb_str)
            self.show_status(f"RGB 값 복사 완료: {rgb_str}")

    def copy_cmyk(self):
        if self.current_color:
            c, m, y, k = self.current_color[2]
            cmyk_str = f"{c},{m},{y},{k}"
            QGuiApplication.clipboard().setText(cmyk_str)
            self.show_status(f"CMYK 값 복사 완료: {cmyk_str}")
            
    def trigger_search(self):
        raw_text = self.search.text().strip()
        
        # 💡 "정확히 일치" 모드 확인: 양끝이 따옴표(" 또는 ')로 감싸져 있는지 검사
        is_exact_match = False
        if (raw_text.startswith('"') and raw_text.endswith('"') and len(raw_text) >= 2) or \
           (raw_text.startswith("'") and raw_text.endswith("'") and len(raw_text) >= 2):
            is_exact_match = True
            # 따옴표를 벗겨낸 알맹이만 추출하여 특수기호 제거
            search_query = re.sub(r'[^a-z0-9]', '', raw_text[1:-1].lower())
        else:
            # 일반 검색: 특수기호 제거
            search_query = re.sub(r'[^a-z0-9]', '', raw_text.lower())
            
        is_global = self.global_search_cb.isChecked()
        results = []

        # SHORT_NAMES = {
        #     "base (xcolor)": "base",
        #     "dvipsnames (graphicx)": "dvips",
        #     "x11names (xcolor)": "x11",
        #     "svgnames (xcolor)": "svg",
        #     "latexcolors": "latex",
        #     "usercolordef (local)": "local"
        # }
        SHORT_NAMES = {
            "base (xcolor)": "B",
            "dvipsnames (graphicx)": "D",
            "x11names (xcolor)": "X",
            "svgnames (xcolor)": "S",
            "latexcolors": "L",
            "xkcdcolors": "xk",
            "usercolordef (local)": "U"
        }

        if is_global:
            for pal_name, pal_data in self.all_palettes.items():
                short_pal = SHORT_NAMES.get(pal_name, "misc")
                for c_name, c_data in pal_data.items():
                    # 💡 수정된 부분: 비교를 위해 c_name을 소문자로 먼저 바꾼 뒤 특수기호 제거
                    clean_name = re.sub(r'[^a-z0-9]', '', c_name.lower())
                    
                    # 💡 매칭 조건 분기
                    if is_exact_match:
                        match = (search_query == clean_name) # 글자가 완벽하게 똑같을 때만
                    else:
                        match = (search_query in clean_name) # 일부만 포함되어도
                        
                    if match:
                        display_name = f"{c_name} [{short_pal}]"
                        # 결과 리스트에는 대소문자가 유지된 원본 c_name을 그대로 담습니다.
                        results.append((display_name, c_name, c_data, pal_name))
        else:
            pal_name = self.combo_box.currentText()
            pal_data = self.all_palettes.get(pal_name, {})
            for c_name, c_data in pal_data.items():
                # 💡 수정된 부분: 여기도 마찬가지로 적용
                clean_name = re.sub(r'[^a-z0-9]', '', c_name.lower())
                
                # 💡 매칭 조건 분기
                if is_exact_match:
                    match = (search_query == clean_name)
                else:
                    match = (search_query in clean_name)
                    
                if match:
                    # 여기도 대소문자가 유지된 원본 c_name을 넘깁니다.
                    results.append((c_name, c_name, c_data, pal_name))

        # 💡 전체 검색일 때만 알파벳순으로 섞어서 정렬하고,
        # 단일 패널일 때는 딕셔너리의 고유 순서(latexcolors는 매뉴얼 순서)를 그대로 유지!
        if is_global:
            results.sort(key=lambda x: x[1])

        self.populate_tabs(results)

        if search_query:
            match_type = "(정확히 일치)" if is_exact_match else ""
            self.show_status(f"검색 결과: {len(results)}개 색상 {match_type}")
        elif is_global and not search_query:
            self.show_status(f"전체 패널 색상: {len(results)}개 (알파벳순)")

    def rgb_search(self):
        try:
            r_text = self.r_input.text().strip()
            g_text = self.g_input.text().strip()
            b_text = self.b_input.text().strip()

            # 입력값이 모두 있는지 확인 (새 색상 추가 로직 제어용)
            is_complete_rgb = bool(r_text and g_text and b_text)

            # UI에서 설정한 기본 오차값
            base_tol = self.tol_input.value()

            # R 채널 처리
            if r_text:
                r = int(r_text)
                tol_r = base_tol
            else:
                r = 127
                tol_r = 128

            # G 채널 처리
            if g_text:
                g = int(g_text)
                tol_g = base_tol
            else:
                g = 127
                tol_g = 128

            # B 채널 처리
            if b_text:
                b = int(b_text)
                tol_b = base_tol
            else:
                b = 127
                tol_b = 128

        except ValueError:
            QMessageBox.warning(self, "입력 오류", "RGB 값은 0~255 범위의 정수로 입력하세요")
            return

        if any(not (0 <= v <= 255) for v, t in ((r, r_text), (g, g_text), (b, b_text)) if t):
            QMessageBox.warning(self, "입력 오류", "RGB 값은 0~255 범위의 정수로 입력하세요")
            return

        # 오차 범위 (0~1 스케일로 변환)
        tol_r_scale = tol_r / 255.0
        tol_g_scale = tol_g / 255.0
        tol_b_scale = tol_b / 255.0

        is_global = self.global_search_cb.isChecked()
        results = []

        search_target = (
            self.all_palettes
            if is_global
            else {self.combo_box.currentText(): self.all_palettes.get(self.combo_box.currentText(), {})}
        )

        SHORT_NAMES = {
            "base (xcolor)": "B",
            "dvipsnames (graphicx)": "D",
            "x11names (xcolor)": "X",
            "svgnames (xcolor)": "S",
            "latexcolors": "L",
            "xkcdcolors": "xk",
            "usercolordef (local)": "U",
        }

        # 기준 RGB → HSV 변환 (빈 값은 자동으로 127로 계산되어 중앙값을 기준으로 정렬됨)
        base_h, base_s, base_v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)

        for pal_name, pal_data in search_target.items():
            short_pal = SHORT_NAMES.get(pal_name, "misc")
            for c_name, c_data in pal_data.items():
                cr, cg, cb = c_data['rgb']  # 0~1 범위
                h, s, v = colorsys.rgb_to_hsv(cr, cg, cb)

                match = True
                
                # R 매칭: 원래 값이 0인지 확인하기 위해 r_text 사용
                if r_text == '0' and cr != 0.0:
                    match = False
                elif r_text != '0' and not ((r/255.0) - tol_r_scale <= cr <= (r/255.0) + tol_r_scale):
                    match = False
                
                # G 매칭
                if g_text == '0' and cg != 0.0:
                    match = False
                elif g_text != '0' and not ((g/255.0) - tol_g_scale <= cg <= (g/255.0) + tol_g_scale):
                    match = False
                
                # B 매칭
                if b_text == '0' and cb != 0.0:
                    match = False
                elif b_text != '0' and not ((b/255.0) - tol_b_scale <= cb <= (b/255.0) + tol_b_scale):
                    match = False

                if match:
                    display_name = f"{c_name} [{short_pal}]" if is_global else c_name
                    dh = abs(base_h - h)
                    dh = min(dh, 1.0 - dh)
                    dist = ((dh)**2 + (base_s - s)**2 + (base_v - v)**2) ** 0.5
                    results.append((display_name, c_name, c_data, pal_name, dist))

        if results:
            results.sort(key=lambda x: x[4])
            if is_global:
                results.sort(key=lambda x: (x[4], x[1]))

            self.populate_tabs([(d, c, data, p) for d, c, data, p, _ in results])
            self.show_status(f"HSB 검색 결과: {len(results)}개 색상 (가장 가까운 색: {results[0][0]})")
        
        else:
            # 모든 값이 입력되었을 때만 새 색상 추가 팝업 표시
            if is_complete_rgb:
                hexcode = "#{:02X}{:02X}{:02X}".format(r, g, b)

                msg = QMessageBox(self)
                msg.setWindowTitle("검색 결과 없음")
                msg.setText(
                    f"조건에 맞는 색상이 없습니다.\n"
                    f"입력한 RGB({r},{g},{b}) 샘플을 확인하세요.\n\n"
                    "이 색상을 usercolordef에 추가하시겠습니까?"
                )
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                # 이모지나 다른 UI 디자인 지침이 있다면 여기서 아이콘을 제거하고 이모지로 텍스트를 대체할 수도 있습니다.
                msg.setIcon(QMessageBox.Information)

                preview = QLabel()
                preview.setFixedSize(100, 50)
                preview.setStyleSheet(f"background-color: {hexcode}; border: 1px solid black;")
                msg.layout().addWidget(preview, 1, 1)

                if msg.exec() == QMessageBox.Yes:
                    default_name = f"usercolor{random.randint(100,999)}"
                    name, ok = QInputDialog.getText(
                        self, "색상 이름 지정", "그림 이름을 정해주세요:", text=default_name
                    )
                    if ok and name:
                        # 1. CMYK 근사값 계산 (0~1 범위로 정규화하여 전달)
                        cmyk_vals = rgb_to_cmyk_calc(r/255.0, g/255.0, b/255.0)
                        
                        # 2. LaTeX 정의문 생성
                        define_str = f"\\definecolor{{{name}}}{{RGB}}{{{r},{g},{b}}}"
                        QApplication.clipboard().setText(define_str)

                        # 3. 내부 dict에 추가 (계산된 cmyk_vals 적용)
                        color_entry = {
                            "rgb": (r/255.0, g/255.0, b/255.0),
                            "cmyk": cmyk_vals,
                            "exact": "rgb"
                        }

                        if "usercolordef (local)" not in self.all_palettes:
                            self.all_palettes["usercolordef (local)"] = {}

                        self.all_palettes["usercolordef (local)"][name] = color_entry
                        self.temp_usercolors[name] = color_entry

                        QMessageBox.information(
                            self, "색상 추가",
                            f"{define_str}\n\n"
                            "복사됨. usercolordef.tex에 붙여넣기 하세요."
                        )
            else:
                QMessageBox.information(self, "검색 결과 없음", "조건에 맞는 색상이 없습니다")

    def show_status(self, message):
        self.status.setText(message)
        # 3초(3000ms) 뒤에 빈 칸이 아니라 '기본 단축키 안내'로 복구
        QTimer.singleShot(3500, lambda: self.status.setText(self.default_status_msg))

    def reset_app(self):
        # F5 입력 시 로컬 파일을 포함하여 데이터를 다시 처음부터 읽어옵니다.
        self.load_all_palettes()

        # 임시 색상 다시 반영
        if "usercolordef (local)" not in self.all_palettes:
            self.all_palettes["usercolordef (local)"] = {}
        self.all_palettes["usercolordef (local)"].update(self.temp_usercolors)

        # UI 초기화
        self.search.clear()
        self.r_input.clear()
        self.g_input.clear()
        self.b_input.clear()
        self.info.setText("색상을 클릭하세요")
        self.preview.setAutoFillBackground(False)
        self.current_color = None
        self.global_search_cb.setChecked(False)

        self.trigger_search()
        self.show_status("팔레트를 새로고침하고 초기화했습니다.")
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            idx = self.tabs.currentIndex()
            if idx < self.tabs.count() - 1:
                self.tabs.setCurrentIndex(idx + 1)
        elif event.key() == Qt.Key_PageUp:
            idx = self.tabs.currentIndex()
            if idx > 0:
                self.tabs.setCurrentIndex(idx - 1)
        else:
            super().keyPressEvent(event)

    def fill_and_search_rgb(self):
        # 1. 선택된 색상이 없으면 무시
        if not self.current_color:
            self.status.setText("먼저 기준이 될 색상을 클릭해주세요.")
            return

        # 2. current_color에서 RGB 값 추출
        # self.current_color 형태: (actual_name, (r, g, b), (c, m, y, k))
        _, rgb_tuple, _ = self.current_color
        r, g, b = rgb_tuple

        # 3. RGB 검색창 필드에 값 입력
        self.r_input.setText(str(r))
        self.g_input.setText(str(g))
        self.b_input.setText(str(b))

        # 4. 전체 패널 검색 체크박스를 켜주면 더 유용할 수 있습니다 (선택 사항)
        self.global_search_cb.setChecked(True)

        # 5. 기존에 만들어두신 RGB 검색 함수(rgb_search) 강제 호출
        self.rgb_search()
        
        self.status.setText(f"선택한 색상({r},{g},{b}) 기준으로 비슷한 색상을 검색합니다.")

    def fill_and_search_complementary(self):
        # 1. 선택된 색상이 없으면 안내 후 종료
        if not self.current_color:
            self.show_status("먼저 기준이 될 색상을 클릭해주세요.")
            return

        # 2. current_color에서 RGB 값 추출
        # self.current_color 형태: (actual_name, (r, g, b), (c, m, y, k))
        _, rgb_tuple, _ = self.current_color
        r, g, b = rgb_tuple

        # 💡 3. 보색 계산 (255 - 원래 색상값)
        comp_r = 255 - r
        comp_g = 255 - g
        comp_b = 255 - b

        # 4. RGB 검색창 필드에 보색 값 입력
        self.r_input.setText(str(comp_r))
        self.g_input.setText(str(comp_g))
        self.b_input.setText(str(comp_b))

        # 5. 보색은 보통 다른 팔레트에 있을 확률이 높으므로 전체 패널 검색 활성화
        self.global_search_cb.setChecked(True)

        # 6. RGB 검색 함수 실행
        self.rgb_search()
        
        # 7. 상태바에 현재 무슨 기준으로 검색했는지 명시
        self.show_status(f"선택한 색상의 보색({comp_r},{comp_g},{comp_b}) 기준으로 검색합니다.")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Windows는 .ico, 그 외(Linux/macOS)는 .png를 창 아이콘으로 사용
    icon_name = "latexcolorpalette.ico" if sys.platform == "win32" else "latexcolorpalette.png"
    app.setWindowIcon(QIcon(resource_path(icon_name)))

    window = LatexColorTabs(per_tab=70)
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec())

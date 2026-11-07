# LaTeX Colors Palette

LaTeX에서 쓸 수 있는 색상 이름을 한 화면에서 훑어보고, 이름·RGB·CMYK 값을 바로 복사하는 데스크탑 도구입니다. (PySide6 / Qt)

`xcolor`, `dvipsnames`, `x11names`, `svgnames`, `latexcolors`, `xkcdcolors` 패키지의 색상을 모두 모아 두었고, 이름 검색과 RGB 값 기반 유사색·보색 검색을 지원합니다. 원하는 색이 어느 패키지에도 없으면 `\definecolor` 정의문을 만들어 클립보드에 복사해 줍니다.

## 지원하는 팔레트

| 팔레트 | 색상 수 | 출처 / 사용 방법 |
|---|---:|---|
| `base (xcolor)` | 19 | xcolor 기본 색상 (`\usepackage{xcolor}`) |
| `dvipsnames (graphicx)` | 68 | `\usepackage[dvipsnames]{xcolor}` (`dvipsnam.def`에서 읽음) |
| `x11names (xcolor)` | 317 | `\usepackage[x11names]{xcolor}` |
| `svgnames (xcolor)` | 151 | `\usepackage[svgnames]{xcolor}` |
| `latexcolors` | 758 | `\usepackage{latexcolors}` (Tobias Plüss) |
| `xkcdcolors` | 937 | `\usepackage{xkcdcolors}` (xkcd 색상 설문, 인기순 정렬) |
| `usercolordef (local)` | 가변 | 사용자 정의 `usercolordef.tex` |

> 색상 수는 이 저장소에 포함된 데이터 파일 기준입니다.

## 주요 기능

- **팔레트 탐색**: 콤보박스로 팔레트를 고르면 색상 버튼이 70개씩 `Page N` 탭으로 나뉘어 표시됩니다. 글자색은 배경 밝기에 맞춰 자동으로 바뀝니다.
- **색상 정보**: 버튼을 클릭(또는 키보드 포커스)하면 하단에 HEX, LaTeX 색상 이름, RGB, CMYK 값과 미리보기가 나타납니다. 원본이 CMYK가 아닌 색의 CMYK는 근사 변환값이며, 정보창에 `[원본: …]`으로 구분해 표시합니다.
- **복사**: `색상 이름 복사` / `HEX 값 복사` / `RGB 값 복사` / `CMYK 값 복사` 버튼 또는 우클릭 메뉴. HEX는 `#` 없이 `RRGGBB`로 복사되어 `\definecolor{이름}{HTML}{RRGGBB}`에 바로 붙여 넣을 수 있습니다.
- **이름 검색**: 대소문자·공백·특수문자를 무시하고 부분 일치로 찾습니다. 검색어를 따옴표(`"red"` 또는 `'red'`)로 감싸면 정확히 일치하는 이름만 보여 줍니다. `모든 패널 검색`을 켜면 전체 팔레트를 알파벳순으로 검색하며, 이름 뒤에 팔레트 약어가 붙습니다.
- **RGB 검색**: R·G·B(0–255)와 허용 오차(기본 ±20)를 입력하면 조건에 맞는 색을 HSB 거리 기준으로 가까운 순서로 보여 줍니다. 비워 둔 채널은 조건에서 제외됩니다. 값을 `0`으로 입력한 채널은 오차와 관계없이 정확히 0인 색만 찾습니다.
- **새 색상 추가**: 세 값을 모두 입력했는데 결과가 없으면 `\definecolor{이름}{RGB}{r,g,b}`를 클립보드에 복사해 줍니다. 이를 `usercolordef.tex`에 붙여 넣으세요. 앱을 실행하는 동안에는 `usercolordef (local)` 팔레트에도 임시로 추가됩니다.

### 단축키

| 키 | 동작 |
|---|---|
| `F4` | 선택한 색과 비슷한 색 검색 (전체 팔레트 대상) |
| `F8` | 선택한 색의 보색(255 − 값) 검색 (전체 팔레트 대상) |
| `F5` / `Ctrl+R` | 모든 팔레트 파일을 다시 읽고 검색 상태 초기화 |
| `PageUp` / `PageDown` | 이전 / 다음 페이지 탭 |

### 팔레트 약어

전체 패널 검색 결과에서 이름 뒤에 붙는 약어입니다.

`B` base · `D` dvipsnames · `X` x11names · `S` svgnames · `L` latexcolors · `xk` xkcdcolors · `U` usercolordef

## usercolordef.tex 위치

`usercolordef (local)` 팔레트는 다음 순서로 파일을 찾습니다.

1. 앱을 **실행한 현재 폴더**의 `usercolordef.tex`
2. TeX 배포판에서 `kpsewhich usercolordef.tex`로 찾은 경로

둘 다 없으면 빈 팔레트로 시작하고 콘솔에 안내만 출력합니다. macOS와 Linux에서는 `kpsewhich`를 찾을 수 있도록 `/Library/TeX/texbin`, `/opt/homebrew/bin`, `/usr/local/texlive/2026/bin/x86_64-linux` 등을 PATH에 덧붙여 검색합니다. TeX Live 버전이나 경로가 다르면 `latexcolorpalette.py`의 `get_usercolordef_path()`를 수정하세요.

`usercolordef.tex`는 `\definecolor{이름}{rgb|RGB|HTML|cmyk}{값}` 형식의 줄을 읽습니다.

## 실행 (소스에서)

Python 3와 PySide6가 필요합니다. Python 3.13 + PySide6 6.12 + PyInstaller 6.22 조합(Linux)에서 빌드와 실행을 확인했습니다.

```bash
pip install -r requirements.txt
python latexcolorpalette.py
```

데이터 파일은 **현재 작업 폴더**에서 읽으므로 반드시 이 저장소 폴더 안에서 실행하세요.

## 실행 파일 빌드 (PyInstaller)

```bash
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm latexcolorpalette.spec
```

결과물은 `dist/latexcolorpalette`(Windows는 `latexcolorpalette.exe`, macOS는 `LaTeX Color Palette.app`)에 만들어집니다. 필요한 데이터 파일(`*.sty`, `*.def`, `*.txt`)은 `.spec`의 `datas`로 함께 묶이며 실행 시 임시 폴더에서 읽습니다.

- 아이콘은 `.spec`이 플랫폼별로 고릅니다(Windows `.ico`, macOS `.icns`, Linux는 실행 파일 아이콘 미지원).
- PyInstaller는 크로스 컴파일을 지원하지 않습니다. Windows용은 Windows에서, macOS용은 macOS에서 빌드하세요.
- 단일 파일 방식이라 첫 실행 때 압축을 푸느라 시작이 다소 느립니다.
- `upx=True`가 설정되어 있습니다. UPX가 설치되어 있지 않으면 무시됩니다. Windows에서 UPX로 압축하면 일부 백신이 오탐할 수 있으니, 문제가 생기면 `upx=False`로 바꾸세요.
- `usercolordef.tex`는 실행 파일 안에 묶이지 않습니다. 실행 파일과 같은 폴더에서 실행하거나 TeX 배포판에 설치해 두세요.
- Linux에서는 Qt의 xcb 플랫폼 플러그인이 `libxcb-cursor0`을 필요로 합니다. 없으면 `sudo apt install libxcb-cursor0` 등으로 설치하세요.

## 저장소 구성

| 파일 | 설명 |
|---|---|
| `latexcolorpalette.py` | 앱 본체 (UI, 파서, 검색) |
| `latexcolorpalette.spec` | PyInstaller 빌드 설정 |
| `requirements.txt` | 실행에 필요한 Python 패키지 |
| `latexcolorpalette.ico` / `.icns` / `.png` | 앱 아이콘 (Windows / macOS / Linux·창 아이콘) |
| `latexcolors.sty`, `latexcolorsnames.txt` | latexcolors 정의 / 매뉴얼 표시 순서 |
| `xkcdcolors.sty`, `xkcd_popular.txt` | xkcd 색상 정의 / 인기순 목록 |
| `x11nam.def`, `svgnam.def`, `dvipsnam.def` | xcolor의 x11names / svgnames / dvipsnames 정의 |

## 사용 시 참고

- LaTeX 색상 이름은 **대소문자를 구분**합니다. 복사한 이름은 표시된 철자 그대로 쓰세요.
- 해당 패키지를 불러오지 않으면 그 팔레트의 이름은 문서에서 쓸 수 없습니다. 위 표의 사용 방법을 확인하세요.
- 화면에 보이는 RGB/HEX는 모니터 기준 값이며, CMYK는 인쇄용 근사치입니다. 인쇄 결과가 중요하면 원본이 CMYK인 색(`[원본: CMYK]`)을 쓰는 편이 안전합니다.

## 라이선스와 출처

색상 데이터 파일은 각각의 원저작자와 라이선스를 따릅니다. 자세한 내용은 각 파일 머리말을 확인하세요.

- `latexcolors.sty` — Tobias Plüss, LPPL 1.3
- `xkcdcolors.sty` — Romano Giannetti, LPPL 1.3c (xkcd 색상 설문 데이터 기반)
- `x11nam.def`, `svgnam.def` — xcolor, Dr. Uwe Kern
- `dvipsnam.def` — David Carlisle, Sebastian Rahtz

앱 코드 자체는 MIT 라이선스로 배포합니다.


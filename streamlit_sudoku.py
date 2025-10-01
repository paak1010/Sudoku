import streamlit as st
import random
from datetime import datetime
import time # 타이머를 위해 time 모듈 사용

# --- CSS 스타일 정의 (PyQt5 레이아웃 재현) ---
# PyQt5의 QGridLayout처럼 버튼을 빽빽하게 배치하고, 고정된 크기를 부여합니다.
CELL_SIZE = "40px" # PyQt5 위젯 크기 비율을 고려하여 40px로 조정

CELL_STYLE = f"""
<style>
/* 1. Streamlit 앱 전체 패딩 조정 */
.stApp {{
    padding-top: 20px;
}}

/* 2. Grid 컨테이너 스타일 (9개의 동일한 크기 컬럼 정의) */
.sudoku-grid-row {{
    display: flex; /* 플렉스박스로 컬럼 간격을 최소화 */
    width: fit-content;
    margin: 0 auto; /* 중앙 정렬 */
    /* st.columns 대신 flex를 사용해 셀을 빽빽하게 배치 */
}}

/* 3. 입력 필드 컨테이너 마진 제거 */
div[data-testid="stTextInput"] {{
    margin: 0 !important; 
    padding: 0 !important;
}}

/* 4. 셀 입력 필드 자체 스타일: 크기 고정 및 중앙 정렬 */
div[data-testid="stTextInput"] > div > input {{
    text-align: center !important;
    font-weight: bold;
    font-size: 1.2em !important;
    padding: 0 !important;
    height: {CELL_SIZE} !important; 
    width: {CELL_SIZE} !important; 
    box-sizing: border-box;
    margin: 0;
    border: none; /* 테두리는 부모 Div에 인라인으로 적용 */
    border-radius: 0;
}}

/* 5. 고정된 셀 (fixed-cell) 스타일 */
.fixed-cell {{
    text-align: center;
    font-weight: bold;
    font-size: 1.2em;
    height: {CELL_SIZE}; 
    line-height: {CELL_SIZE}; /* 수직 중앙 정렬 */
    width: {CELL_SIZE};
    background-color: #f0f2f6; 
    color: black;
    box-sizing: border-box;
    margin: 0;
}}

/* 🏆 모든 Streamlit 버튼 디자인 통일 🏆 */
.stButton > button {{
    background-color: #4CAF50; 
    color: white;             
    border: none;             
    padding: 10px 15px;       
    font-size: 16px;          
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 8px;       
    transition: background-color 0.3s;
}}

.stButton > button:hover {{
    background-color: #45a049; 
}}

/* Streamlit에서 생성되는 경고 메시지 스타일 */
.stAlert {{
    margin-top: 10px;
    margin-bottom: 0;
    padding: 10px;
}}
</style>
"""

# 스도쿠 초기 정답판 (PyQt UI에서 가져온 AVal의 초기값)
# 1 2 3 4 5 6 7 8 9
# 4 5 6 7 8 9 1 2 3
# 7 8 9 1 2 3 4 5 6
# 2 3 1 8 9 7 5 6 4
# 5 6 4 2 3 1 8 9 7
# 8 9 7 5 6 4 2 3 1
# 3 1 2 6 4 5 9 7 8
# 6 4 5 9 7 8 3 1 2
# 9 7 8 3 1 2 6 4 5
INITIAL_SOLUTION = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
    ["4", "5", "6", "7", "8", "9", "1", "2", "3"],
    ["7", "8", "9", "1", "2", "3", "4", "5", "6"],
    ["2", "3", "1", "8", "9", "7", "5", "6", "4"],
    ["5", "6", "4", "2", "3", "1", "8", "9", "7"],
    ["8", "9", "7", "5", "6", "4", "2", "3", "1"],
    ["3", "1", "2", "6", "4", "5", "9", "7", "8"],
    ["6", "4", "5", "9", "7", "8", "3", "1", "2"],
    ["9", "7", "8", "3", "1", "2", "6", "4", "5"]
]

# --- 게임 상태 초기화 ---

def initialize_session_state():
    """세션 상태를 초기화하고 첫 게임을 시작합니다."""
    if 'initialized' not in st.session_state:
        st.session_state.initial_solution = INITIAL_SOLUTION
        st.session_state.difficulty_prob = 0.7  # PyQt의 pEdit 기본값
        st.session_state.result_message = "버튼을 클릭하고 1~9사이의 정수를 입력하세요, Finish를 누르면 채점 결과를 알려드립니다."
        
        st.session_state.board = [[""] * 9 for _ in range(9)]
        st.session_state.correct_board = [[""] * 9 for _ in range(9)]
        st.session_state.game_start_time = datetime.now()
        st.session_state.timer_running = False
        st.session_state.time_finished_display = "00:00"
        st.session_state.initial_cells = set()
        st.session_state.cell_colors = {}
        st.session_state.initialized = True
        
        # PyQt의 __init__에서 ShuffleClick이 호출되는 것을 모방
        shuffle_click(initial_run=True)

# --- 게임 로직 함수 ---

def shuffle_click(initial_run=False):
    """보드를 셔플하고 새 게임을 시작합니다."""
    if not initial_run:
        try:
            # 난이도 입력 필드에서 값을 가져옴 (PyQt의 pEdit 역할)
            prob = float(st.session_state.get('difficulty_prob_input', st.session_state.difficulty_prob))
            st.session_state.difficulty_prob = max(0.0, min(1.0, prob)) 
        except ValueError:
            st.session_state.difficulty_prob = 0.7 
    
    AVal = st.session_state.initial_solution
    
    # 1. 숫자 셔플
    random19 = list(range(1, 10))
    random.shuffle(random19)
    
    # 2. 정답 보드 생성
    correct_board = [[str(random19[int(AVal[i][j]) - 1]) for j in range(9)] for i in range(9)]
    
    # 3. 사용자 보드 생성 (Blank 적용)
    new_board = [[correct_board[i][j] for j in range(9)] for i in range(9)]
    initial_cells = set()
    prob = st.session_state.difficulty_prob
    
    st.session_state.cell_colors = {} 
    
    for i in range(9):
        for j in range(9):
            if random.random() > prob: 
                new_board[i][j] = ""
            else:
                initial_cells.add((i, j))
            
            # 초기 고정 셀은 'black' (PyQt 스타일)
            color = 'black' if (i, j) in initial_cells else 'red'
            st.session_state.cell_colors[(i, j)] = color

    st.session_state.correct_board = correct_board
    st.session_state.board = new_board
    st.session_state.initial_cells = initial_cells
    st.session_state.game_start_time = datetime.now()
    st.session_state.timer_running = True
    st.session_state.result_message = "빈 칸에 1~9 사이의 숫자를 입력하세요."
    st.session_state.time_finished_display = "00:00"
    
    st.rerun() 

def update_cell_value(r, c):
    """텍스트 입력 필드가 변경될 때 호출됩니다. (PyQt의 keyPressEvent 역할)"""
    new_val = st.session_state[f"cell_{r}_{c}"].strip()
    
    # 1~9 사이의 숫자만 허용하고, 그 외는 빈 값으로 처리
    if new_val.isdigit() and 1 <= int(new_val) <= 9:
        st.session_state.board[r][c] = new_val
        st.session_state.cell_colors[(r, c)] = 'red' # PyQt의 keyPressEvent에서 색을 red로 바꾸는 것 재현
    elif new_val == "":
        st.session_state.board[r][c] = ""
        st.session_state.cell_colors[(r, c)] = 'red' 
    else:
        # 잘못된 입력은 무시하고 이전 값으로 롤백
        st.session_state[f"cell_{r}_{c}"] = st.session_state.board[r][c]
        
def complete_test_click():
    """채점 로직을 실행합니다. (PyQt의 CompleteTestClick 역할)"""
    st.session_state.timer_running = False 

    is_correct = True
    
    # 시간 계산 및 저장
    elapsed_time = datetime.now() - st.session_state.game_start_time
    minutes = int(elapsed_time.total_seconds() // 60)
    seconds = int(elapsed_time.total_seconds() % 60)
    current_time_display = f"{minutes:02d}:{seconds:02d}"
    st.session_state.time_finished_display = current_time_display

    # 채점 및 색상 결정
    for i in range(9):
        for j in range(9):
            current_val = st.session_state.board[i][j]
            correct_val = st.session_state.correct_board[i][j]
            
            # PyQt와 동일하게, 정답과 다른 모든 셀 (사용자 입력 + 빈 칸)을 빨간색으로 표시
            if current_val != correct_val:
                st.session_state.cell_colors[(i, j)] = 'red' 
                is_correct = False
            else:
                st.session_state.cell_colors[(i, j)] = 'black'

    # 결과 메시지 출력 (resEdit 역할)
    if is_correct:
        st.session_state.result_message = f"정답입니다! 퍼즐을 풀었습니다. 소요 시간: {current_time_display}"
        st.balloons()
    else:
        st.session_state.result_message = "아쉽지만, 정답이 아닙니다. 빨간색으로 표시된 부분을 확인하세요."
        
    st.rerun() 

# --- 메인 UI 구성 ---

def main_app():
    initialize_session_state()
    st.markdown(CELL_STYLE, unsafe_allow_html=True) 
    
    st.title("Streamlit Sudoku 🧩 (PyQt Style)")
    
    # --- 컨트롤 패널 (PyQt UI의 배치 재현) ---
    col_empty1, col_shuffle, col_prob_label, col_prob_edit, col_timer, col_finish, col_empty2 = st.columns([1, 2, 1, 1, 1.5, 2, 1])
    
    # 타이머 표시 (PyQt의 label 역할)
    if st.session_state.timer_running:
        elapsed_time = datetime.now() - st.session_state.game_start_time
        minutes = int(elapsed_time.total_seconds() // 60)
        seconds = int(elapsed_time.total_seconds() % 60)
        time_display = f"{minutes:02d}:{seconds:02d}"
    else:
        time_display = st.session_state.time_finished_display
        
    # 타이머
    with col_timer:
        st.markdown(f"<div style='background-color: white; text-align: center; font-weight: bold; padding: 5px; border: 1px solid #ccc; font-size: 16px; margin-top: 20px;'>⏱️ {time_display}</div>", unsafe_allow_html=True)
    
    # 난이도 입력 (PyQt의 pEdit 역할)
    with col_prob_edit:
        st.text_input("난이도 확률", 
                             value=f"{st.session_state.difficulty_prob:.2f}", 
                             key='difficulty_prob_input', 
                             label_visibility="collapsed")
    
    # 난이도 레이블
    col_prob_label.markdown("<div style='text-align: right; margin-top: 20px; font-size: 13px;'>빈칸 확률 (0~1):</div>", unsafe_allow_html=True)
    
    # Shuffle 버튼
    if col_shuffle.button("Shuffle", key="ShuffleButton", use_container_width=True):
        shuffle_click()
    
    # Finish 버튼
    if col_finish.button("Finish", key="FinishButton", use_container_width=True):
        complete_test_click()

    # --- 설명 메시지 (PyQt의 textEdit 역할) ---
    st.markdown("---")
    st.markdown(f"<p style='text-align: center; margin: 0; padding: 0;'>{st.session_state.result_message}</p>", unsafe_allow_html=True)
    st.markdown("---")

    # --- Sudoku 그리드 영역 (9x9 격자판) ---
    # 전체 보드를 중앙에 배치하기 위한 컬럼
    grid_col_left, grid_col_center, grid_col_right = st.columns([1, 4, 1])
    
    with grid_col_center:
        # 💡 9x9 격자판 전체의 테두리(왼쪽/위쪽)를 그리는 컨테이너
        st.markdown(f"""
        <div style="border-top: 3px solid black; border-left: 3px solid black; width: fit-content; margin: 0 auto;">
        """, unsafe_allow_html=True)

        THIN_BORDER_STYLE = "1px solid #ccc"
        THICK_BORDER_STYLE = "3px solid black"
        CELL_SIZE_PX = "40px"

        for i in range(9):
            # 행을 표시하는 flex 컨테이너 (CSS에서 .sudoku-grid-row로 정의)
            st.markdown('<div class="sudoku-grid-row">', unsafe_allow_html=True) 
            
            # 현재 행이 3x3 블록의 아래 경계선인지 확인 (인덱스 2와 5, 그리고 마지막 행)
            is_thick_row = i == 8 or i in [2, 5]
            
            for j in range(9):
                is_initial_cell = (i, j) in st.session_state.initial_cells
                current_val = st.session_state.board[i][j]
                cell_key = f"cell_{i}_{j}"
                cell_color = st.session_state.cell_colors.get((i, j), 'red')
                
                # 3x3 블록 구분선 계산
                is_thick_col = j == 8 or j in [2, 5]
                
                border_right_style = THICK_BORDER_STYLE if is_thick_col else THIN_BORDER_STYLE
                border_bottom_style = THICK_BORDER_STYLE if is_thick_row else THIN_BORDER_STYLE

                # 셀의 기본 스타일 (컨테이너 역할)
                cell_container_style = f"display: flex; flex-direction: column; border-right: {border_right_style}; border-bottom: {border_bottom_style};"

                # 💡 각 셀을 위한 컨테이너를 생성 (컬럼 없이 플렉스 아이템으로 사용)
                st.markdown(f'<div style="{cell_container_style}">', unsafe_allow_html=True)
                
                if is_initial_cell:
                    # 고정된 셀
                    cell_html = f"""
                    <div class="fixed-cell">
                        {current_val}
                    </div>
                    """
                    st.markdown(cell_html, unsafe_allow_html=True)
                else:
                    # 사용자 입력 가능 셀
                    
                    # 1. input 태그의 폰트 색상 및 보더 스타일 강제 주입
                    st.markdown(f"""
                    <style>
                    div[data-testid="stTextInput"] input[key="{cell_key}"] {{
                        color: {cell_color} !important;
                        /* 크기는 CSS에서 고정되었으므로 여기서는 보더만 조정 */
                        border: none !important; /* 기본 보더 제거 */
                    }}
                    /* 인풋 필드의 부모 컨테이너가 40px*40px을 차지하도록 강제 */
                    div[data-testid="stTextInput"][data-input-id*="{cell_key}"] {{
                        width: {CELL_SIZE_PX} !important;
                        height: {CELL_SIZE_PX} !important;
                    }}
                    </style>
                    """, unsafe_allow_html=True)
                    
                    # 2. st.text_input 위젯
                    st.text_input(" ", 
                                   value=current_val, 
                                   max_chars=1, 
                                   key=cell_key, 
                                   on_change=update_cell_value, 
                                   args=(i, j),
                                   label_visibility="collapsed",
                                   placeholder=" ")
                
                # 셀 컨테이너 닫기
                st.markdown('</div>', unsafe_allow_html=True)

            # 행 컨테이너 닫기
            st.markdown('</div>', unsafe_allow_html=True) 
        
        # 9x9 격자판 전체의 테두리 닫기
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown("---")
            
if __name__ == "__main__":
    main_app()

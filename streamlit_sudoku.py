import streamlit as st
import random
from datetime import datetime
import time # 타이머 업데이트를 위해 time 모듈 추가

# --- 📐 디자인 상수 ---
CELL_SIZE_PX = 45 # 셀의 크기 (정사각형)
GRID_WIDTH_PX = CELL_SIZE_PX * 9 + 10 # 전체 그리드 너비 (테두리 여백 포함)

# --- 🎯 CSS 스타일 정의 (HTML 테이블 기반 완벽 그리드) 🎯 ---
CELL_STYLE = f"""
<style>
/* Streamlit 기본 스타일 조정 */
div[data-testid="stTextInput"] {{
    margin: 0 !important;
    padding: 0 !important;
}}
div[data-testid="stTextInput"] > label {{
    display: none; /* 레이블 숨김 */
}}

/* 🏆 버튼 스타일 유지 🏆 */
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

/* 9x9 스도쿠 보드 전체 컨테이너 */
.sudoku-container {{
    width: {GRID_WIDTH_PX}px;
    margin: 20px auto; /* 중앙 정렬 */
}}

/* HTML 테이블 스타일 */
.sudoku-table {{
    border-collapse: collapse;
    width: 100%;
    border: 3px solid #333; /* 전체 보드 두꺼운 테두리 */
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}}

/* 모든 셀 (td) 기본 스타일 */
.sudoku-table td {{
    width: {CELL_SIZE_PX}px;
    height: {CELL_SIZE_PX}px;
    padding: 0;
    margin: 0;
    text-align: center;
    vertical-align: top; 
    border: 1px solid #ccc; /* 얇은 기본 테두리 */
}}

/* 3x3 블록 간의 굵은 테두리 */
.sudoku-table tr:nth-child(3n) td {{
    border-bottom-width: 3px;
    border-bottom-color: #333;
}}
.sudoku-table td:nth-child(3n) {{
    border-right-width: 3px;
    border-right-color: #333;
}}

/* 맨 마지막 행/열의 굵은 테두리 제거 */
.sudoku-table tr:last-child td {{ border-bottom: none; }}
.sudoku-table td:last-child {{ border-right: none; }}

/* 고정된 셀 (숫자가 주어진 셀) */
.fixed-cell {{
    background-color: #eee;
    color: black;
    font-weight: bold;
    font-size: 1.2em;
    line-height: {CELL_SIZE_PX}px; 
}}

/* 입력 필드 스타일: Streamlit input 위젯의 내부 input 태그를 제어 */
.sudoku-table input {{
    width: 100%;
    height: 100%;
    padding: 0;
    margin: 0;
    border: none;
    text-align: center;
    font-weight: bold;
    font-size: 1.2em;
}}

/* Timer Label (PyQt5의 label) */
.timer-display {{
    background-color: white;
    text-align: center;
    font-weight: bold;
    padding: 5px;
    border: 1px solid #ccc;
    font-size: 16px;
    margin-top: 5px;
    line-height: 1.5;
}}

/* PyQt5의 textEdit (안내 메시지) */
.info-message {{
    text-align: center; 
    padding: 10px; 
    background-color: #f0f0f0; 
    border: 1px solid #ccc;
}}
</style>
"""

# 스도쿠 초기 정답판 
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

# --- 게임 상태 초기화 및 로직 함수 ---

def initialize_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.initial_solution = INITIAL_SOLUTION
        st.session_state.difficulty_prob = 0.7
        st.session_state.result_message = "Shuffle 버튼을 눌러 게임을 시작하세요"
        st.session_state.board = [[""] * 9 for _ in range(9)]
        st.session_state.correct_board = [[""] * 9 for _ in range(9)]
        # 시작 시간 대신, 경과 시간(seconds_elapsed)을 저장합니다.
        st.session_state.seconds_elapsed = 0
        st.session_state.last_time_check = datetime.now()
        st.session_state.timer_running = False
        st.session_state.time_finished_display = "00:00"
        st.session_state.initial_cells = set()
        st.session_state.cell_colors = {}
        st.session_state.initialized = True
        shuffle_click(initial_run=True)
    
    # 타이머가 실행 중이면 시간을 업데이트하고 rerun을 요청합니다.
    if st.session_state.timer_running:
        now = datetime.now()
        # 경과 시간 계산 및 저장
        delta = now - st.session_state.last_time_check
        st.session_state.seconds_elapsed += delta.total_seconds()
        st.session_state.last_time_check = now
        
        # 1초마다 업데이트를 위해 지연 후 rerun 호출
        time.sleep(1) 
        st.rerun() # ★★★ 수정된 함수 st.rerun() 사용 ★★★


def shuffle_click(initial_run=False):
    try:
        prob = float(st.session_state.get('difficulty_prob_input', st.session_state.difficulty_prob))
        st.session_state.difficulty_prob = max(0.0, min(1.0, prob))
    except ValueError:
        st.session_state.difficulty_prob = 0.7
    
    AVal = st.session_state.initial_solution
    random19 = list(range(1, 10))
    random.shuffle(random19)
    
    correct_board = [[str(random19[int(AVal[i][j]) - 1]) for j in range(9)] for i in range(9)]
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
            
            color = 'black' if (i, j) in initial_cells else 'red'
            st.session_state.cell_colors[(i, j)] = color

    st.session_state.correct_board = correct_board
    st.session_state.board = new_board
    st.session_state.initial_cells = initial_cells
    
    # 타이머 초기화 및 시작
    st.session_state.seconds_elapsed = 0
    st.session_state.last_time_check = datetime.now()
    st.session_state.timer_running = True
    st.session_state.result_message = "빈 칸에 1~9 사이의 숫자를 입력하세요."
    st.session_state.time_finished_display = "00:00"
    st.rerun()

def update_cell_value(r, c):
    new_val = st.session_state[f"cell_{r}_{c}"].strip()
    
    if new_val.isdigit() and 1 <= int(new_val) <= 9:
        st.session_state.board[r][c] = new_val
        st.session_state.cell_colors[(r, c)] = 'red'
    elif new_val == "":
        st.session_state.board[r][c] = ""
        st.session_state.cell_colors[(r, c)] = 'red'
    else:
        st.session_state[f"cell_{r}_{c}"] = st.session_state.board[r][c]
        
def complete_test_click():
    st.session_state.timer_running = False

    total_seconds = int(st.session_state.seconds_elapsed)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    current_time_display = f"{minutes:02d}:{seconds:02d}"
    st.session_state.time_finished_display = current_time_display

    is_correct = True
    for i in range(9):
        for j in range(9):
            current_val = st.session_state.board[i][j]
            correct_val = st.session_state.correct_board[i][j]
            
            st.session_state.cell_colors[(i, j)] = 'black' if current_val == correct_val else 'red'

            if current_val != correct_val:
                is_correct = False
    
    for r, c in st.session_state.initial_cells:
        st.session_state.cell_colors[(r, c)] = 'black'

    if is_correct:
        st.session_state.result_message = f"정답입니다! 퍼즐을 풀었습니다. 소요 시간: {current_time_display}"
        st.balloons()
    else:
        st.session_state.result_message = "아쉽지만, 정답이 아닙니다. 빨간색으로 표시된 부분을 확인하세요."
        
    st.rerun()

# --- 메인 UI 구성 ---

def main_app():
    # initialize_session_state 함수에서 이미 st.rerun()을 호출하여 타이머를 업데이트합니다.
    initialize_session_state()
    st.markdown(CELL_STYLE, unsafe_allow_html=True)
    
    st.title("Streamlit Sudoku")
    
    # --- 컨트롤 패널 ---
    col_shuffle, col_prob_label, col_prob_edit, col_timer, col_finish = st.columns([1.5, 0.8, 1, 1.5, 1.5])
    
    if col_shuffle.button("Shuffle", key="ShuffleButton", use_container_width=True):
        shuffle_click()
    
    col_prob_label.markdown("<div style='text-align: right; margin-top: 10px; font-size: 13px;'>빈칸 확률 (0~1):</div>", unsafe_allow_html=True)
    col_prob_edit.text_input("난이도 확률", 
                             value=f"{st.session_state.difficulty_prob:.2f}", 
                             key='difficulty_prob_input', 
                             label_visibility="collapsed")
    
    # 타이머 표시 로직
    if st.session_state.timer_running:
        total_seconds = int(st.session_state.seconds_elapsed)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_display = f"{minutes:02d}:{seconds:02d}"
    else:
        time_display = st.session_state.time_finished_display
        
    col_timer.markdown(f"<div class='timer-display'>{time_display}</div>", unsafe_allow_html=True)

    if col_finish.button("Finish", key="FinishButton", use_container_width=True):
        complete_test_click()

    # --- 결과 메시지 ---
    st.markdown("---")
    
    # PyQt5의 textEdit (안내 메시지)와 resEdit (결과 메시지) 통합
    st.markdown(f"<div class='info-message'>{st.session_state.result_message}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- 스도쿠 보드 UI (HTML 테이블 렌더링) ---
    
    # 1. 81개의 Streamlit text_input 위젯을 숨겨진 상태로 생성
    st.markdown('<div style="display:none">', unsafe_allow_html=True) 
    for i in range(9):
        for j in range(9):
            cell_key = f"cell_{i}_{j}"
            st.text_input(" ", 
                          value=st.session_state.board[i][j], 
                          max_chars=1, 
                          key=cell_key, 
                          on_change=update_cell_value, 
                          args=(i, j),
                          label_visibility="collapsed",
                          placeholder=" ")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. HTML 테이블 구조 생성
    html_table = '<div class="sudoku-container"><table class="sudoku-table">'
    
    for i in range(9):
        html_table += '<tr>'
        for j in range(9):
            is_initial_cell = (i, j) in st.session_state.initial_cells
            cell_color = st.session_state.cell_colors.get((i, j), 'red')
            cell_key = f"cell_{i}_{j}"
            
            html_table += '<td>'
            
            if is_initial_cell:
                # 고정된 셀: HTML div로 값 표시
                current_val = st.session_state.board[i][j]
                html_table += f'<div class="fixed-cell">{current_val}</div>'
            else:
                # 입력 가능한 셀: CSS를 이용해 Streamlit input 위젯을 원하는 위치에 표시
                
                # 위젯의 텍스트 색상을 동적으로 변경하기 위한 CSS 삽입
                html_table += f"""
                <style>
                div[data-testid*="stTextInput"] input[key="{cell_key}"] {{
                    color: {cell_color} !important;
                }}
                </style>
                <div data-st-component="{cell_key}" style="width: 100%; height: 100%;">
                    </div>
                """
                
            html_table += '</td>'
        html_table += '</tr>'
    
    html_table += '</table></div>'
    
    # 3. HTML 테이블을 마크다운으로 최종 렌더링합니다.
    st.markdown(html_table, unsafe_allow_html=True)

if __name__ == "__main__":
    main_app()

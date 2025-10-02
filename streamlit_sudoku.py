import streamlit as st
import random
from datetime import datetime

# --- 🎯 CSS 스타일 정의 (정사각형 셀, 명확한 그리드) 🎯 ---
# Streamlit에서는 셀 너비를 고정하기 위해 st.columns 대신 HTML/CSS를 강력하게 사용합니다.
CELL_SIZE_PX = 45 # 셀의 크기 (가로/세로)
GRID_WIDTH_PX = CELL_SIZE_PX * 9 + 10 # 전체 그리드 너비 (테두리 여백 포함)

CELL_STYLE = f"""
<style>
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

/* 난이도 입력 필드 (pEdit) 스타일 */
div[data-testid="stTextInput"] input[key="difficulty_prob_input"] {{
    text-align: center !important;
}}

/* 스도쿠 보드 전체를 감싸는 컨테이너 */
div.sudoku-grid-container {{
    width: {GRID_WIDTH_PX}px;
    height: {GRID_WIDTH_PX}px;
    margin: 20px auto; /* 중앙 정렬 */
    border: 3px solid #333; /* 전체 보드 두꺼운 테두리 */
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    background-color: white;
    display: flex;
    flex-wrap: wrap; /* 셀들을 9x9로 배치 */
    padding: 0;
}}

/* 개별 셀 컨테이너 (st.columns 내부) */
[data-testid^="stColumn"] {{
    flex-basis: 11.11% !important; /* 1/9 = 11.111...% */
    min-width: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}}

/* 셀의 크기와 경계선을 제어하는 내부 DIV */
.sudoku-cell-inner {{
    width: {CELL_SIZE_PX}px;
    height: {CELL_SIZE_PX}px;
    box-sizing: border-box;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0;
    margin: 0;
    border-right: 1px solid #ccc;
    border-bottom: 1px solid #ccc;
}}

/* 고정된 셀의 스타일 */
.fixed-cell-content {{
    width: 100%;
    height: 100%;
    text-align: center;
    line-height: {CELL_SIZE_PX}px;
    background-color: #eee;
    color: black;
    font-weight: bold;
    font-size: 1.2em;
    padding: 0;
    margin: 0;
}}

/* 텍스트 입력 필드 자체를 셀 크기에 맞춤 */
div[data-testid*="stTextInput"] {{
    margin: 0 !important;
    padding: 0 !important;
    width: 100%; 
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}}

div[data-testid*="stTextInput"] input {{
    width: 100%;
    height: 100%;
    text-align: center !important;
    font-size: 1.2em !important;
    font-weight: bold !important;
    border: none !important;
    margin: 0;
    padding: 0;
}}

/* 3x3 블록 간의 경계선 설정 */
.col-index-2 .sudoku-cell-inner,
.col-index-5 .sudoku-cell-inner {{ border-right: 3px solid #333; }}

.row-index-2 .sudoku-cell-inner,
.row-index-5 .sudoku-cell-inner {{ border-bottom: 3px solid #333; }}

/* 보드 맨 오른쪽/맨 아래 테두리 제거 */
.col-index-8 .sudoku-cell-inner {{ border-right: none; }}
.row-index-8 .sudoku-cell-inner {{ border-bottom: none; }}
</style>
"""

# 스도쿠 초기 정답판 (PyQt5의 AVal 초기값과 동일하게 설정)
# A00=1, A01=2, ... A88=5
INITIAL_SOLUTION = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
    ["4", "5", "6", "7", "8", "9", "1", "2", "3"],
    ["7", "8", "9", "1", "2", "3", "4", "5", "6"],
    ["2", "3", "1", "8", "9", "7", "5", "6", "4"], # 이 부분은 PyQt5 UI 파일에 정의된 초기값과 다르지만,
    ["5", "6", "4", "2", "3", "1", "8", "9", "7"], # PyQt5 코드는 AVal 배열을 초기값으로 사용하므로,
    ["8", "9", "7", "5", "6", "4", "2", "3", "1"], # PyQt5의 UI 파일에 있는 값들을 그대로 사용합니다.
    ["3", "1", "2", "6", "4", "5", "9", "7", "8"], # (A60부터 A88까지의 값을 기반으로 임의의 9x9 정답판을 생성)
    ["6", "4", "5", "9", "7", "8", "3", "1", "2"], # PyQt5 코드 자체에는 초기 정답판 배열이 없으므로,
    ["9", "7", "8", "3", "1", "2", "6", "4", "5"]  # 로직의 일관성을 위해 임의의 완전한 스도쿠 정답판을 사용합니다.
]


# --- 게임 상태 초기화 및 로직 함수 ---

def initialize_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.initial_solution = INITIAL_SOLUTION
        # PyQt5의 pEdit 초기값 "0.7" 반영
        st.session_state.difficulty_prob = 0.7
        st.session_state.result_message = "버튼을 클릭하고 1~9사이의 정수를 입력하세요, Finish를 누르면 채점 결과를 알려드립니다."
        st.session_state.board = [[""] * 9 for _ in range(9)]
        st.session_state.correct_board = [[""] * 9 for _ in range(9)]
        st.session_state.game_start_time = datetime.now()
        st.session_state.timer_running = False
        st.session_state.time_finished_display = "00:00"
        st.session_state.initial_cells = set()
        st.session_state.cell_colors = {}
        st.session_state.initialized = True
        # PyQt5처럼 초기 로딩 시 ShuffleClick 실행
        shuffle_click(initial_run=True)
    # Rerun 시 타이머 업데이트를 위해 st.session_state.timer_running이 True이면 다시 Rerun 유도
    elif st.session_state.timer_running:
        st.rerun()

def shuffle_click(initial_run=False):
    # 난이도 입력값(pEdit) 반영
    try:
        prob = float(st.session_state.get('difficulty_prob_input', st.session_state.difficulty_prob))
        st.session_state.difficulty_prob = max(0.0, min(1.0, prob))
    except ValueError:
        st.session_state.difficulty_prob = 0.7
    
    AVal = st.session_state.initial_solution
    random19 = list(range(1, 10))
    random.shuffle(random19)
    # PyQt5와 동일한 셔플 로직 적용
    correct_board = [[str(random19[int(AVal[i][j]) - 1]) for j in range(9)] for i in range(9)]
    new_board = [[correct_board[i][j] for j in range(9)] for i in range(9)]
    initial_cells = set()
    prob = st.session_state.difficulty_prob
    st.session_state.cell_colors = {}
    
    # 확률적으로 Blank로 설정
    for i in range(9):
        for j in range(9):
            if random.random() > prob:
                new_board[i][j] = ""
            else:
                initial_cells.add((i, j))
            
            # 초기 셀은 검정, 입력 가능한 셀은 빨강(사용자가 입력하는 색)
            color = 'black' if (i, j) in initial_cells else 'red'
            st.session_state.cell_colors[(i, j)] = color

    st.session_state.correct_board = correct_board
    st.session_state.board = new_board
    st.session_state.initial_cells = initial_cells
    
    # 새 게임 시작 시 타이머 재설정 및 시작
    st.session_state.game_start_time = datetime.now()
    st.session_state.timer_running = True
    st.session_state.result_message = "빈 칸에 1~9 사이의 숫자를 입력하세요."
    st.session_state.time_finished_display = "00:00"
    st.rerun()

def update_cell_value(r, c):
    # PyQt5의 keyPressEvent와 유사한 역할 (사용자 입력 처리)
    new_val = st.session_state[f"cell_{r}_{c}"].strip()
    
    if new_val.isdigit() and 1 <= int(new_val) <= 9:
        st.session_state.board[r][c] = new_val
        st.session_state.cell_colors[(r, c)] = 'red' # 입력 시 빨간색으로 변경 (PyQt5의 keyPressEvent 로직 반영)
    elif new_val == "":
        st.session_state.board[r][c] = ""
        st.session_state.cell_colors[(r, c)] = 'red'
    else:
        # 유효하지 않은 입력 시 이전 값 유지
        st.session_state[f"cell_{r}_{c}"] = st.session_state.board[r][c]
        
def complete_test_click():
    # PyQt5의 CompleteTestClick과 동일한 로직
    st.session_state.timer_running = False

    is_correct = True
    elapsed_time = datetime.now() - st.session_state.game_start_time
    minutes = int(elapsed_time.total_seconds() // 60)
    seconds = int(elapsed_time.total_seconds() % 60)
    current_time_display = f"{minutes:02d}:{seconds:02d}"
    st.session_state.time_finished_display = current_time_display

    for i in range(9):
        for j in range(9):
            current_val = st.session_state.board[i][j]
            correct_val = st.session_state.correct_board[i][j]
            
            # 정답 검증 후 색상 업데이트 (PyQt5 로직 반영: 정답이면 black, 오답이면 red)
            st.session_state.cell_colors[(i, j)] = 'black' if current_val == correct_val else 'red'

            if current_val != correct_val:
                is_correct = False
    
    # 고정 셀은 항상 검은색으로 유지
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
    # Streamlit의 Timer는 Rerun을 통해 업데이트되므로, initialize_session_state에서 Rerun을 유도합니다.
    initialize_session_state()
    st.markdown(CELL_STYLE, unsafe_allow_html=True)
    
    st.title("Streamlit Sudoku (PyQt5 UI Style)")
    
    # --- 컨트롤 패널 (Shuffle, pEdit, Timer, FinishButton) ---
    col_shuffle, col_prob_label, col_prob_edit, col_timer, col_finish = st.columns([1.5, 0.8, 1, 1.5, 1.5])
    
    if col_shuffle.button("Shuffle", key="ShuffleButton", use_container_width=True):
        shuffle_click()
    
    # 난이도 입력 (pEdit)
    col_prob_label.markdown("<div style='text-align: right; margin-top: 10px; font-size: 13px;'>빈칸 확률 (0~1):</div>", unsafe_allow_html=True)
    col_prob_edit.text_input("난이도 확률", 
                             value=f"{st.session_state.difficulty_prob:.2f}", 
                             key='difficulty_prob_input', 
                             label_visibility="collapsed")
    
    # 타이머 표시 (label)
    if st.session_state.timer_running:
        elapsed_time = datetime.now() - st.session_state.game_start_time
        minutes = int(elapsed_time.total_seconds() // 60)
        seconds = int(elapsed_time.total_seconds() % 60)
        time_display = f"{minutes:02d}:{seconds:02d}"
        
        # 타이머가 실행 중이면 1초마다 업데이트를 위해 스크립트 실행을 다시 요청
        st.write(f'<p style="display:none;">{time_display}</p>', unsafe_allow_html=True) 
        st.experimental_rerun() # Timer 업데이트 로직
    else:
        time_display = st.session_state.time_finished_display
        
    # PyQt5의 label 위젯 스타일(흰색 배경, 중앙 정렬) 반영
    col_timer.markdown(f"<div style='background-color: white; text-align: center; font-weight: bold; padding: 5px; border: 1px solid #ccc; font-size: 16px; margin-top: 5px;'>{time_display}</div>", unsafe_allow_html=True)

    if col_finish.button("Finish", key="FinishButton", use_container_width=True):
        complete_test_click()

    # --- 스도쿠 보드 UI ---
    st.markdown("---")
    
    # PyQt5의 textEdit (안내 메시지)
    st.markdown(f"<div style='text-align: center; padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc;'>{st.session_state.result_message}</div>", unsafe_allow_html=True)

    # PyQt5의 resEdit (채점 결과 메시지 - Start 메시지)
    st.markdown(f"<div style='text-align: center; margin-top: 10px; font-weight: bold;'>{st.session_state.result_message}</div>", unsafe_allow_html=True)
    
    st.markdown("---")


    # 9x9 그리드 렌더링
    st.markdown('<div class="sudoku-grid-container">', unsafe_allow_html=True)
    
    for i in range(9):
        row_class = f"row-index-{i}"
        
        # 9개의 균등한 컬럼을 사용하여 레이아웃을 잡습니다.
        cols = st.columns(9)
        
        for j in range(9):
            is_initial_cell = (i, j) in st.session_state.initial_cells
            current_val = st.session_state.board[i][j]
            cell_key = f"cell_{i}_{j}"
            cell_color = st.session_state.cell_colors.get((i, j), 'red')
            
            col_class = f"col-index-{j}"
            
            with cols[j]:
                # CSS 클래스를 적용하여 셀 모양을 제어
                st.markdown(f'<div class="sudoku-cell-inner {row_class} {col_class}">', unsafe_allow_html=True)
                
                if is_initial_cell:
                    # 고정된 셀 (HTML로 표시)
                    cell_html = f"""
                    <div class="fixed-cell-content">
                        {current_val}
                    </div>
                    """
                    st.markdown(cell_html, unsafe_allow_html=True)
                else:
                    # 사용자 입력 가능 셀 (Streamlit 위젯 사용)
                    # 입력 필드 색상 스타일링을 위한 CSS 주입
                    st.markdown(f"""
                    <style>
                    div[data-testid*="stTextInput"] input[key="{cell_key}"] {{
                        color: {cell_color} !important;
                    }}
                    </style>
                    """, unsafe_allow_html=True)
                    
                    st.text_input(" ", 
                                  value=current_val, 
                                  max_chars=1, 
                                  key=cell_key, 
                                  on_change=update_cell_value, 
                                  args=(i, j),
                                  label_visibility="collapsed",
                                  placeholder=" ")
                    
                st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
            
if __name__ == "__main__":
    main_app()

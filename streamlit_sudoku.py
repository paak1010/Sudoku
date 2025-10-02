import streamlit as st
import random
from datetime import datetime

# --- 🎯 CSS 스타일 정의 (9x9 그리드 강제 적용 및 보정) 🎯 ---
CELL_STYLE = """
<style>
/* 🏆 버튼 스타일은 그대로 유지 🏆 */
.stButton > button {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 15px;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 8px;
    transition: background-color 0.3s;
}

.stButton > button:hover {
    background-color: #45a049;
}

/* 9x9 스도쿠 보드 컨테이너 스타일 */
div.sudoku-grid-container {
    width: 100%;
    max-width: 540px; /* 9개의 셀을 50px로 잡고 테두리 여유를 둔 크기 */
    margin: 20px auto; /* 중앙 정렬 */
    border: 3px solid #333; /* 전체 보드 두꺼운 테두리 */
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    background-color: white;
    display: flex; /* 자식 요소들을 유연하게 배치 */
    flex-direction: column;
}

/* Streamlit 컬럼 컨테이너 (한 줄) 스타일 */
[data-testid="stHorizontalBlock"] {
    padding: 0;
    margin: 0;
    width: 100%;
}

/* 개별 Streamlit 컬럼 (개별 셀 컨테이너)에 9등분 너비 강제 적용 */
[data-testid^="stColumn"] {
    flex-basis: 11.11% !important; /* 1/9 = 11.111...% */
    min-width: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* 스도쿠 셀의 텍스트 입력 필드 스타일 조정 */
div[data-testid*="stTextInput"] {
    margin: 0 !important;
    padding: 0 !important;
    height: 100%;
}

div[data-testid*="stTextInput"] input {
    height: 100%;
    width: 100%;
    text-align: center !important;
    font-size: 1.5em !important;
    font-weight: bold !important;
    margin: 0;
    padding: 0;
    border-radius: 0;
    border: none !important;
}

/* 고정된 셀과 입력 셀의 공통 스타일 */
.sudoku-cell, .fixed-cell {
    width: 100%;
    height: 60px; /* 셀 높이 고정 (가로/세로 비율에 맞게 조정 가능) */
    box-sizing: border-box;
    text-align: center;
    line-height: 60px; /* 텍스트 중앙 정렬 */
    padding: 0;
    margin: 0;
}

/* 고정된 셀의 스타일 */
.fixed-cell {
    background-color: #eee; /* 고정된 셀 배경색 */
    color: black;
    font-weight: bold;
    font-size: 1.5em;
}

/* 3x3 블록 간의 경계선 설정 */
/* 모든 셀에 기본 얇은 오른쪽/아래쪽 경계선 적용 */
.sudoku-cell {
    border-right: 1px solid #ccc;
    border-bottom: 1px solid #ccc;
}

/* 3, 6 번째 열에 두꺼운 오른쪽 경계선 */
.col-index-2 .sudoku-cell,
.col-index-5 .sudoku-cell {
    border-right: 3px solid #333;
}

/* 2, 5 번째 행에 두꺼운 아래쪽 경계선 */
.row-index-2 .sudoku-cell,
.row-index-5 .sudoku-cell {
    border-bottom: 3px solid #333;
}

/* 보드 맨 오른쪽/맨 아래 테두리 제거 (전체 보드 테두리가 대신함) */
.col-index-8 .sudoku-cell { border-right: none; }
.row-index-8 .sudoku-cell { border-bottom: none; }

</style>
"""

# 스도쿠 초기 정답판 (변경 없음)
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

# --- 게임 상태 초기화 및 로직 함수 (변경 없음) ---

def initialize_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.initial_solution = INITIAL_SOLUTION
        st.session_state.difficulty_prob = 0.7
        st.session_state.result_message = "Shuffle 버튼을 눌러 게임을 시작하세요"
        st.session_state.board = [[""] * 9 for _ in range(9)]
        st.session_state.correct_board = [[""] * 9 for _ in range(9)]
        st.session_state.game_start_time = datetime.now()
        st.session_state.timer_running = False
        st.session_state.time_finished_display = "00:00"
        st.session_state.initial_cells = set()
        st.session_state.cell_colors = {}
        st.session_state.initialized = True
        shuffle_click(initial_run=True)

def shuffle_click(initial_run=False):
    if not initial_run:
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
    st.session_state.game_start_time = datetime.now()
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
            
            st.session_state.cell_colors[(i, j)] = 'black' if current_val == correct_val else 'red'

            if current_val != correct_val:
                is_correct = False
    
    # 고정 셀은 다시 검은색으로 강제 설정 (원래 상태 유지)
    for r, c in st.session_state.initial_cells:
        st.session_state.cell_colors[(r, c)] = 'black'

    if is_correct:
        st.session_state.result_message = f"정답입니다! 퍼즐을 풀었습니다. 소요 시간: {current_time_display}"
        st.balloons()
    else:
        st.session_state.result_message = "아쉽지만, 정답이 아닙니다. 빨간색 칸을 확인하세요."
        
    st.rerun()

# --- 메인 UI 구성 ---

def main_app():
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
    
    # 타이머 표시
    if st.session_state.timer_running:
        elapsed_time = datetime.now() - st.session_state.game_start_time
        minutes = int(elapsed_time.total_seconds() // 60)
        seconds = int(elapsed_time.total_seconds() % 60)
        time_display = f"{minutes:02d}:{seconds:02d}"
    else:
        time_display = st.session_state.time_finished_display
        
    col_timer.markdown(f"<div style='background-color: white; text-align: center; font-weight: bold; padding: 5px; border: 1px solid #ccc; font-size: 16px; margin-top: 5px;'>⏱️ {time_display}</div>", unsafe_allow_html=True)

    if col_finish.button("Finish", key="FinishButton", use_container_width=True):
        complete_test_click()

    # --- 결과 메시지 ---
    st.markdown("---")
    st.info(st.session_state.result_message)
    st.markdown("---")

    # --- 스도쿠 보드 UI (9x9 그리드 명확화) ---
    st.markdown('<div class="sudoku-grid-container">', unsafe_allow_html=True)
    
    for i in range(9):
        row_class = f"row-index-{i}"
        
        # Streamlit 컬럼을 명확하게 9개 만듭니다.
        cols = st.columns(9)
        
        for j in range(9):
            is_initial_cell = (i, j) in st.session_state.initial_cells
            current_val = st.session_state.board[i][j]
            cell_key = f"cell_{i}_{j}"
            cell_color = st.session_state.cell_colors.get((i, j), 'red')
            
            col_class = f"col-index-{j}"
            
            with cols[j]:
                # CSS 클래스를 적용하여 셀 모양을 제어
                st.markdown(f'<div class="sudoku-cell {row_class} {col_class}">', unsafe_allow_html=True)
                
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
                    st.markdown(f"""
                    <style>
                    /* 특정 입력 필드의 텍스트 색상 설정 */
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

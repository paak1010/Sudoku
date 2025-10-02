import streamlit as st
import random
from datetime import datetime

# --- 🎯 CSS 스타일 정의 (정사각형 셀, 명확한 그리드) 🎯 ---
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

/* 개별 셀 컨테이너 (st.markdown으로 생성되는 div) */
.sudoku-cell-container {{
    width: {CELL_SIZE_PX}px;
    height: {CELL_SIZE_PX}px;
    box-sizing: border-box;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0;
    margin: 0;
}}

/* 고정된 셀의 스타일 */
.fixed-cell-content {{
    width: 100%;
    height: 100%;
    text-align: center;
    line-height: {CELL_SIZE_PX}px;
    background-color: #eee; /* 고정된 셀 배경색 */
    color: black;
    font-weight: bold;
    font-size: 1.2em;
    padding: 0;
    margin: 0;
}}

/* 텍스트 입력 필드 자체를 정사각형 셀 크기에 맞춤 */
div[data-testid*="stTextInput"] {{
    margin: 0 !important;
    padding: 0 !important;
    width: {CELL_SIZE_PX}px; 
    height: {CELL_SIZE_PX}px;
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
    border: none !important; /* 기본 Streamlit 테두리 제거 */
    margin: 0;
    padding: 0;
}}

/* 3x3 블록 간의 경계선 설정 */
.sudoku-cell-container {{
    border-right: 1px solid #ccc;
    border-bottom: 1px solid #ccc;
}}

/* 3, 6 번째 열에 두꺼운 오른쪽 경계선 */
/* (index 2, 5, 8은 0부터 시작하는 인덱스입니다) */
.col-index-2 {{ border-right: 3px solid #333; }}
.col-index-5 {{ border-right: 3px solid #333; }}
.col-index-8 {{ border-right: none; }} /* 가장 오른쪽 테두리는 전체 그리드 테두리가 대신함 */

/* 3, 6 번째 행에 두꺼운 아래쪽 경계선 */
.row-index-2 .sudoku-cell-container,
.row-index-5 .sudoku-cell-container {{ border-bottom: 3px solid #333; }}
.row-index-8 .sudoku-cell-container {{ border-bottom: none; }}
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
        # 유효하지 않은 입력 시 이전 값 유지
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
            
            # 정답 검증 후 색상 업데이트
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

    # --- 스도쿠 보드 UI (단일 마크다운 블록으로 9x9 렌더링) ---
    st.markdown('<div class="sudoku-grid-container">', unsafe_allow_html=True)
    
    # st.columns 대신 단일 블록 안에 모든 셀을 순서대로 배치
    cols_placeholder = st.empty()
    
    all_cells_html = ""
    for i in range(9):
        for j in range(9):
            is_initial_cell = (i, j) in st.session_state.initial_cells
            current_val = st.session_state.board[i][j]
            cell_key = f"cell_{i}_{j}"
            cell_color = st.session_state.cell_colors.get((i, j), 'red')
            
            row_class = f"row-index-{i}"
            col_class = f"col-index-{j}"
            
            cell_container_start = f'<div class="sudoku-cell-container {row_class} {col_class}">'
            cell_container_end = '</div>'
            
            if is_initial_cell:
                # 고정된 셀 (HTML로 표시)
                cell_content = f"""
                <div class="fixed-cell-content">
                    {current_val}
                </div>
                """
                all_cells_html += cell_container_start + cell_content + cell_container_end
            else:
                # 사용자 입력 가능 셀 (Streamlit 위젯 사용)
                # st.columns를 사용하지 않으므로, 셀을 순서대로 생성해야 합니다.
                
                # 입력 필드 색상 스타일링을 위한 CSS 주입 (Streamlit 버그 우회)
                color_style = f"""
                <style>
                div[data-testid*="stTextInput"] input[key="{cell_key}"] {{
                    color: {cell_color} !important;
                }}
                </style>
                """
                st.markdown(color_style, unsafe_allow_html=True)
                
                # 위젯을 st.columns 안에 넣지 않고 순서대로 생성합니다.
                # 컨테이너 없이 위젯만 생성하고, 위젯을 감싸는 div를 CSS로 제어합니다.
                st.text_input(" ", 
                              value=current_val, 
                              max_chars=1, 
                              key=cell_key, 
                              on_change=update_cell_value, 
                              args=(i, j),
                              label_visibility="collapsed",
                              placeholder=" ")
    
    # 이 부분은 st.columns를 사용하지 않으므로 삭제
    # st.markdown(all_cells_html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
            
if __name__ == "__main__":
    main_app()

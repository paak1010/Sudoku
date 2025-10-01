import streamlit as st
import random
from datetime import datetime

# --- CSS 스타일 정의 (셀 크기 통일 및 3x3 경계 추가) ---
CELL_STYLE = """
<style>
/* Streamlit 앱의 전체 배경색 설정 (선택 사항) */
/* .stApp { background-color: #f0f2f6; } */

/* 모든 텍스트 입력 필드의 컨테이너 마진 조정 */
div[data-testid="stTextInput"] {
    margin: -10px 0 !important; /* 행 간격 줄이기 */
    padding: 0 !important;
}

/* 🏆 모든 Streamlit 버튼 디자인 통일 🏆 */
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

/* Streamlit에서 생성되는 경고 메시지 스타일 */
.stAlert {
    margin-top: 10px;
    margin-bottom: 0;
    padding: 10px;
}

/* ⚠️ 모든 셀 (고정 셀, 입력 셀)의 기본 스타일 ⚠️ */
.sudoku-cell {
    width: 100%; 
    height: 35px; /* 모든 셀의 높이 통일 */
    box-sizing: border-box; /* 패딩과 경계선을 너비/높이에 포함 */
    text-align: center; 
    line-height: 35px; /* 텍스트 수직 중앙 정렬 */
    font-family: 'Arial', sans-serif; /* 폰트 통일 */
    font-weight: bold; /* 굵게 */
    font-size: 1.2em; /* 폰트 크기 통일 */
    border: 1px solid #ddd; /* 얇은 기본 경계선 */
}

/* 🔒 고정된 셀의 배경색 */
.fixed-cell {
    background-color: #e6e6e6; 
    color: #333; /* 고정 셀의 색상 */
}

/* ✏️ 입력 필드 자체의 스타일 오버라이드 */
div[data-testid="stTextInput"] input {
    text-align: center !important;
    font-weight: bold !important;
    font-size: 1.2em !important;
    font-family: 'Arial', sans-serif !important; 
    width: 100% !important; 
    height: 35px !important; 
    padding: 0 !important; /* 패딩 제거하여 크기 조절 용이 */
    margin: 0 !important; /* 마진 제거하여 크기 조절 용이 */
    border-radius: 0 !important; /* 모서리 둥글기 제거 */
}

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
            
            # 초기 셀은 검은색, 입력 셀은 붉은색
            color = 'black' if (i, j) in initial_cells else '#C0392B' # 입력 셀 색상을 좀 더 진한 붉은색으로 변경
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
    
    # 입력 검증: 1-9 사이의 숫자 또는 빈 문자열
    if new_val.isdigit() and 1 <= int(new_val) <= 9:
        st.session_state.board[r][c] = new_val
        st.session_state.cell_colors[(r, c)] = '#C0392B' # 입력값 유지 시 붉은색
    elif new_val == "":
        st.session_state.board[r][c] = ""
        st.session_state.cell_colors[(r, c)] = '#C0392B' # 빈 칸 시 붉은색
    else:
        # 유효하지 않은 입력은 무시하고 기존 값으로 복원
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
            
            if current_val != correct_val:
                st.session_state.cell_colors[(i, j)] = '#C0392B' # 오답 셀은 붉은색
                is_correct = False
            else:
                # 정답 셀은 고정 셀과 동일한 검은색으로 표시
                st.session_state.cell_colors[(i, j)] = 'black'

    if is_correct:
        st.session_state.result_message = f"🎉 정답입니다! 퍼즐을 풀었습니다. 소요 시간: {current_time_display}"
        st.balloons()
    else:
        st.session_state.result_message = "❌ 아쉽지만, 정답이 아닙니다. 잘못된 셀이 빨간색으로 표시됩니다."
        
    st.rerun() 

# --- 메인 UI 구성 ---

def main_app():
    initialize_session_state()
    st.markdown(CELL_STYLE, unsafe_allow_html=True) 
    
    st.title("Streamlit Sudoku 🧩")
    
    # --- 컨트롤 패널 ---
    col_shuffle, col_prob_label, col_prob_edit, col_timer, col_finish = st.columns([1.5, 0.8, 1, 1.5, 1.5])
    
    if col_shuffle.button("Shuffle (New Game)", key="ShuffleButton", use_container_width=True):
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
        # 타이머가 돌아갈 때만 rerunning
        st.rerun() 
    else:
        time_display = st.session_state.time_finished_display
        
    col_timer.markdown(f"<div style='background-color: white; text-align: center; font-weight: bold; padding: 5px; border: 1px solid #ccc; font-size: 16px; margin-top: 5px;'>⏱️ {time_display}</div>", unsafe_allow_html=True)

    if col_finish.button("Check Answer", key="FinishButton", use_container_width=True):
        complete_test_click()

    # --- 결과 메시지 ---
    st.markdown("---")
    st.info(st.session_state.result_message)
    st.markdown("---")

    
    for i in range(9):
        # 9개의 균등한 컬럼을 생성합니다.
        cols = st.columns(9, gap="TINY") # gap="TINY"로 컬럼 간격 최소화
        
        # 행 간의 간격을 최소화하는 CSS 오버라이드
        # (st.columns를 사용하면 행 간격을 직접 제어하기 어려우므로, CSS로 stTextInput의 마진을 조절한 상태)
        
        for j in range(9):
            is_initial_cell = (i, j) in st.session_state.initial_cells
            current_val = st.session_state.board[i][j]
            cell_key = f"cell_{i}_{j}"
            cell_color = st.session_state.cell_colors.get((i, j), '#C0392B')
            
            # 3x3 블록 경계선 스타일을 동적으로 계산
            border_top = "1px solid #ddd"
            border_bottom = "1px solid #ddd"
            border_left = "1px solid #ddd"
            border_right = "1px solid #ddd"
            
            # 3x3 경계선 굵게
            if i % 3 == 0: # 0, 3, 6번째 행의 상단 경계선 (전체 보드의 상단 제외)
                border_top = "3px solid #333" if i != 0 else "1px solid #333"
            if i == 8: # 8번째 행의 하단 경계선
                border_bottom = "3px solid #333"
            elif (i + 1) % 3 == 0: # 2, 5, 8번째 행의 하단 경계선
                border_bottom = "3px solid #333"

            if j % 3 == 0: # 0, 3, 6번째 열의 왼쪽 경계선 (전체 보드의 왼쪽 제외)
                border_left = "3px solid #333" if j != 0 else "1px solid #333"
            if j == 8: # 8번째 열의 오른쪽 경계선
                border_right = "3px solid #333"
            elif (j + 1) % 3 == 0: # 2, 5, 8번째 열의 오른쪽 경계선
                border_right = "3px solid #333"
                
            custom_border_style = f"border-top: {border_top}; border-bottom: {border_bottom}; border-left: {border_left}; border-right: {border_right};"

            if is_initial_cell:
                # 고정된 셀 (HTML div 사용)
                cell_html = f"""
                <div class="sudoku-cell fixed-cell" style="{custom_border_style}">
                    {current_val}
                </div>
                """
                cols[j].markdown(cell_html, unsafe_allow_html=True)
            else:
                # 사용자 입력 가능 셀 (st.text_input 사용)
                # 입력 필드에 동적 스타일 적용을 위해 CSS를 인라인으로 주입
                cols[j].markdown(f"""
                <style>
                /* 입력 필드 자체에 동적 테두리 및 색상 적용 */
                div[data-testid="stTextInput"] input[key="{cell_key}"] {{
                    color: {cell_color} !important;
                    {custom_border_style}
                }}
                </style>
                """, unsafe_allow_html=True)
                
                cols[j].text_input(" ", 
                                    value=current_val, 
                                    max_chars=1, 
                                    key=cell_key, 
                                    on_change=update_cell_value, 
                                    args=(i, j),
                                    label_visibility="collapsed",
                                    placeholder=" ")
    
    st.markdown("---")
            
if __name__ == "__main__":
    main_app()

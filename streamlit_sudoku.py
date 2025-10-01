import streamlit as st
import random
from datetime import datetime

# --- CSS 스타일 정의 (셀 크기 고정 및 3x3 블록 구분선 포함) ---
CELL_STYLE = """
<style>
/* 1. Streamlit 컬럼 및 위젯 컨테이너의 기본 간격 제거 */
/* Streamlit 컬럼의 패딩/마진을 0으로 설정하여 셀들을 밀착시킵니다. */
div[data-testid^="stHorizontalBlock"] > div[data-testid^="stVerticalBlock"] > div {
    padding: 0px !important;
    margin: 0px !important;
}

/* 2. 입력 필드 컨테이너 스타일 */
div[data-testid="stTextInput"] {
    margin: 0 !important; 
    padding: 0 !important;
}

/* 3. 셀 입력 필드 자체 스타일: 크기 고정 및 중앙 정렬 */
div[data-testid="stTextInput"] > div > input {
    text-align: center !important;
    font-weight: bold;
    font-size: 1.2em !important;
    padding: 0px !important;
    height: 35px !important; 
    width: 35px !important;  /* 🎯 핵심 수정: 셀 너비 고정 */
    box-sizing: border-box;
    margin: 0;
    border: 1px solid #ccc; /* 얇은 기본 경계선 */
    border-radius: 0px;
}

/* 4. 고정된 셀 (fixed-cell) 스타일 */
.fixed-cell {
    text-align: center;
    font-weight: bold;
    font-size: 1.2em;
    height: 35px; /* 높이 고정 */
    width: 35px;  /* 🎯 핵심 수정: 셀 너비 고정 */
    line-height: 35px;
    background-color: #f0f2f6; 
    color: black;
    border: 1px solid #ccc;
    box-sizing: border-box;
    margin: 0;
    border-radius: 0px;
}

/* 🏆 모든 Streamlit 버튼 디자인 통일 🏆 */
.stButton > button {
    background-color: #4CAF50; 
    color: white;             
    border: none;             
    padding: 10px 15px;       
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;          
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 8px;       
    transition: background-color 0.3s;
}

.stButton > button:hover {
    background-color: #45a049; 
}

/* Streamlit에서 생성되는 경고 메시지 스타일 숨기기 */
.stAlert {
    margin-top: 0;
    margin-bottom: 0;
    padding: 10px;
}
</style>
"""

# --- 게임 상태 초기화 ---

def initialize_session_state():
    """세션 상태를 초기화하고 첫 게임을 시작합니다."""
    if 'initialized' not in st.session_state:
        AVal_initial = [
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
        
        st.session_state.initial_solution = AVal_initial
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


# --- 게임 로직 함수 (변경 없음) ---

def shuffle_click(initial_run=False):
    """보드를 셔플하고 새 게임을 시작합니다."""
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
    """텍스트 입력 필드가 변경될 때 호출됩니다."""
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
    """채점 로직을 실행합니다."""
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
            
            if (i, j) not in st.session_state.initial_cells:
                if current_val != correct_val:
                    st.session_state.cell_colors[(i, j)] = 'red' 
                    is_correct = False
                else:
                    st.session_state.cell_colors[(i, j)] = 'green'
            else:
                st.session_state.cell_colors[(i, j)] = 'black'

    if is_correct:
        st.session_state.result_message = f"✅ 정답입니다! 퍼즐을 풀었습니다. 소요 시간: {current_time_display}"
        st.balloons()
    else:
        st.session_state.result_message = "❌ 아쉽지만, 정답이 아닙니다. 빨간색/빈칸 부분을 확인하세요."
        
    st.rerun() 

# --- 메인 UI 구성 ---

def main_app():
    initialize_session_state()
    st.markdown(CELL_STYLE, unsafe_allow_html=True) 
    
    st.title("Streamlit Sudoku 🧩")
    
    # --- 컨트롤 패널 (Shuffle, Finish, 난이도, 타이머) ---
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


    # --- Sudoku 그리드 영역 ---
    
    for i in range(9):
        # 현재 행이 3x3 블록의 아래 경계선인지 확인 (인덱스 2와 5)
        is_thick_row = i in [2, 5]
        
        # 9개의 균등한 컬럼을 생성합니다. (CSS로 크기가 고정되므로 간격이 좁아짐)
        cols = st.columns(9)
        
        for j in range(9):
            is_initial_cell = (i, j) in st.session_state.initial_cells
            current_val = st.session_state.board[i][j]
            cell_key = f"cell_{i}_{j}"
            cell_color = st.session_state.cell_colors.get((i, j), 'red')
            
            # 🎯 3x3 블록 구분선을 계산하여 굵은 선 복원
            is_thick_col = j in [2, 5]
            
            # 경계선 스타일 정의: 3x3 구분선은 굵게, 나머지는 얇게
            border_right_style = "3px solid black" if is_thick_col else "1px solid #ccc"
            border_bottom_style = "3px solid black" if is_thick_row else "1px solid #ccc"

            if is_initial_cell:
                # 고정된 셀
                cell_html = f"""
                <div class="fixed-cell" style="border-right: {border_right_style}; border-bottom: {border_bottom_style};">
                    {current_val}
                </div>
                """
                cols[j].markdown(cell_html, unsafe_allow_html=True)
            else:
                # 사용자 입력 가능 셀
                cols[j].markdown(f"""
                <style>
                /* 특정 셀의 텍스트 색상과 보더를 지정합니다. */
                div[data-testid="stTextInput"] input[key="{cell_key}"] {{
                    color: {cell_color} !important;
                    border-right: {border_right_style} !important;
                    border-bottom: {border_bottom_style} !important;
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
            
        # ⚠️ 이전 단계에서 그리드를 망가뜨린 불필요한 마크다운 제거 (CSS로 해결됨)
        # st.markdown('<div style="height: 1px; margin-top: -15px;"></div>', unsafe_allow_html=True) 
        
    st.markdown("---")
            
if __name__ == "__main__":
    main_app()

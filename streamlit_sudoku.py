import streamlit as st
import random
from datetime import datetime

# --- CSS 스타일 정의 (CSS Grid를 모방하여 완벽한 격자 구조 구현) ---

# 셀 크기
CELL_SIZE = "35px"
THICK_BORDER = "3px solid black"
THIN_BORDER = "1px solid #ccc"

CELL_STYLE = f"""
<style>
/* 1. 스도쿠 그리드 컨테이너 스타일 (Grid 레이아웃 구현) */
.sudoku-grid {{
    display: grid;
    /* 9개의 동일한 크기(CELL_SIZE)를 가진 컬럼을 정의 */
    grid-template-columns: repeat(9, {CELL_SIZE});
    width: fit-content; /* 그리드 너비를 내용물에 맞춤 */
    margin: 20px auto; /* 중앙 정렬 */
    border-top: {THICK_BORDER}; /* 전체 보드의 위쪽 테두리 */
    border-left: {THICK_BORDER}; /* 전체 보드의 왼쪽 테두리 */
}}

/* 2. 일반적인 Streamlit 위젯 마진/패딩 초기화 */
div[data-testid="stTextInput"], 
div[data-testid="stHorizontalBlock"] > div[data-testid^="stVerticalBlock"] > div {{
    margin: 0 !important; 
    padding: 0 !important;
}}

/* 3. 셀 입력 필드 자체 스타일: 크기 고정 및 중앙 정렬 */
div[data-testid="stTextInput"] > div > input {{
    text-align: center !important;
    font-weight: bold;
    font-size: 1.2em !important;
    padding: 0 !important;
    height: {CELL_SIZE} !important; 
    width: {CELL_SIZE} !important;
    box-sizing: border-box;
    margin: 0;
    border: none; /* 개별 셀의 테두리는 부모 요소가 담당 */
    border-radius: 0;
}}

/* 4. 고정된 셀 (fixed-cell) 스타일 */
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

/* Streamlit에서 생성되는 경고 메시지 스타일 숨기기 */
.stAlert {{
    margin-top: 0;
    margin-bottom: 0;
    padding: 10px;
}}
</style>
"""

# --- 게임 상태 초기화 (변경 없음) ---

def initialize_session_state():
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


    # --- Sudoku 그리드 영역 (CSS Grid 컨테이너 사용) ---
    
    # Grid 컨테이너 시작
    st.markdown('<div class="sudoku-grid">', unsafe_allow_html=True)
    
    for i in range(9):
        # 현재 행이 3x3 블록의 아래 경계선인지 확인 (인덱스 2와 5)
        is_thick_row = i in [2, 5]
        
        for j in range(9):
            is_initial_cell = (i, j) in st.session_state.initial_cells
            current_val = st.session_state.board[i][j]
            cell_key = f"cell_{i}_{j}"
            cell_color = st.session_state.cell_colors.get((i, j), 'red')
            
            # 3x3 블록 구분선을 계산하는 코드
            is_thick_col = j in [2, 5]
            
            # 경계선 스타일 정의: 3x3 구분선은 굵게, 나머지는 얇게
            # Grid 방식에서는 오른쪽과 아래쪽 테두리만 조건부로 적용
            border_right_style = THICK_BORDER if is_thick_col else THIN_BORDER
            border_bottom_style = THICK_BORDER if is_thick_row else THIN_BORDER
            
            # 셀을 담을 Grid 아이템 컨테이너 시작 (스타일 적용)
            st.markdown(f'<div style="border-right: {border_right_style}; border-bottom: {border_bottom_style};">', unsafe_allow_html=True)
            
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
                # **주의**: st.text_input을 Grid 내부에서 직접 사용하면 레이아웃이 깨지기 쉬우므로,
                # 여기서는 st.columns 대신 Grid의 개별 아이템으로 렌더링하는 방식을 사용합니다.
                
                # 인라인 스타일 주입으로 텍스트 색상만 제어
                st.markdown(f"""
                <style>
                div[data-testid="stTextInput"] input[key="{cell_key}"] {{
                    color: {cell_color} !important;
                }}
                </style>
                """, unsafe_allow_html=True)
                
                # st.text_input 위젯 (Grid 아이템 안에 삽입)
                st.text_input(" ", 
                               value=current_val, 
                               max_chars=1, 
                               key=cell_key, 
                               on_change=update_cell_value, 
                               args=(i, j),
                               label_visibility="collapsed",
                               placeholder=" ")
            
            # 셀을 담을 Grid 아이템 컨테이너 닫기
            st.markdown('</div>', unsafe_allow_html=True)
            
    # Grid 컨테이너 닫기
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
            
if __name__ == "__main__":
    main_app()

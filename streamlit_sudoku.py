import streamlit as st
import random
from datetime import datetime
# time 모듈은 이제 강제 재실행을 위해 사용하지 않습니다.

# --- CSS 스타일 정의 ---
CELL_STYLE = """
<style>
/* 모든 텍스트 입력 필드의 컨테이너 스타일 */
div[data-testid="stTextInput"] {
    margin: -10px 0; /* st.text_input의 기본 마진을 줄여 간격 최소화 */
}

/* 셀 입력 필드 자체 스타일 */
div[data-testid="stTextInput"] > div > input {
    text-align: center !important;
    font-size: 1.2em !important;
    padding: 0px !important;
    height: 35px !important;
    width: 100% !important; /* 컬럼 너비에 꽉 채우기 */
    box-sizing: border-box;
    margin: 0;
    border: 1px solid #ccc;
    border-radius: 0px;
}

/* 고정된 셀 (fixed-cell) 스타일 */
.fixed-cell {
    text-align: center;
    font-weight: bold;
    font-size: 1.2em;
    height: 35px;
    line-height: 35px; /* 텍스트 수직 중앙 정렬 */
    background-color: #f0f2f6; /* 약간 어두운 배경 */
    color: black;
    border: 1px solid #ccc;
    box-sizing: border-box;
    margin: 0;
}

/* 스도쿠 3x3 블록 구분선 스타일 */
.col-border-right {
    border-right: 3px solid black !important;
}

.row-border-bottom {
    border-bottom: 3px solid black !important;
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
        st.session_state.active_cell = None  
        st.session_state.initialized = True
        
        shuffle_click(initial_run=True)


# --- 게임 로직 함수 ---

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
    st.session_state.result_message = "빈 칸에 1~9 사이의 숫자를 입력하거나, 아래 버튼을 클릭하세요."
    st.session_state.time_finished_display = "00:00"
    st.session_state.active_cell = None
    
    st.rerun() 

def update_cell_value(r, c):
    """텍스트 입력 필드가 변경될 때 호출됩니다. (키보드 입력 처리)"""
    new_val = st.session_state[f"cell_{r}_{c}"].strip()
    
    # 1. 현재 포커스된 셀 저장 (버튼 입력에 사용)
    # Streamlit의 on_change는 포커스를 잃을 때 발생하므로, 이 시점에 active_cell을 설정합니다.
    st.session_state.active_cell = (r, c)

    # 2. 값 유효성 검사 및 업데이트 
    if new_val.isdigit() and 1 <= int(new_val) <= 9:
        st.session_state.board[r][c] = new_val
        st.session_state.cell_colors[(r, c)] = 'red' 
    elif new_val == "":
        st.session_state.board[r][c] = ""
        st.session_state.cell_colors[(r, c)] = 'red' 
    else:
        # 잘못된 입력은 무시 (이전 값 유지)
        pass
        
def complete_test_click():
    """채점 로직을 실행합니다."""
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
            
            if (i, j) not in st.session_state.initial_cells:
                if current_val != correct_val:
                    st.session_state.cell_colors[(i, j)] = 'red' 
                    is_correct = False
                else:
                    st.session_state.cell_colors[(i, j)] = 'green' # 정답은 녹색으로 표시
            else:
                # 초기값은 검정 유지
                st.session_state.cell_colors[(i, j)] = 'black'

    # 결과 메시지 출력
    if is_correct:
        st.session_state.result_message = f"✅ 정답입니다! 퍼즐을 풀었습니다. 소요 시간: {current_time_display}"
        st.balloons()
    else:
        st.session_state.result_message = "❌ 아쉽지만, 정답이 아닙니다. 빨간색으로 표시된 부분을 확인하세요."
        
    st.rerun() 

def insert_number_click(number_str):
    """숫자 버튼 클릭 시 호출되어, 활성화된 셀에 숫자를 입력합니다."""
    if st.session_state.active_cell is None:
        st.session_state.result_message = "⚠️ 먼저 스도쿠 보드의 빈 칸을 클릭(선택)해주세요!"
        st.rerun()
        return

    r, c = st.session_state.active_cell
    
    # 초기 고정 셀이 아닌지 확인
    if (r, c) in st.session_state.initial_cells:
        st.session_state.result_message = "❌ 이 셀은 초기 고정된 셀이라 수정할 수 없습니다."
        st.rerun()
        return

    # 숫자 삽입 또는 지우기
    if number_str == "DEL":
        st.session_state.board[r][c] = ""
    else:
        st.session_state.board[r][c] = number_str

    # 텍스트 입력 필드의 값을 수동으로 업데이트합니다.
    st.session_state[f"cell_{r}_{c}"] = st.session_state.board[r][c]
    
    # 색상 업데이트 (사용자 입력이므로 빨간색)
    st.session_state.cell_colors[(r, c)] = 'red'

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
    
    # **🔥 타이머 로직 수정 (에러 해결 핵심 부분) 🔥**
    if st.session_state.timer_running:
        elapsed_time = datetime.now() - st.session_state.game_start_time
        minutes = int(elapsed_time.total_seconds() // 60)
        seconds = int(elapsed_time.total_seconds() % 60)
        time_display = f"{minutes:02d}:{seconds:02d}"
        
        # ⚠️ 무한 루프를 유발하는 time.sleep()과 st.rerun()을 제거했습니다.
        # 이제 시간은 Streamlit의 일반적인 동작(위젯 상호작용)에 따라 갱신됩니다.
        
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
        # 3x3 블록 구분을 위한 컬럼 설정
        cols_config = [1] * 3 + [0.05] + [1] * 3 + [0.05] + [1] * 3
        cols = st.columns(cols_config)
        
        col_index = 0
        
        for j in range(9):
            is_initial_cell = (i, j) in st.session_state.initial_cells
            current_val = st.session_state.board[i][j]
            cell_key = f"cell_{i}_{j}"
            cell_color = st.session_state.cell_colors.get((i, j), 'red')
            
            # 3열과 6열 다음 경계선 컬럼을 건너뜁니다.
            if j in [3, 6]:
                col_index += 1
            
            # 셀 스타일 및 위젯/마크다운 렌더링
            border_right_style = "3px solid black" if j in [2, 5] else "1px solid #ccc"
            border_bottom_style = "3px solid black" if i in [2, 5] else "1px solid #ccc"

            if is_initial_cell:
                # 고정된 셀 (fixed-cell 클래스 스타일 사용)
                cell_html = f"""
                <div class="fixed-cell" style="border-right: {border_right_style}; border-bottom: {border_bottom_style};">
                    {current_val}
                </div>
                """
                cols[col_index].markdown(cell_html, unsafe_allow_html=True)
            else:
                # 사용자 입력 가능 셀 (Streamlit text_input 사용)
                # Streamlit 위젯의 스타일을 오버라이드합니다.
                cols[col_index].markdown(f"""
                <style>
                div[data-testid="stTextInput"] input[key="{cell_key}"] {{
                    color: {cell_color} !important;
                    border-right: {border_right_style} !important;
                    border-bottom: {border_bottom_style} !important;
                }}
                </style>
                """, unsafe_allow_html=True)
                
                cols[col_index].text_input(" ", 
                                           value=current_val, 
                                           max_chars=1, 
                                           key=cell_key, 
                                           on_change=update_cell_value, 
                                           args=(i, j), # on_change 시 셀 정보를 저장합니다.
                                           label_visibility="collapsed",
                                           placeholder=" ")
                
            col_index += 1
            
    st.markdown("---")

    # --- 숫자 버튼 영역 (키패드) ---
    st.subheader("숫자 입력 패드")
    
    # 9개의 버튼과 1개의 지우기 버튼을 위한 컬럼 설정
    num_cols = st.columns([1] * 9 + [1.5]) 

    # 1부터 9까지의 버튼 생성
    for k in range(1, 10):
        number_str = str(k)
        if num_cols[k-1].button(number_str, key=f"num_btn_{k}", use_container_width=True):
            insert_number_click(number_str)

    # 지우기 버튼 (DEL)
    if num_cols[9].button("❌ 지우기", key="del_btn", use_container_width=True):
        insert_number_click("DEL")
            
if __name__ == "__main__":
    main_app()

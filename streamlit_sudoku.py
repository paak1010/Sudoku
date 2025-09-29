import streamlit as st
import random
from datetime import datetime

# --- 설정 및 초기화 ---

# 스도쿠 보드의 기본 스타일 설정 (셀과 텍스트 입력의 모양을 제어)
CELL_STYLE = """
<style>
/* Streamlit 기본 입력 필드 여백 제거 */
div[data-testid="stTextInput"] {
    margin: 0px;
    padding: 0px;
}
/* 입력 필드 자체 스타일링 */
input[type="text"] {
    text-align: center;
    font-size: 20px;
    font-weight: bold;
    height: 45px;
    padding: 0;
    margin: 0;
    border: 1px solid #ccc;
}
/* 고정된 초기값 셀 스타일 */
.fixed-cell {
    background-color: #f0f2f6;
    text-align: center;
    font-weight: bold;
    font-size: 20px;
    height: 45px;
    line-height: 45px; /* 텍스트 수직 중앙 정렬 */
    border: 1px solid #ccc;
}
</style>
"""

# Streamlit 앱의 세션 상태(Session State)를 초기화합니다.
def initialize_session_state():
    if 'initialized' not in st.session_state:
        # Sudoku.ui에서 가져온 초기 보드 구조를 기반으로 한 9x9 배열 (정답 기반)
        # 이 초기값은 실제 스도쿠 규칙에 맞는 완성된 판이라고 가정합니다.
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
        st.session_state.cell_colors = {} # { (i, j): 'red' }
        st.session_state.initialized = True
        
        # 초기화 후 바로 Shuffle 실행
        shuffle_click(initial_run=True)


# --- 게임 로직 함수 ---

def shuffle_click(initial_run=False):
    """보드를 셔플하고 새 게임을 시작합니다. (PyQt의 ShuffleClick 역할)"""
    if not initial_run:
        try:
            prob = float(st.session_state.get('difficulty_prob_input', st.session_state.difficulty_prob))
            st.session_state.difficulty_prob = max(0.0, min(1.0, prob)) 
        except ValueError:
            st.session_state.difficulty_prob = 0.7 
    
    AVal = st.session_state.initial_solution
    
    # 1. 1~9 숫자 셔플
    random19 = list(range(1, 10))
    random.shuffle(random19)
    
    # 2. 정답 보드 생성 (셔플된 값 적용)
    correct_board = [[str(random19[int(AVal[i][j]) - 1]) for j in range(9)] for i in range(9)]
    
    # 3. 사용자 보드 생성 (Blank 적용 및 초기 고정 셀 위치 저장)
    new_board = [[correct_board[i][j] for j in range(9)] for i in range(9)]
    initial_cells = set()
    prob = st.session_state.difficulty_prob
    
    for i in range(9):
        for j in range(9):
            if random.random() > prob:
                new_board[i][j] = ""
            else:
                initial_cells.add((i, j))
            st.session_state.cell_colors[(i, j)] = 'black' # 모든 셀의 색상 초기화

    # 4. 세션 상태 업데이트
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
    
    # 1~9 사이의 숫자만 허용하고, 그 외는 빈 값으로 처리
    if new_val.isdigit() and 1 <= int(new_val) <= 9:
        st.session_state.board[r][c] = new_val
        st.session_state.cell_colors[(r, c)] = 'red' # 사용자 입력은 빨간색으로 표시
    elif new_val == "":
        st.session_state.board[r][c] = ""
        st.session_state.cell_colors[(r, c)] = 'red' 
    else:
        # 잘못된 입력은 무시하고 이전 값으로 롤백하여 UI에 표시
        st.session_state[f"cell_{r}_{c}"] = st.session_state.board[r][c] 
    
    # 이 함수가 실행된 후 Streamlit은 자동으로 새로고침됩니다.
    
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
            
            # 정답과 다르거나 비어있는 경우 (초기 고정 셀 제외)
            if current_val != correct_val:
                st.session_state.cell_colors[(i, j)] = 'red' # 틀린 부분은 빨간색
                is_correct = False
            else:
                st.session_state.cell_colors[(i, j)] = 'black' # 정답은 검정색 (초기값과 동일)

    # 결과 메시지 출력
    if is_correct:
        st.session_state.result_message = f"✅ 정답입니다! 퍼즐을 풀었습니다. 소요 시간: {current_time_display}"
        st.balloons()
    else:
        st.session_state.result_message = "❌ 아쉽지만, 정답이 아닙니다. 빨간색으로 표시된 부분을 확인하세요."
        
    st.rerun() 


# --- 메인 UI 구성 ---

def main_app():
    initialize_session_state()
    st.markdown(CELL_STYLE, unsafe_allow_html=True) # 전역 CSS 스타일 적용
    
    st.title("Streamlit Sudoku")
    
    # --- 컨트롤 패널 (Shuffle, Finish, 난이도, 타이머) ---
    
    col_shuffle, col_prob_label, col_prob_edit, col_timer, col_finish = st.columns([1.5, 0.8, 1, 1.5, 1.5])
    
    if col_shuffle.button("Shuffle", key="ShuffleButton", use_container_width=True):
        shuffle_click()
    
    # 난이도 설정
    col_prob_label.markdown("<div style='text-align: right; margin-top: 10px; font-size: 13px;'>빈칸 확률 (0~1):</div>", unsafe_allow_html=True)
    col_prob_edit.text_input("난이도 확률", 
                             value=st.session_state.difficulty_prob, 
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


    # --- Sudoku 그리드 영역 ---
    
    # 9x9 그리드 구현 (전체 너비를 사용하도록 설정)
    board_cols = st.columns(9)
    
    for i in range(9):
        # 가로 구분선 스타일: 3행, 6행 아래에 굵은 선 추가
        border_bottom = "2px solid black" if i in [2, 5] else "1px solid #ccc"
        
        # 9개의 셀을 위한 컬럼 구성 (각 행마다 다시 컬럼을 정의해야 합니다)
        cols = st.columns([1, 1, 1, 0.02, 1, 1, 1, 0.02, 1, 1, 1])
        col_index = 0
        
        for j in range(9):
            is_initial_cell = (i, j) in st.session_state.initial_cells
            current_val = st.session_state.board[i][j]
            cell_key = f"cell_{i}_{j}"
            cell_color = st.session_state.cell_colors.get((i, j), 'red')
            
            # 세로 구분선 스타일: 3열, 6열 다음에 굵은 선 추가
            border_right = "2px solid black" if j in [2, 5] else "1px solid #ccc"
            
            # 셀 스타일
            
            if is_initial_cell:
                # 고정된 셀 (클래스 스타일 사용)
                cell_html = f"""
                <div class="fixed-cell" style="border-right: {border_right}; border-bottom: {border_bottom};">
                    {current_val}
                </div>
                """
                cols[col_index].markdown(cell_html, unsafe_allow_html=True)
            else:
                # 사용자 입력 가능 셀 (Streamlit text_input 사용)
                # 입력 필드의 CSS를 직접 제어할 수 없어, 텍스트 색상을 인라인으로 주입합니다.
                
                # Streamlit 위젯은 마크다운처럼 스타일 클래스를 직접 적용하기 어려우므로,
                # on_change 이벤트로 상태를 갱신하고, 인라인 스타일을 주입합니다.
                
                input_style = f"color: {cell_color}; border-right: {border_right}; border-bottom: {border_bottom};"
                
                cols[col_index].text_input(" ", 
                                           value=current_val, 
                                           max_chars=1, 
                                           key=cell_key, 
                                           on_change=update_cell_value, 
                                           args=(i, j), 
                                           label_visibility="collapsed",
                                           placeholder=" ")
                
                # 추가적인 인라인 스타일 주입을 위해 HTML/CSS 사용
                st.markdown(f"""
                <style>
                div[data-testid="stTextInput"] input[aria-label=" "][value="{current_val}"] {{
                    color: {cell_color} !important;
                    border-right: {border_right} !important;
                    border-bottom: {border_bottom} !important;
                }}
                </style>
                """, unsafe_allow_html=True)
                
            col_index += 1
            
            # 3열과 6열 다음에는 굵은 세로 구분선 역할을 하는 빈 컬럼 추가
            if j in [2, 5]:
                # 굵은 세로선 구현 (컬럼 자체의 배경색으로 표현)
                cols[col_index].markdown('<div style="background-color: black; width: 100%; height: 47px;"></div>', unsafe_allow_html=True)
                col_index += 1
        
        # 각 행 사이에 약간의 마진을 추가하여 간격 확보 (선이 겹치는 문제 방지)
        st.markdown('<div style="height: 1px;"></div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main_app()

import streamlit as st
import random
from datetime import datetime
import time # 타이머를 위해 time 모듈 추가

# --- CSS 스타일 정의 ---
# Streamlit 위젯의 기본 스타일을 오버라이드하여 스도쿠 보드 모양을 만듭니다.
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

/* 스도쿠 3x3 블록 구분선 스타일 (3번째, 6번째 행과 열에 적용될 보더) */
.col-border-right {
    border-right: 3px solid black !important;
}

.row-border-bottom {
    border-bottom: 3px solid black !important;
}

/* Streamlit에서 생성되는 경고 메시지 스타일 숨기기 (경고 메시지가 너무 많아지는 것을 방지) */
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
        # Sudoku.ui에서 가져온 초기 보드 구조를 기반으로 한 9x9 배열 (정답 기반)
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
        st.session_state.difficulty_prob = 0.7  # 빈칸으로 남길 확률 (높을수록 어려움)
        st.session_state.result_message = "Shuffle 버튼을 눌러 게임을 시작하세요"
        
        st.session_state.board = [[""] * 9 for _ in range(9)]
        st.session_state.correct_board = [[""] * 9 for _ in range(9)]
        st.session_state.game_start_time = datetime.now()
        st.session_state.timer_running = False
        st.session_state.time_finished_display = "00:00"
        st.session_state.initial_cells = set()  # 초기 고정된 셀의 (r, c) 좌표
        st.session_state.cell_colors = {} # { (i, j): 'red' }
        st.session_state.initialized = True
        
        # 초기화 후 바로 Shuffle 실행
        shuffle_click(initial_run=True)


# --- 게임 로직 함수 ---

def shuffle_click(initial_run=False):
    """보드를 셔플하고 새 게임을 시작합니다."""
    # 난이도 입력 값 처리
    if not initial_run:
        try:
            prob = float(st.session_state.get('difficulty_prob_input', st.session_state.difficulty_prob))
            st.session_state.difficulty_prob = max(0.0, min(1.0, prob)) 
        except ValueError:
            st.session_state.difficulty_prob = 0.7 
    
    AVal = st.session_state.initial_solution
    
    # 1. 1~9 숫자 셔플 (스도쿠 정답의 변형)
    random19 = list(range(1, 10))
    random.shuffle(random19)
    
    # 2. 정답 보드 생성 (셔플된 값 적용)
    correct_board = [[str(random19[int(AVal[i][j]) - 1]) for j in range(9)] for i in range(9)]
    
    # 3. 사용자 보드 생성 (Blank 적용 및 초기 고정 셀 위치 저장)
    new_board = [[correct_board[i][j] for j in range(9)] for i in range(9)]
    initial_cells = set()
    prob = st.session_state.difficulty_prob
    
    st.session_state.cell_colors = {} # 색상 초기화
    
    for i in range(9):
        for j in range(9):
            if random.random() > prob: # prob 값보다 크면 빈칸으로 만듦 (난이도)
                new_board[i][j] = ""
            else:
                initial_cells.add((i, j))
            
            # 초기 고정 셀은 'black'으로, 사용자 입력 셀은 'red'로 기본 설정
            color = 'black' if (i, j) in initial_cells else 'red'
            st.session_state.cell_colors[(i, j)] = color

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
        # 잘못된 입력은 무시하고 이전 값으로 롤백하여 UI에 표시 (Streamlit의 특성상 바로 반영은 어려움)
        # 하지만 st.session_state.board[r][c]는 이전 값을 유지하게 됩니다.
        pass
    
    # 이 함수가 실행된 후 Streamlit은 자동으로 새로고침됩니다.
    
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
            
            # 초기 고정 셀이 아닌, 사용자 입력/빈칸을 확인
            if (i, j) not in st.session_state.initial_cells:
                if current_val != correct_val:
                    st.session_state.cell_colors[(i, j)] = 'red' # 틀린 부분은 빨간색
                    is_correct = False
                else:
                    st.session_state.cell_colors[(i, j)] = 'green' # 맞은 부분은 녹색 (피드백을 위해)

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
    
    st.title("Streamlit Sudoku 🧩")
    
    # --- 컨트롤 패널 (Shuffle, Finish, 난이도, 타이머) ---
    
    col_shuffle, col_prob_label, col_prob_edit, col_timer, col_finish = st.columns([1.5, 0.8, 1, 1.5, 1.5])
    
    # Shuffle 버튼
    if col_shuffle.button("Shuffle", key="ShuffleButton", use_container_width=True):
        shuffle_click()
    
    # 난이도 설정
    col_prob_label.markdown("<div style='text-align: right; margin-top: 10px; font-size: 13px;'>빈칸 확률 (0~1):</div>", unsafe_allow_html=True)
    col_prob_edit.text_input("난이도 확률", 
                             value=f"{st.session_state.difficulty_prob:.2f}", 
                             key='difficulty_prob_input', 
                             label_visibility="collapsed")
    
    # 타이머 표시
    # 게임 중일 때만 현재 시간을 계산하고, finished_display는 게임 종료 시점의 시간을 유지합니다.
    if st.session_state.timer_running:
        elapsed_time = datetime.now() - st.session_state.game_start_time
        minutes = int(elapsed_time.total_seconds() // 60)
        seconds = int(elapsed_time.total_seconds() % 60)
        time_display = f"{minutes:02d}:{seconds:02d}"
        
        # 타이머를 1초마다 업데이트하기 위해 st.empty()와 time.sleep() 사용
        # st.rerun() 대신 time.sleep()과 st.empty().markdown() 조합이 더 효율적
        timer_placeholder = col_timer.empty()
        timer_placeholder.markdown(f"<div style='background-color: white; text-align: center; font-weight: bold; padding: 5px; border: 1px solid #ccc; font-size: 16px; margin-top: 5px;'>⏱️ {time_display}</div>", unsafe_allow_html=True)
        time.sleep(1)
        st.experimental_rerun()
        
    else:
        time_display = st.session_state.time_finished_display
        col_timer.markdown(f"<div style='background-color: white; text-align: center; font-weight: bold; padding: 5px; border: 1px solid #ccc; font-size: 16px; margin-top: 5px;'>⏱️ {time_display}</div>", unsafe_allow_html=True)


    # Finish 버튼
    if col_finish.button("Finish", key="FinishButton", use_container_width=True):
        complete_test_click()

    # --- 결과 메시지 ---
    st.markdown("---")
    st.info(st.session_state.result_message)
    st.markdown("---")


    # --- Sudoku 그리드 영역 ---
    
    # 9x9 그리드 구현 (전체 너비를 사용하도록 설정)
    
    for i in range(9):
        # 9개의 컬럼을 1:1:1 비율로 정의하고, 3x3 블록 구분을 위해 얇은 컬럼을 추가합니다.
        # 비율: 1(셀), 1(셀), 1(셀), 0.05(경계선), 1(셀), 1(셀), 1(셀), 0.05(경계선), 1(셀), 1(셀), 1(셀)
        cols_config = [1] * 3 + [0.05] + [1] * 3 + [0.05] + [1] * 3
        cols = st.columns(cols_config)
        
        col_index = 0
        
        for j in range(9):
            is_initial_cell = (i, j) in st.session_state.initial_cells
            current_val = st.session_state.board[i][j]
            cell_key = f"cell_{i}_{j}"
            cell_color = st.session_state.cell_colors.get((i, j), 'red')
            
            # CSS 클래스를 사용하여 3x3 블록의 경계선 스타일을 적용
            cell_class = ""
            if j in [2, 5]:
                cell_class += "col-border-right "
            if i in [2, 5]:
                cell_class += "row-border-bottom "
            
            
            # 3열과 6열 다음에는 굵은 세로 구분선 역할을 하는 빈 컬럼 처리
            if j in [3, 6]:
                # 굵은 세로선 컬럼: 이 부분은 실제로 빈 컬럼으로 사용
                col_index += 1
            
            
            # 셀 스타일 및 위젯/마크다운 렌더링
            if is_initial_cell:
                # 고정된 셀 (fixed-cell 클래스 스타일 사용)
                cell_html = f"""
                <div class="fixed-cell {cell_class}">
                    {current_val}
                </div>
                """
                cols[col_index].markdown(cell_html, unsafe_allow_html=True)
            else:
                # 사용자 입력 가능 셀 (Streamlit text_input 사용)
                # 입력 필드에 직접 클래스나 인라인 스타일을 적용하기 어려우므로, 
                # st.text_input의 기본 스타일을 오버라이드하고, 텍스트 색상만 인라인으로 주입합니다.
                
                # 주의: st.text_input의 input 스타일을 오버라이드하기 위해 고유한 CSS를 사용해야 합니다.
                # 여기서는 셀의 경계선 스타일을 **텍스트 입력 자체**에 인라인으로 적용합니다.
                
                border_right_style = "3px solid black" if j in [2, 5] else "1px solid #ccc"
                border_bottom_style = "3px solid black" if i in [2, 5] else "1px solid #ccc"

                cols[col_index].markdown(f"""
                <style>
                div[data-testid="stTextInput"] input[aria-label=" "][value="{current_val}"][key="{cell_key}"] {{
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
                                           args=(i, j), 
                                           label_visibility="collapsed",
                                           placeholder=" ")
                
            col_index += 1
            
        # 각 행 사이에 마진을 줄여 선이 겹치는 문제를 해결합니다.
        # 이 부분은 전체 CSS에서 div[data-testid="stTextInput"]의 margin을 조절하여 처리했습니다.
        
if __name__ == "__main__":
    main_app()

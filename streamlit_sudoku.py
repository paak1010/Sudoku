import streamlit as st
import random
import time
from datetime import datetime, timedelta

# Streamlit 앱의 세션 상태(Session State)를 초기화합니다.
def initialize_session_state():
    """
    게임 상태를 초기화하거나, 이미 실행 중이면 유지합니다.
    """
    if 'initialized' not in st.session_state:
        # Sudoku.ui에서 가져온 초기 보드 구조 (1~9로 채워진 정답 보드)
        # 실제 Sudoku.ui의 버튼 텍스트를 기반으로 한 9x9 배열을 여기에 정의해야 합니다.
        # 예시로 제공된 Sudoku.ui의 초기값 배열 (A00부터 A88까지의 텍스트 값)
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
        st.session_state.difficulty_prob = 0.7  # Sudoku.ui의 pEdit 기본값
        st.session_state.result_message = "Shuffle을 눌러 게임을 시작하세요"
        
        # 첫 시작 시에는 보드를 빈 값으로 설정하고, ShuffleClick에서 실제 보드를 설정합니다.
        st.session_state.board = [[""] * 9 for _ in range(9)]
        st.session_state.correct_board = [[""] * 9 for _ in range(9)]
        st.session_state.game_start_time = datetime.now()
        st.session_state.timer_running = False
        st.session_state.time_finished_display = "00:00"
        st.session_state.initial_cells = set() # 초기 고정된 셀의 위치 (i, j)
        st.session_state.initialized = True
        
        # 초기화 후 바로 Shuffle 실행
        shuffle_click(initial_run=True)


def shuffle_click(initial_run=False):
    """
    보드를 셔플하고 새 게임을 시작합니다. (PyQt의 ShuffleClick 역할)
    """
    if not initial_run:
        try:
            # pEdit의 텍스트 입력값을 가져와 난이도 확률을 업데이트합니다.
            prob = float(st.session_state.get('difficulty_prob_input', st.session_state.difficulty_prob))
            st.session_state.difficulty_prob = max(0.0, min(1.0, prob)) 
        except ValueError:
            st.session_state.difficulty_prob = 0.7 
    
    AVal = st.session_state.initial_solution
    
    # 1. 1~9 숫자 셔플
    random19 = list(range(1, 10))
    random.shuffle(random19)
    
    # 2. 정답 보드 생성 (셔플된 값 적용)
    # PyQt 코드: self.ButtonList[i][j].setText(str(random19[int(self.AVal[i][j]) - 1]))
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

    # 4. 세션 상태 업데이트
    st.session_state.correct_board = correct_board
    st.session_state.board = new_board
    st.session_state.initial_cells = initial_cells
    st.session_state.game_start_time = datetime.now()
    st.session_state.timer_running = True
    st.session_state.result_message = "버튼을 클릭하고 1~9사이의 정수를 입력하세요."
    st.session_state.time_finished_display = "00:00"
    
    # st.rerun()은 이 함수를 호출한 곳에서 처리합니다.


def complete_test_click():
    """
    채점 로직을 실행합니다. (PyQt의 CompleteTestClick 역할)
    """
    st.session_state.timer_running = False # 타이머 정지

    is_correct = True
    current_time_display = "00:00"
    
    # 시간 계산 및 저장
    elapsed_time = datetime.now() - st.session_state.game_start_time
    # total_seconds를 사용하여 mm:ss 포맷팅 (PyQt QTime.toString("mm:ss") 대체)
    minutes = int(elapsed_time.total_seconds() // 60)
    seconds = int(elapsed_time.total_seconds() % 60)
    current_time_display = f"{minutes:02d}:{seconds:02d}"
    st.session_state.time_finished_display = current_time_display

    # 채점 및 색상 결정
    for i in range(9):
        for j in range(9):
            current_val = st.session_state.board[i][j]
            correct_val = st.session_state.correct_board[i][j]
            
            # 입력값이 비어있거나(Sudoku 규칙 위반), 정답과 다른 경우
            if current_val != correct_val:
                # 초기 고정된 셀이 잘못된 경우는 없다고 가정합니다.
                if (i, j) not in st.session_state.initial_cells:
                    st.session_state[f"color_{i}_{j}"] = "red" # 사용자 입력 오류
                    is_correct = False
            else:
                st.session_state[f"color_{i}_{j}"] = "black" # 정답

    # 결과 메시지 출력
    if is_correct:
        st.session_state.result_message = f"정답입니다! 퍼즐을 풀었습니다. 소요 시간: {current_time_display}"
        st.balloons()
    else:
        st.session_state.result_message = "아쉽지만, 정답이 아닙니다. 빨간색으로 표시된 부분을 확인하세요."
        
    st.rerun() # UI 업데이트를 위해 강제 재실행


def main_app():
    """
    Streamlit 앱의 메인 UI 레이아웃을 구성합니다.
    """
    initialize_session_state()

    # --- UI 헤더 및 컨트롤 영역 ---
    
    st.title("Sudoku")
    
    # Shuffle, Finish 버튼, 난이도 입력 필드
    col_shuffle, col_prob_label, col_prob_edit, col_finish = st.columns([2, 1, 1.5, 2])
    
    if col_shuffle.button("Shuffle", key="ShuffleButton"):
        shuffle_click()
    
    col_prob_label.markdown("<div style='text-align: right; margin-top: 10px;'>난이도 확률:</div>", unsafe_allow_html=True)
    col_prob_edit.text_input("난이도 확률", 
                             value=st.session_state.difficulty_prob, 
                             key='difficulty_prob_input', 
                             label_visibility="collapsed")
    
    if col_finish.button("Finish", key="FinishButton"):
        complete_test_click()
    
    # --- 타이머 및 메시지 영역 ---
    
    # 타이머 표시 (PyQt의 QTimer를 대체)
    # Streamlit은 지속적인 업데이트를 지원하지 않으므로, 이 코드는 페이지가 새로고침될 때만 시간을 업데이트합니다.
    # 실시간 타이머를 위해선 'streamlit-autorefresh'와 같은 외부 컴포넌트가 필요합니다.
    
    col_timer, col_res = st.columns([1, 5])
    
    if st.session_state.timer_running:
        elapsed_time = datetime.now() - st.session_state.game_start_time
        # f-string 포맷팅을 사용하여 PyQt의 toString("mm:ss")를 대체
        minutes = int(elapsed_time.total_seconds() // 60)
        seconds = int(elapsed_time.total_seconds() % 60)
        time_display = f"{minutes:02d}:{seconds:02d}"
    else:
        time_display = st.session_state.time_finished_display
        
    col_timer.markdown(f"<div style='background-color: white; text-align: center; font-weight: bold; padding: 5px; border: 1px solid #ccc; font-size: 16px;'>{time_display}</div>", unsafe_allow_html=True)
    
    col_res.markdown(f"<div style='text-align: center; font-weight: bold; color: green;'>{st.session_state.result_message}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- Sudoku 그리드 영역 ---

    # 9x9 그리드 구현
    for i in range(9):
        # 9개의 셀 + 2개의 구분선(0.1 너비)을 위한 컬럼 구성
        cols = st.columns([1, 1, 1, 0.1, 1, 1, 1, 0.1, 1, 1, 1])
        col_index = 0
        for j in range(9):
            is_initial_cell = (i, j) in st.session_state.initial_cells
            current_val = st.session_state.board[i][j]
            cell_key = f"cell_{i}_{j}"
            cell_color = st.session_state.get(f"color_{i}_{j}", "black")

            # 세로 구분선 (3, 6 열 다음)
            if j == 3 or j == 6:
                # 세로줄 스타일: 검정색 실선
                cols[col_index].markdown('<div style="border-left: 2px solid black; height: 100%;"></div>', unsafe_allow_html=True)
                col_index += 1

            # 셀 업데이트 핸들러
            def update_cell_value(r, c):
                new_val = st.session_state[f"cell_{r}_{c}"].strip()
                # 1~9 사이의 숫자만 허용하고, 그 외는 빈 값으로 처리
                if new_val.isdigit() and 1 <= int(new_val) <= 9:
                    st.session_state.board[r][c] = new_val
                elif new_val == "":
                    st.session_state.board[r][c] = ""
                else:
                    # 잘못된 입력은 현재 값으로 덮어쓰기 (다시 입력하도록)
                    st.session_state[f"cell_{r}_{c}"] = st.session_state.board[r][c]
                st.session_state[f"color_{r}_{c}"] = "red" # 사용자가 값을 입력하면 빨간색으로 변경
                
                # Streamlit의 상태 변경은 자동 새로고침을 유발합니다.
                st.rerun() 
            
            # 셀 표시 로직
            if is_initial_cell:
                # 초기 고정된 셀 (사용자 입력 불가)
                # 스타일: 배경 회색, 글자색 검정
                style = "background-color: #f0f2f6; text-align: center; font-weight: bold; padding: 5px; border: 1px solid #ccc; height: 36px; line-height: 24px;"
                cols[col_index].markdown(f"<div style='{style}'>{current_val}</div>", unsafe_allow_html=True)
            else:
                # 사용자 입력 가능 셀
                # 스타일: 글자색은 채점 결과에 따라 결정 (기본은 빨강)
                
                # Streamlit의 text_input 글자색을 직접 변경하려면 CSS injection이 필요합니다.
                # 여기서는 버튼이나 st.text_input을 사용하며, 글자색은 마크다운으로 표시하는 것이 더 일반적입니다.
                
                # 간단한 텍스트 입력으로 구현
                cols[col_index].text_input(" ", 
                                           value=current_val, 
                                           max_chars=1, 
                                           key=cell_key, 
                                           on_change=update_cell_value, 
                                           args=(i, j), 
                                           label_visibility="collapsed")
                

                if current_val:
                    style = f"color: {cell_color}; text-align: center; font-weight: bold; font-size: 16px;"
                    cols[col_index].markdown(f"<p style='{style}; margin-top: -30px; margin-bottom: 0;'>{current_val}</p>", unsafe_allow_html=True)


            col_index += 1
        
        # 가로 구분선 (3, 6 행 다음)
        if i == 2 or i == 5:
            st.markdown("<hr style='border-top: 2px solid black;'>", unsafe_allow_html=True)
        else:
            st.markdown("")

# 애플리케이션 실행
if __name__ == "__main__":
    main_app()
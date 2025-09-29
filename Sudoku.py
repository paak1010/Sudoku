import sys
import random
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
from PyQt5.uic import loadUiType
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt, QTimer, QTime

form_class = loadUiType("Sudoku.ui")[0]

class SudokuUI(QMainWindow, form_class):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.ButtonList = [[self.A00, self.A01, self.A02, self.A03, self.A04, self.A05, self.A06, self.A07, self.A08],
                           [self.A10, self.A11, self.A12, self.A13, self.A14, self.A15, self.A16, self.A17, self.A18],
                           [self.A20, self.A21, self.A22, self.A23, self.A24, self.A25, self.A26, self.A27, self.A28],
                           [self.A30, self.A31, self.A32, self.A33, self.A34, self.A35, self.A36, self.A37, self.A38],
                           [self.A40, self.A41, self.A42, self.A43, self.A44, self.A45, self.A46, self.A47, self.A48],
                           [self.A50, self.A51, self.A52, self.A53, self.A54, self.A55, self.A56, self.A57, self.A58],
                           [self.A60, self.A61, self.A62, self.A63, self.A64, self.A65, self.A66, self.A67, self.A68],
                           [self.A70, self.A71, self.A72, self.A73, self.A74, self.A75, self.A76, self.A77, self.A78],
                           [self.A80, self.A81, self.A82, self.A83, self.A84, self.A85, self.A86, self.A87, self.A88]]

        for i in range(0, 9):
            for number in self.ButtonList[i]:
                number.clicked.connect(self.NumClick)

        # 초기값 Setting
        self.AVal = []
        for i in range(0, 9):
            temp = []
            for j in range(0, 9):
                temp.append(str(self.ButtonList[i][j].text()))
            self.AVal.append(temp)
        
        # 정답 보드 저장 (셔플 전의 초기 상태)
        self.CorrectVal = [row[:] for row in self.AVal]

        # 타이머 관련 변수 및 객체를 __init__에서 먼저 정의합니다.
        self.game_time = QTime(0, 0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer_is_running = False

        # **시간 레이블의 배경색을 흰색으로 변경 및 정렬**
        timer_label = self.findChild(QLabel, 'label')
        if timer_label:
            timer_label.setStyleSheet("background-color: white;")
            # Qlabel의 텍스트를 중앙으로 정렬
            timer_label.setAlignment(Qt.AlignCenter)

        # 초기설정값을 순서바꾸기를 통해 문제가 나갈 때마다 랜덤하게 달라지게 한다.
        self.ShuffleClick()
        self.ShuffleButton.clicked.connect(self.ShuffleClick)
        self.FinishButton.clicked.connect(self.CompleteTestClick)

    def ShuffleClick(self):
        random19 = list(range(1, 10))
        random.shuffle(random19)
        
        # 1,2,3,4,5,6,7,8,9 를 자리바꾸기한 결과로 재배치
        for i in range(0, 9):
            for j in range(0, 9):
                self.ButtonList[i][j].setText(str(random19[int(self.AVal[i][j]) - 1]))
                # 모든 버튼의 글자색을 검정색으로 초기화
                self.ButtonList[i][j].setStyleSheet('QPushButton {color: black;}')

        # 정답 보드 업데이트
        self.CorrectVal = [[str(random19[int(self.AVal[i][j]) - 1]) for j in range(9)] for i in range(9)]

        # 확률적으로 버튼 숫자를 Blank로 바꾼다.
        for i in range(0, 9):
            for j in range(0, 9):
                if random.random() > float(self.pEdit.text()):
                    self.ButtonList[i][j].setText("")

        # 새 게임 시작 시 타이머 재설정 및 시작
        self.game_time.setHMS(0, 0, 0)
        self.update_timer()
        if not self.timer_is_running:
            self.timer.start(1000)
            self.timer_is_running = True

    def update_timer(self):
        self.game_time = self.game_time.addSecs(1)
        # UI 파일에서 'label' 위젯의 이름을 찾아 적용
        timer_label = self.findChild(QLabel, 'label')
        if timer_label:
            timer_label.setText(self.game_time.toString("mm:ss"))

    def NumClick(self):
        for i in range(0, 9):
            for j in range(0, 9):
                if self.sender() == self.ButtonList[i][j]:
                    self.XLoc = i
                    self.YLoc = j

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_1:
                self.ButtonList[self.XLoc][self.YLoc].setText("1")
            elif event.key() == Qt.Key_2:
                self.ButtonList[self.XLoc][self.YLoc].setText("2")
            elif event.key() == Qt.Key_3:
                self.ButtonList[self.XLoc][self.YLoc].setText("3")
            elif event.key() == Qt.Key_4:
                self.ButtonList[self.XLoc][self.YLoc].setText("4")
            elif event.key() == Qt.Key_5:
                self.ButtonList[self.XLoc][self.YLoc].setText("5")
            elif event.key() == Qt.Key_6:
                self.ButtonList[self.XLoc][self.YLoc].setText("6")
            elif event.key() == Qt.Key_7:
                self.ButtonList[self.XLoc][self.YLoc].setText("7")
            elif event.key() == Qt.Key_8:
                self.ButtonList[self.XLoc][self.YLoc].setText("8")
            elif event.key() == Qt.Key_9:
                self.ButtonList[self.XLoc][self.YLoc].setText("9")
            else:
                print("Error")
        self.ButtonList[self.XLoc][self.YLoc].setStyleSheet('QPushButton {color: red;}')

    def CompleteTestClick(self):
        self.resEdit.setText("")
        self.timer.stop() # 게임 완료 시 타이머 정지

        is_correct = True
        for i in range(0, 9):
            for j in range(0, 9):
                # 정답과 현재 값이 다른 경우
                if self.ButtonList[i][j].text() != self.CorrectVal[i][j]:
                    self.ButtonList[i][j].setStyleSheet('QPushButton {color: red;}')
                    is_correct = False
                else:
                    self.ButtonList[i][j].setStyleSheet('QPushButton {color: black;}')

        # 전체 정답 여부에 따른 메시지 출력
        if is_correct:
            self.resEdit.setText(f"정답입니다! 퍼즐을 풀었습니다. 소요 시간: {self.game_time.toString('mm:ss')}")
        else:
            self.resEdit.setText("아쉽지만, 정답이 아닙니다. 빨간색으로 표시된 부분을 확인하세요.")

app = QApplication(sys.argv)
myWindow = SudokuUI(None)
myWindow.show()
app.exec_()
''' Writes missed questions and incorrect answers to missed.py
vbox implemented; question now inside window
'''


import sys
from random import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Question(object):
    def __init__(self):
        self.question = ''
        self.answer = []

class QuizWidget(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setGeometry(300, 300, 300, 100)

        self.missed = open('missed.py', 'a')

        self.qList = {}
        self.make_list(self.qList)

        self.qNumber = randint(0, len(self.qList) - 1)
        self.setWindowTitle('Quiz Applet')
        self.labelQuestion = QLabel(str(self.qList[self.qNumber].question))

        self.answerBox = QLineEdit()
        self.connect(self.answerBox, SIGNAL('returnPressed()'), self.check_answer)

#       grid = QGridLayout()
#       grid.addWidget(self.labelQuestion, 0, 0)
#       grid.addWidget(self.answerBox, 1, 0)
#       self.setCentralWidget(grid)

#       title = self.addDockWidget(self.labelQuestion)
#       self.setCentralWidget(self.answerBox)
        self.main_frame = QWidget()
        self.setCentralWidget(self.main_frame)
#       grid.setParent(self.main_frame)

        vbox = QVBoxLayout()
        vbox.addWidget(self.labelQuestion)
        vbox.addWidget(self.answerBox)
        self.main_frame.setLayout(vbox)

    def make_list(self, probList):
        fh = open('problems.txt', 'r')
        i = 0
        lines = fh.readlines()
        for line in lines:
            words = line.split()
            self.a = Question()
            self.a.question = words[0]
            for entry in words[1:len(words)]:
                self.a.answer.append(entry)
            probList[i] = self.a
            i += 1

    def check_answer(self):
        guess = self.answerBox.text()
        currentQuestion = self.qList[self.qNumber]
        guess.replace(' ', '')
        guess.replace('[', '(')
        guess.replace(']', ')')
        guess.replace('**', '^')
        if guess in currentQuestion.answer:
            print 'you win!'
        else:
            print 'nope'
            self.missed.write(currentQuestion.question)
            self.missed.write(' ')
            self.missed.write(guess)
            self.missed.write('\n')
        
def main():
    app = QApplication(sys.argv)
    w = QuizWidget()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

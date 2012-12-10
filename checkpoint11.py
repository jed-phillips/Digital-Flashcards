# Save file/load on startup
# Checkboxes to choose decks to include

import sys
import xml.dom.minidom
import os
from random import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class cards(object):
    '''Reads through the FlashCards directory and makes a list of the available xml files
    after you create a cards object, every time you run the readQuestions(filename) function
    it adds all the questions from that file to the list of questions. Questions are stored
    as question objects which have the question text stored and a list containing all 
    possible answers.'''

    files = []
    qList = []
    def __init__(self):
        try:
            os.chdir('FlashCards')
            files = os.listdir(os.getcwd())
            for name in files:
              if name[-3:] != '.xml':
                files.remove(name)
        except:
            print "FlashCards directory does not exist"
            return

    def readQuestions(self, filename):
        try:
            cardfile = open(os.getcwd()+'/'+filename)
            data = xml.dom.minidom.parseString(cardfile.read())
            cardfile.close()
            for element in data.getElementsByTagName('question'):
                self.qList.append(question(element))
        except:
            raise
            print 'Error reading file: ' + filename
            return

    def totalWeight(self):
        total = 0
        for que in self.qList:
            total+=que.weight()
        return total

    def randomWeightedIndex(self):
        number=randint(1,self.totalWeight())
        total = 0
        for que in self.qList:
            total+=que.weight()
            if total>=number:
                return self.qList.index(que)

    def __str__(self):
        return self.files

class question(object):
    '''Digests a given question element from the xml file. Question elements are separated by
    the text and the acceptable answers.'''

    question = None
    answers = []
    missCounter = 0
    totalCounter = 0

    def __init__(self, element):
        self.question = getValue(element, 'text')
        self.answers = []
        for ans in element.getElementsByTagName('answer'):
            self.answers.append(ans.childNodes[0].nodeValue.replace(" ", ""))

    def weight(self):
        if 2*self.missCounter - self.totalCounter < 1:
            return 1
        else:
            return 2*self.missCounter - self.totalCounter + 1

    def __str__(self):
        return self.question

def getValue(element, name):
    '''A function to get the value of a certain element regardless of whether it's an element
    or an attribute'''

    if element.hasAttribute(name):
        return element.getAttribute(name)
    elif element.getElementsByTagName(name):
        return element.getElementsByTagName(name)[0].childNodes[0].nodeValue
    else:
        return None

class QuizWidget(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setGeometry(300, 300, 500, 100)

        self.number_correct = 0
        self.number_missed = 0

        self.deck = cards()
        self.deck.readQuestions('science.xml')

        self.setWindowTitle('Quiz Applet')

        self.generate_things()

        self.answerBox = QLineEdit()
        self.connect(self.answerBox, SIGNAL('returnPressed()'), self.check_answer)
        self.connect(self.answerBox, SIGNAL('returnPressed()'), self._update)

        ldw = QDockWidget(self)
        ldw.setAllowedAreas(Qt.TopDockWidgetArea)
        self.missBox = QLabel()
        ldw.setWidget(self.missBox)
        self.addDockWidget(Qt.TopDockWidgetArea, ldw)

        rdw = QDockWidget(self)
        rdw.setAllowedAreas(Qt.TopDockWidgetArea)
        self.correctBox = QLabel()
        rdw.setWidget(self.correctBox)
        self.addDockWidget(Qt.TopDockWidgetArea, rdw)

        bdw = QDockWidget(self)
        bdw.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.notification = QLabel()
        bdw.setWidget(self.notification)
        self.addDockWidget(Qt.BottomDockWidgetArea, bdw)

        self.main_frame = QWidget()
        self.setCentralWidget(self.main_frame)

        self.labelQuestion = QLabel()
        self.labelQuestion.setText(str(self.deck.qList[self.qNumber].question))

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.labelQuestion)
        self.vbox.addWidget(self.answerBox)
        self.main_frame.setLayout(self.vbox)

    def generate_things(self):
        self.qNumber = self.deck.randomWeightedIndex()
        self.currentAnswers = self.deck.qList[self.qNumber].answers

    def check_answer(self):
        guess = self.answerBox.text()
        guess.replace(' ', '')
        guess.replace('[', '(')
        guess.replace(']', ')')
        guess.replace('**', '^')

        if guess in self.currentAnswers:
            print 'you win!'
            self.number_correct += 1
            self.deck.qList[self.qNumber].totalCounter += 1
            self.notificationText = 'Correct!'
        else:
            print 'nope'
            self.number_missed += 1
            self.deck.qList[self.qNumber].missCounter += 1
            self.deck.qList[self.qNumber].totalCounter += 1
            actualAnswer = str(self.currentAnswers[0])
            self.notificationText = 'Nope; the correct answer is '+actualAnswer

    def _update(self):
        self.generate_things()
        self.labelQuestion.clear()
        thing = str(self.deck.qList[self.qNumber].question)
        self.labelQuestion.setText(thing)
        print self.labelQuestion.text()
        self.missBox.setText('Number missed: '+str(self.number_missed))
        self.correctBox.setText('Number correct: '+str(self.number_correct))
        self.answerBox.clear()
        self.notification.setText(self.notificationText)
        self.update()
        
def main():
    app = QApplication(sys.argv)
    w = QuizWidget()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

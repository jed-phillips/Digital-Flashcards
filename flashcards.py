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
            self.files = os.listdir(os.getcwd())
            for name in self.files:
              if name[-4:] != '.xml':
                self.files.remove(name)
        except:
            raise
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
            fix = ans.childNodes[0].nodeValue.replace(' ', '')
            self.answers.append(fix)

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
        '''Initializes main application window and all widgets.
        '''
        QMainWindow.__init__(self)
        self.setGeometry(300, 300, 400, 100)

        # Initialize counters for questions correct and missed
        self.number_correct = 0
        self.number_missed = 0

        # Generate deck of flashcards, and read in questions from command-line
        # passed file.
        self.deck = cards()
        self.deck.readQuestions(sys.argv[(len(sys.argv)-1)])

        self.setWindowTitle('Quiz Applet')

        # Initialize answer box; connect "enter" signal to answer-checker and
        # window-update functions
        self.answerBox = QLineEdit()
        self.connect(self.answerBox, SIGNAL('returnPressed()'), self.check_answer)
        self.connect(self.answerBox, SIGNAL('returnPressed()'), self._update)

        # Create widget to display number of questions missed
        ldw = QDockWidget(self)
        ldw.setAllowedAreas(Qt.TopDockWidgetArea)
        self.missBox = QLabel()
        ldw.setWidget(self.missBox)
        self.addDockWidget(Qt.TopDockWidgetArea, ldw)

        # Create widget to display number of questions answered correctly
        rdw = QDockWidget(self)
        rdw.setAllowedAreas(Qt.TopDockWidgetArea)
        self.correctBox = QLabel()
        rdw.setWidget(self.correctBox)
        self.addDockWidget(Qt.TopDockWidgetArea, rdw)

        # Create widget to notify user of correct or missed answer, and display
        # correct answer if necessary
        bdw = QDockWidget(self)
        bdw.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.notification = QLabel()
        bdw.setWidget(self.notification)
        self.addDockWidget(Qt.BottomDockWidgetArea, bdw)

        # Generate and display first question
        self.generate_things()
        self.labelQuestion = QLabel()
        self.labelQuestion.setText(str(self.deck.qList[self.qNumber].question))

        # Set up layout of main window
        self.main_frame = QWidget()
        self.setCentralWidget(self.main_frame)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.labelQuestion)
        self.vbox.addWidget(self.answerBox)
        self.main_frame.setLayout(self.vbox)

    def generate_things(self):
        '''Generates semi-random question based on weighting index and stores
        list of acceptable answers.
        '''
        self.qNumber = self.deck.randomWeightedIndex()
        self.currentAnswers = self.deck.qList[self.qNumber].answers

    def check_answer(self):
        '''Reads in user-inputted answer, changes certain formatting elements
        to ensure uniformity, and checks reformatted answer against list of
        acceptable answers. Appropriate response is sent to display, and 
        counters are bumped.
        '''
        guess = self.answerBox.text()
        guess.replace(' ', '')
        guess.replace('[', '(')
        guess.replace(']', ')')
        guess.replace('**', '^')

        # Correct answer case:
        if guess in self.currentAnswers:
            self.number_correct += 1
            self.deck.qList[self.qNumber].totalCounter += 1
            self.notificationText = 'Correct!'
        # Wrong answer case:
        else:
            self.number_missed += 1
            self.deck.qList[self.qNumber].missCounter += 1
            self.deck.qList[self.qNumber].totalCounter += 1
            actualAnswer = str(self.currentAnswers[0])
            self.notificationText = 'Nope; the correct answer is '+actualAnswer

    def _update(self):
        '''Prepares window for next question when 'enter' is pressed.
        Generates new question and displays it, clears the answer box, updates
        the counter displays, and shows either the 'answer was correct' or
        'answer was incorrect' response.
        '''
        self.generate_things()
        self.labelQuestion.clear()
        thing = str(self.deck.qList[self.qNumber].question)
        self.labelQuestion.setText(thing)
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

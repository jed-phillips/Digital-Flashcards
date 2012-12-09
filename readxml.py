import xml.dom.minidom
import os

class cards(object):
    '''Reads through the FlashCards directory and makes a list of the available xml files
    after you create a cards object, every time you run the readQuestions(filename) function
    it adds all the questions from that file to the list of questions. Questions are stored
    as question objects which have the question text stored and a list containing all 
    possible answers.'''

    files = []
    questions = []
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
                self.questions.append(question(element))
        except:
            raise
            print 'Error reading file: ' + filename
            return
    def __str__(self):
        return self.files

class question(object):
    '''Digests a given question element from the xml file. Question elements are separated by
    the text and the acceptable answers.'''

    question = None
    answers = []
    def __init__(self, element):
        self.question = getValue(element, 'text')
        for ans in element.getElementsByTagName('answer'):
          self.answers.append(ans.childNodes[0].nodeValue)
    def __str__(self):
        return self.question+self.answers

def getValue(element, name):
    '''A function to get the value of a certain element regardless of whether it's an element
    or an attribute'''

    if element.hasAttribute(name):
        return element.getAttribute(name)
    elif element.getElementsByTagName(name):
        return element.getElementsByTagName(name)[0].childNodes[0].nodeValue
    else:
        return None

card = cards()
card.readQuestions('science.xml')
print card

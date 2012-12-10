from random import *
class question(object):
    missCounter = 0
    totalCounter = 0
    question = 0
    def __init__(self,miss,total,identity):
        self.missCounter = miss
        self.totalCounter = total
        self.question = identity
    def weight(self):
        if 2*self.missCounter -self.totalCounter<1:
            return 1
        else:
            return 2*self.missCounter - self.totalCounter+1
def totalWeight(qList):
    total = 0
    for que in qList:
        total+=que.weight()
    return total

def randomQuestion(qList):
    number = randint(1,totalWeight(qList))
    total = 0
    for que in qList:
        total+=que.weight()
        if total>=number:
            return que

ques = []
ques.append(question(2,5,0))
ques.append(question(15,65,1))
ques.append(question(0,0,2))
#ques.append(question(0,0,3))

n1 = input("How many questions?\n")
i = 0
for n in range(n1):
    weight = round(abs(input("Weight of question " + str(i) + '\n')))
    if weight == 0:
        weight = 1
    ques.append(question(weight-1,weight-1,i))
    i+=1
trials = int(abs(input("How many trials?\n")))
hist = {}
for n in range(trials):
    x=randomQuestion(ques)
    if not hist.has_key(x.question):
        hist[x.question]=1
    else:
        hist[x.question]=hist[x.question]+1
print hist

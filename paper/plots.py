import matplotlib.pyplot as plt
import mpld3
import json
import math

def attemptedGraph(classRoom,responseList):
    total = classRoom.students.count()
    attempted = responseList.count()
    attemptedButLeft = 0
    for i in responseList.values('student'):
        if len(classRoom.students.filter(id=i['student'])) != 1:
            attemptedButLeft += 1

    attempted = attempted - attemptedButLeft    
    notAttempted = total - attempted

    fig = plt.figure(figsize = (4,4))
    x = [attempted,notAttempted,attemptedButLeft]
    label = ['Attempted','Not Attempted','Attempted(Left the class)']
    plt.pie(x, autopct='%1.0f%%', pctdistance=0.8, textprops={'color':"w"})
    plt.legend(labels=label)
    html_str = mpld3.fig_to_html(fig)
    return html_str

def boxPlot(responseList):
    marks=[]
    for i in responseList.values('score'):
        marks.append(i['score'])

    fig = plt.figure(figsize = (4,4))
    bp = plt.boxplot(marks, vert=1, labels=['Marks'])
    html_str = mpld3.fig_to_html(fig)
    return html_str

def questionWiseBarGraph(paper,testResponse):
    html_str_list = []
    questions = paper['questions']
    fig = plt.figure(figsize = (10,2.5*len(questions)))
    n = 0
    for i in questions:
        optionChosen = []
        m = 0
        for j in testResponse:
            paperResponseStr = j.response
            paperResponse = json.loads(paperResponseStr)

            for k in paperResponse:
                if i['qid'] == k['qid']:
                    optionChosen.append(k['optionSelected'])
            
            m += 1
                    
        optionsCount = {i:optionChosen.count(i) for i in optionChosen}
                    
        ans = {'A':0,'B':1,'C':2,'D':3}
        options = ['A','B','C','D','None']
        
        students = []
        
        
        for k in ['A','B','C','D','']:
            try:
                students.append(optionsCount[k])
            except:
                students.append(0)
            
        
        students = [x/m*100 for x in students]
        
        pltNo = n + 1
        pltRow = math.ceil(len(questions) / 2)
        pltCol = 2
            
        plt.subplot(pltRow, pltCol, pltNo)
        subplotBars = plt.bar(options,students)
        subplotBars[ans[i['answer']]].set_color('g')
        
        plt.xticks([0.0,1.0,2.0,3.0,4.0], ['A','B','C','D','None'], fontsize=16)
        plt.ylabel('Students (%)',fontsize=16)
        plt.xlabel(f'Question {n+1}',fontsize=18)
        plt.subplots_adjust(wspace=1, hspace=0.5)
        
        
        n += 1

    html_str = mpld3.fig_to_html(fig)
    return html_str

import csv
import json
import random
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from .forms import TestForm, TestResponseForm, ClassroomForm, CreateUserForm
from .modules import *
from .plots import *


def home(request):
    if request.path == '/signup/':
        form = CreateUserForm()
        if request.method == 'POST' and request.POST['action'] == 'sign up':
            data = request.POST
            def generateUserId(userType):
                if userType in ['T','S']:
                    if userType == 'T':
                        userId = '1'
                    else:
                        userId = '2'
                    for i in range(0,5):
                        userId += str(random.randint(0,9))
                    userExist = User.objects.filter(username = userId).count()
                    if userExist == 0 and userId != '':
                        return int(userId)
                    else:  
                        generateUserId(userType)
    
            formData = {'first_name': data['first_name'], 'last_name': data['last_name'], 'password1': data['password1'], 'password2': data['password2'],}
            uid = generateUserId(data['userType'])
            formData['username'] = uid
            form = CreateUserForm(formData)
            if form.is_valid():
                form.save()
                new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
                login(request, new_user)

                if data['userType'] == 'T':
                    name = data['first_name'] + ' ' + data['last_name']
                    t = Teacher(name=name, id=uid)
                    t.save()
                else:
                    name = data['first_name'] + ' ' + data['last_name']
                    s = Student(name=name, id=uid)
                    s.save()
                return redirect('/')
        else:
            form = CreateUserForm()
        return render(request, 'paper/home.html',{'form':form})
    else:
        err = ''
        if request.method == 'POST' and request.POST['action'] == 'log in':
            username = request.POST.get('userId')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                err = 'User ID or password is incorrect.'

        return render(request, 'paper/home.html', {'userAuthenticated':request.user.is_authenticated,'error':err})

def logoutUser(request):
    logout(request)
    return redirect('home')

def loginRequired(request):
    return render(request, 'paper/loginRequired.html',{'userAuthenticated':request.user.is_authenticated})

def teacher(request,pk_classroom=0):
    currentUser = int(request.user.username)
    teacher = Teacher.objects.get(id=currentUser)
    if pk_classroom == 0:
        try:
            className = teacher.classes.all()
            classCode = str(className[0])
            tempClass = Classroom.objects.get(class_code=classCode[0:5])
            pk_classroom = tempClass.id
            classRoom = Classroom.objects.get(id=pk_classroom)
            tests =  Test.objects.filter(classes=pk_classroom,creator=currentUser)
            mssg = ''
        except:
            classRoom = tests = testGiven = testList = ''
            mssg = 'Not part of any class'

    else:
        classRoom = Classroom.objects.get(id=pk_classroom)
        tests =  Test.objects.filter(classes=pk_classroom,creator=currentUser)
        mssg = ''


    if request.method == 'POST':
        if 'className' in request.POST:
            classData = request.POST
            className = classData['className']
            
            cl = Classroom.objects.values_list('class_code')
            classCodeList = [x[0] for x in cl]
            classCode = generateClassCode(classCodeList)
            formData = {'class_name':className,'teachers':[teacher],'class_code':classCode}
            form = ClassroomForm(formData)
            if form.is_valid():
                form.save()
                print("form sent")
                currentClassroom = Classroom.objects.get(class_code=classCode)
                teacher.classes.add(currentClassroom)

        elif 'classCode' in request.POST:
            classroom = request.POST
            classCode = classroom['classCode']
            try:
                currentClassroom = Classroom.objects.get(class_code=classCode)
                teacher.classes.add(currentClassroom)
                currentClassroom.teachers.add(teacher)
                print('teacher added to class')
            except:
                print('Invalid class code.')
        
        return HttpResponseRedirect("/classroom/")

    return render(request, 'paper/teacher.html',{'teacher': teacher,'tests':tests,'currentClass':classRoom,'noClass':mssg,'userAuthenticated':request.user.is_authenticated})

def student(request,pk_classroom=0):
    currentUser = int(request.user.username)
    student = Student.objects.get(id=currentUser)
    if pk_classroom == 0:
        try:
            className = student.classes.all()
            classCode = str(className[0])
            tempClass = Classroom.objects.get(class_code=classCode[0:5])
            pk_classroom = tempClass.id
            classRoom = Classroom.objects.get(id=pk_classroom)
            tests =  Test.objects.filter(classes=pk_classroom)
            testList = TestResponse.objects.filter(student=currentUser)
            testGiven = []
            for i in testList:
                testGiven.append(i.test.id)
            mssg = ''
            hideElement = ''
        except:
            classRoom = tests = testGiven = testList = ''
            mssg = 'Not part of any class'
            hideElement = 'hide'

    else:
        classRoom = Classroom.objects.get(id=pk_classroom)
        tests =  Test.objects.filter(classes=pk_classroom)
        testList = TestResponse.objects.filter(student=currentUser)
        testGiven = []
        for i in testList:
            testGiven.append(i.test.id)
        mssg = ''
        hideElement = ''

    if request.method == 'POST':
        if 'classCode' in request.POST:
            classroom = request.POST
            classCode = classroom['classCode']
            try:
                currentClassroom = Classroom.objects.get(class_code=classCode)
                student.classes.add(currentClassroom)
                currentClassroom.students.add(student)
                print('student added to class')
            except:
                print('Invalid class code.')
            return HttpResponseRedirect("/classroom/")

    return render(request,'paper/student.html',{'student':student,'tests':tests,'currentClass':classRoom,'testGiven':testGiven,'noClass':mssg,'hideElement':hideElement,'userAuthenticated':request.user.is_authenticated})

def test(request,pk_test):
    currentUser = int(request.user.username)
    testContent = Test.objects.get(id=pk_test)
    paperStr = testContent.test_paper
    paper = json.loads(paperStr)
    questions = paper['questions']

    student = Student.objects.get(id=currentUser)
    studentId = student.id
    testId = testContent.id

    mm = int(paper['correct']) * len(questions)
    testDetails = {'topic':testContent.topic,'wrong':paper['wrong'],'correct':paper['correct'],'mm':mm}
    if request.method == 'POST':
        paperResponse = request.POST
        marksObtained = 0
        answerData = []
        for i in questions:
            answer = i['answer']
            try:
                choice = paperResponse['qID-'+str(i['qid'])]
            except:
                choice = ''
            if choice == answer:
                status = 'Correct'
                marksObtained += int(paper['correct'])
            elif choice != answer and choice in ['A','B','C','D']:
                status = 'Wrong'
                marksObtained += int(paper['wrong'])
            else:
                status = 'Unanswered'
            ans = {'qid':i['qid'],'optionSelected':choice,'status':status}
            answerData.append(ans)
        
        answerData1 = json.dumps(answerData)
        formData = {'student':studentId,'test':testId,'score':marksObtained,'response':answerData1}
        form = TestResponseForm(formData)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect("/classroom/")

    return render(request, 'paper/test.html',{'questions':questions,'details':testDetails,'userAuthenticated':request.user.is_authenticated})

def viewTest(request,pk_test):
    currentUser = int(request.user.username)
    testContent = Test.objects.get(id=pk_test)
    paperStr = testContent.test_paper
    paper = json.loads(paperStr)
    questions = paper['questions']

    mm = int(paper['correct']) * len(questions)
    testDetails = {'topic':testContent.topic,'wrong':paper['wrong'],'correct':paper['correct'],'mm':mm}

    return render(request, 'paper/test.html',{'questions':questions,'details':testDetails,'submitBtnClass':'hide','userAuthenticated':request.user.is_authenticated})

def studentTestRespone(request,pk_test):
    currentUser = int(request.user.username)
    student = Student.objects.get(id=currentUser)
    test = Test.objects.get(id=pk_test)
    testResponse = TestResponse.objects.filter(student=student,test=test)
    testResponse = testResponse[0]
    paperResponseStr = testResponse.response
    paperResponse = json.loads(paperResponseStr)
    
    paperStr = test.test_paper
    paper = json.loads(paperStr)
    questions = paper['questions']
    for i in questions:
        for j in paperResponse:
            if i['qid'] == j['qid']:
                i['status'] = j['status']
                x = 'selectedOption' + j['optionSelected']
                i[x] = 'option-selected'
                y = 'correctOption' + i['answer']
                i[y] = 'answer-selected'
                if j['status'] == 'Correct':
                    i['correct'] = 'correct-q'
                elif j['status'] == 'Wrong':
                    i['incorrect'] = 'incorrect-q'
                else:
                    i['unanswered'] = 'unanswered-q'

            else:
                i['optionSelected'] = ''
                i['status'] = 'Unanswered'
    score = testResponse.score


    mm = int(paper['correct']) * len(questions)
    testDetails = {'topic':test.topic,'wrong':paper['wrong'],'correct':paper['correct'],'mm':mm,'score':score}

    return render(request,'paper/studentTestResponse.html',{'questions':questions,'details':testDetails,'userAuthenticated':request.user.is_authenticated})

def createTest(request,pk_classroom):
    currentUser = int(request.user.username)
    creator = Teacher.objects.get(id=currentUser)
    if request.method == 'POST':   
        data = request.POST
        classesId = data.getlist('classes')
        correct_marks = data['correct']
        wrong_marks = data['wrong']
        topic = data['topic']
        questions = []
        i = 1
        no = int((len(data)-4)/6)
        for i in range(1,no + 1):
            qId = i 
            strId = str(i)
            question = data['question-' + strId]
            optA = data[strId + '-A']
            optB = data[strId + '-B']
            optC = data[strId + '-C']
            optD = data[strId + '-D']
            answer = data['answer-' + strId]
            que = {'qid':qId,'question':question, 'options':{'A':optA,'B':optB,'C':optC,'D':optD},'answer':answer}
            questions.append(que)       
        paperData = {'correct':int(correct_marks),'wrong':int(wrong_marks),'questions': questions}
        paperData1 = json.dumps(paperData)
        formData = {'topic':topic,'creator':creator,'test_paper':paperData1}
        form = TestForm(formData)
        if form.is_valid():
            form.save()
            test = Test.objects.get(topic=topic)
            for i in classesId:
                classI = Classroom.objects.get(id=i)
                test.classes.add(classI)
            print("form sent")
            return HttpResponseRedirect("/classroom/")
    return render(request, 'paper/createTest.html',{'teacher':creator,'userAuthenticated':request.user.is_authenticated})

#Not used
def editTest(request,pk_test):
    currentUser = int(request.user.username)
    oldData = Test.objects.get(id=pk_test)
    oldPaper = oldData.test_paper
    oldTopic = oldData.topic
    oldPaper = json.loads(oldPaper)
    oldQuestions = oldPaper['questions']
    oldCorrect = oldPaper['correct']
    oldWrong = oldPaper['wrong']

    teacher = Teacher.objects.get(id=currentUser)
    creator = oldData.creator
    if request.method == 'POST':   
        data = request.POST
        classesId = data.getlist('classes')
        correct_marks = data['correct']
        wrong_marks = data['wrong']
        topic = data['topic']
        try:
            Test.objects.get(topic=topic)
            topic += '(edited)'
        except:
            pass
        questions = []
        i = 1
        no = int((len(data)-4)/6)
        for i in range(1,no + 1):
            qId = i 
            strId = str(i)
            question = data['question-' + strId]
            optA = data[strId + '-A']
            optB = data[strId + '-B']
            optC = data[strId + '-C']
            optD = data[strId + '-D']
            answer = data['answer-' + strId]
            que = {'qid':qId,'question':question, 'options':{'A':optA,'B':optB,'C':optC,'D':optD},'answer':answer}
            questions.append(que)       
        paperData = {'correct':int(correct_marks),'wrong':int(wrong_marks),'questions': questions}
        paperData1 = json.dumps(paperData)
        formData = {'topic':topic, 'creator':creator, 'test_paper':paperData1}
        form = TestForm(formData)
        if form.is_valid():
            form.save()
            test = Test.objects.get(topic=topic)
            for i in classesId:
                classI = Classroom.objects.get(id=i)
                test.classes.add(classI)
            print("form sent")
            return HttpResponseRedirect(f"/classroom/")

    return render(request, 'paper/editTest.html',{'teacher':teacher,'oldQuestions':oldQuestions,'oldTopic':oldTopic,'oldCorrect':oldCorrect,'oldWrong':oldWrong,'userAuthenticated':request.user.is_authenticated})

def response(request,pk_classroom,pk_test):
    currentUser = int(request.user.username)
    testId = Test.objects.get(id=pk_test)
    classRoom = Classroom.objects.get(id=pk_classroom)
    topic = testId.topic
    responseList = TestResponse.objects.filter(test=pk_test).order_by('-score').values('student','score')

    j = 1
    for i in responseList:
        if Student.objects.get(id=i['student']) in classRoom.students.all():
            i['rank'] = j
            studentId = i['student']
            i['student'] = Student.objects.get(id=studentId).name
            i['id'] = studentId
            j += 1

    testResponse = TestResponse.objects.filter(test=testId)
    paperStr = testId.test_paper
    paper = json.loads(paperStr)
    
    graphs = {}
    if len(responseList) > 0:
        graphs['attemptedGraph'] = attemptedGraph(classRoom,responseList)
        graphs['boxPlot'] = boxPlot(responseList)
        graphs['questionWiseBarGraph'] = questionWiseBarGraph(paper,testResponse)
    else:
        graphs['attemptedGraph'] = ''
        graphs['boxPlot'] = ''
        graphs['questionWiseBarGraph'] = ''

    return render(request, 'paper/response.html',{'teacherId':currentUser,'testId':pk_test,'topic':topic,'currentClass':classRoom,'responseList':responseList,'graphs':graphs,'userAuthenticated':request.user.is_authenticated})

def export(request,pk_classroom,pk_test):
    currentUser = int(request.user.username)
    testId = Test.objects.get(id=pk_test)
    classRoom = Classroom.objects.get(id=pk_classroom)
    topic = testId.topic
    responseList = TestResponse.objects.filter(test=pk_test).order_by('-score').values('student','score')

    j = 1
    for i in responseList:
        if Student.objects.get(id=i['student']) in classRoom.students.all():
            i['rank'] = j
            studentId = i['student']
            i['student'] = Student.objects.get(id=studentId).name
            i['id'] = studentId
            j += 1
       
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['rank','student Id','name','marks'])
    for i in responseList:
        if 'id' in i.keys():
            writer.writerow([i['rank'],i['id'],i['student'],i['score']])
    response['Content-Disposition'] = f'attachment; filename="{topic}({classRoom.class_name}).csv"'
    return response

def classroom(request,pk_classroom):
    currentUser = int(request.user.username)
    classRoom = Classroom.objects.get(id=pk_classroom)
    if currentUser // 100000 == 1:
        isTeacher = True
        teacher = Teacher.objects.get(id=currentUser)
        if request.method == 'POST':
            if 'leaveClassroom' in request.POST:
                print(request.POST)
                try:
                    classRoom.teachers.remove(teacher)
                    teacher.classes.remove(classRoom)
                except:
                    print('Unable to leave classroom.')
                return HttpResponseRedirect("/classroom/")
            else:    
                data = request.POST
                print(data)
                for key, value in data.items(): 
                    if value == '\uf00d': 
                        studentId = key.replace("student-","")
                try:
                    student = Student.objects.get(id=studentId)
                    classRoom.students.remove(student)
                    print(student, ' removed')
                except:
                    print('Unable to remove student')
            return HttpResponseRedirect(f"/classroom/{classRoom.id}/members")

    elif currentUser // 100000 == 2:
        isTeacher = False
        student = Student.objects.get(id=currentUser)
        if request.method == 'POST':
            if 'leaveClassroom' in request.POST:
                print(request.POST)
                try:
                    classRoom.students.remove(student)
                    student.classes.remove(classRoom)
                except:
                    print('Unable to leave classroom.')
                return HttpResponseRedirect("/classroom/")

    return render(request, 'paper/classroom.html',{'classroom':classRoom,'teacher':isTeacher,'userAuthenticated':request.user.is_authenticated})

def leaveClassroom(request,pk_classroom):
    currentUser = int(request.user.username)
    classRoom = Classroom.objects.get(id=pk_classroom)

    if currentUser // 100000 == 1:
        teacher = Teacher.objects.get(id=currentUser)
        classRoom.teachers.remove(teacher)
        teacher.classes.remove(classRoom)
    elif currentUser // 100000 == 2:
        student = Student.objects.get(id=currentUser)
        classRoom.students.remove(student)
        student.classes.remove(classRoom)

    return HttpResponseRedirect("/classroom/")

def about(request):
    return render(request, 'paper/about.html',{'userAuthenticated':request.user.is_authenticated})

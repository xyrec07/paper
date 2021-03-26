import random

def switch_view(first_view, second_view, third_view):
    def inner_view(request, *args, **kwargs):
        try:
            if request.user.username[0] == '2':
                return first_view(request, *args, **kwargs)
            elif request.user.username[0] == '1':
                return second_view(request, *args, **kwargs)
        except:
            return third_view(request, *args, **kwargs)
    return inner_view

def generateClassCode(classCodeList):
    code = ''
    for i in range(0,5):
	    code += chr(random.randint(65, 90)) 
    if code in classCodeList:
        generateClassCode()
    elif code != '':  
        return code


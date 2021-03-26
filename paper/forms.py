from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','username','password1','password2')


class TestForm(ModelForm):
    class Meta:
        model = Test
        exclude = ()

class TestResponseForm(ModelForm):
    class Meta:
        model = TestResponse
        exclude = ()
    

class ClassroomForm(ModelForm):
    class Meta:
        model = Classroom
        exclude = ()
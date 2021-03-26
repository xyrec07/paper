from django.contrib import admin

# Register your models here.

from .models import *

class TeacherAdmin(admin.ModelAdmin):
    fields = ['id','name','classes']
    readonly_fields = ('id',)

class TestAdmin(admin.ModelAdmin):
    fields = ['id','topic','classes','creator','test_paper']
    readonly_fields = ('id',)

class TestResponseAdmin(admin.ModelAdmin):
    fields = ['student', 'test','score','response']
    # readonly_fields = fields

class ClassroomAdmin(admin.ModelAdmin):
    fields = ['id','class_name','teachers','students','class_code']
    readonly_fields = ('id',)


admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student)
admin.site.register(Test, TestAdmin)
admin.site.register(TestResponse, TestResponseAdmin)
admin.site.register(Classroom, ClassroomAdmin)


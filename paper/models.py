from django.db import models

class Classroom(models.Model):
    class_name = models.CharField(max_length=200)
    teachers = models.ManyToManyField('Teacher', blank=True)  
    students = models.ManyToManyField('Student', blank=True)   
    class_code = models.CharField(max_length=5)
    def __str__(self):
        return str(self.class_code) + '-' + str(self.class_name)
    class Meta:
        unique_together = (("id","class_code"),)

class Teacher(models.Model):
    name = models.CharField(max_length=200, null=True)
    classes = models.ManyToManyField(Classroom, blank=True)  
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=200)
    classes = models.ManyToManyField(Classroom, blank=True)  
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return self.name

class Test(models.Model):
    topic = models.CharField(max_length=200)
    classes = models.ManyToManyField(Classroom, blank=True)
    creator = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    test_paper = models.TextField(null=True)    #complete paper stored as JSON string
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return str(self.topic)

class TestResponse(models.Model):
    student = models.ForeignKey(Student, related_name='Student', null=True, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, related_name='Test', null=True, on_delete=models.CASCADE)
    score = models.IntegerField(null=True)
    response = models.TextField(null=True)   #answers stored as JSON string
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return str(self.test) + '-' + str(self.student)
    class Meta:
        unique_together = (("student_id", "test_id"),)






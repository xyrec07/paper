from django.urls import path, re_path
from . import views
from .modules import switch_view

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.home, name='signup'),
    path('login/', views.home, name='login'),
    path('logout/', views.logoutUser, name='logout'),

    path('classroom/', switch_view(views.student,views.teacher,views.loginRequired)),
    path('classroom/<str:pk_classroom>/', switch_view(views.student,views.teacher,views.loginRequired)),
    path('classroom/<str:pk_classroom>/leave/', views.leaveClassroom), 

    # test create and edit 
    path('classroom/<str:pk_classroom>/create/', views.createTest),
    path('classroom/<str:pk_classroom>/edit/<str:pk_test>/', views.editTest),

    # test respone
    path('classroom/test/<str:pk_test>/response', views.studentTestRespone),

    # student response and response download 
    path('classroom/<str:pk_classroom>/response/<str:pk_test>/', views.response),
    path('classroom/<str:pk_classroom>/response/<str:pk_test>/download', views.export),

    # classroom
    path('classroom/<str:pk_classroom>/members',views.classroom),

    # tests
    path('classroom/test/<str:pk_test>/',views.test),
    path('classroom/test/<str:pk_test>/view/',views.viewTest),

    path('about/',views.about),
]
from django.urls import path
from django.contrib.auth import views as auth_views
from app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),

    # Instructor
    path('instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/create/', views.create_course, name='create_course'),
    path('instructor/course/<int:course_id>/add_module/', views.add_module, name='add_module'),
    path('instructor/module/<int:module_id>/edit/', views.edit_module, name='edit_module'),
    path('instructor/module/<int:module_id>/add_lesson/', views.add_lesson, name='add_lesson'),
    path('instructor/lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('instructor/course/<int:course_id>/edit/', views.instructor_edit_course, name='instructor_edit_course'),

    # Student
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('course/<int:course_id>/', views.view_course, name='view_course'),
    path('course/<int:course_id>/classroom/', views.classroom_view, name='classroom_view'),
    path('course/<int:course_id>/classroom/<int:lesson_id>/',views.classroom_view, name='classroom_view'),


    # Extras

    # Mark as complete
    path('lesson/<int:course_id>/<int:lesson_id>', views.mark_lesson_complete, name='mark_lesson_complete'),

    path('zoom/<int:course_id>/', views.zoom_classroom, name='zoom_classroom'),
]

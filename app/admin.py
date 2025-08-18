
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Course, Module, Lesson, Quiz, Enrollment, StudentProgress

# Custom User Admin to show instructor status
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'is_instructor')
    list_filter = ('is_staff', 'is_active', 'is_instructor')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_instructor',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_instructor',)}),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'is_published')
    list_filter = ('is_published', 'instructor')
    search_fields = ('title', 'instructor__username')
    ordering = ('title',)


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'available_after_days')
    list_filter = ('course',)
    search_fields = ('title',)
    ordering = ('course', 'order')
    inlines = []


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order')
    list_filter = ('module',)
    search_fields = ('title',)
    ordering = ('module', 'order')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'question')
    search_fields = ('question',)
    list_filter = ('lesson',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_on')
    list_filter = ('course', 'enrolled_on')
    search_fields = ('student__username', 'course__title')
    ordering = ('-enrolled_on',)


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('student__username', 'lesson__title')
    ordering = ('-completed_at',)

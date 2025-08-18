from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from .models import Course, Module, Lesson, Enrollment, StudentProgress
from django.template.loader import render_to_string

from .forms import CustomUserCreationForm
from django.contrib.auth import login


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # Determine if user is instructor
            user.is_instructor = form.cleaned_data.get("is_instructor") == "True"
            user.save()

            login(request, user)

            # Redirect based on role
            if user.is_instructor:
                return redirect("instructor_dashboard")
            else:
                return redirect("student_dashboard")
    else:
        form = CustomUserCreationForm()

    return render(request, "auth/register.html", {"form": form})


def home(request):
    category = request.GET.get("category")
    course_type = request.GET.get("course_type")

    courses = Course.objects.all()

    if category and category != "all":
        courses = courses.filter(category__iexact=category)

    if course_type and course_type != "all":
        courses = courses.filter(course_type__iexact=course_type)

    # Show only 6 courses
    courses = courses[:6]

    categories = Course.objects.values_list("category", flat=True).distinct()
    course_types = Course.COURSE_TYPE_CHOICES

    return render(request, "home.html", {
        "courses": courses,
        "categories": categories,
        "course_types": course_types,
        "selected_category": category,
        "selected_course_type": course_type
    })


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    total_modules = course.modules.count()
    total_lessons = sum(module.lessons.count() for module in course.modules.all())

    return render(request, 'course_detail.html', {'course': course,    'total_modules': total_modules,
    'total_lessons': total_lessons,
})

def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'lesson_detail.html', {'lesson': lesson})



# Instructor Dashboard
@login_required
def instructor_dashboard(request):
    if not request.user.is_instructor:
        return redirect('student_dashboard')
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'instructor/dashboard.html', {'courses': courses})

# Create Course
@login_required
def create_course(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        thmb = request.POST.get('thmb')
        cover_url = request.POST.get('cover_url')
        category = request.POST.get('category')
        course_type = request.POST.get('course_type')
        description = request.POST.get('description')
        price = request.POST.get('price') or 0.00
        is_free = request.POST.get('is_free') == 'on'

        course = Course.objects.create(
            title=title,
            thmb=thmb,
            cover_url=cover_url,
            category=category,
            course_type=course_type,
            description=description,
            price=price,
            is_free=is_free,
            instructor=request.user,
            created_at=timezone.now(),
            is_published=False  # Default draft mode
        )
        return redirect('instructor_dashboard')

    return render(request, 'instructor/create_course.html')


# Add Module
@login_required
def add_module(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        order = request.POST.get('order', '1')
        available_after_days = request.POST.get('available_after_days', '0')
        if title:
            module = Module.objects.create(
                course=course,
                title=title,
                order=int(order),
                available_after_days=int(available_after_days)
            )
            return redirect('instructor_edit_course', course_id=course.id)
        else:
            error = "Title is required."
    else:
        error = None
    return render(request, 'instructor/add_module.html', {'course': course, 'error': error})

# Edit Module
@login_required
def edit_module(request, module_id):
    module = get_object_or_404(Module, id=module_id, course__instructor=request.user)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        order = request.POST.get('order', '1')
        available_after_days = request.POST.get('available_after_days', '0')
        if title:
            module.title = title
            module.order = int(order)
            module.available_after_days = int(available_after_days)
            module.save()
            return redirect('instructor_edit_course', course_id=module.course.id)
        else:
            error = "Title is required."
    else:
        error = None
    return render(request, 'instructor/edit_module.html', {'module': module, 'error': error})

# Add Lesson
@login_required
def add_lesson(request, module_id):
    module = get_object_or_404(Module, id=module_id, course__instructor=request.user)
    error = None

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        video_url = request.POST.get('video_url', '').strip()
        notes = request.POST.get('notes', '').strip()
        order = request.POST.get('order', '1')
        available_after_days = request.POST.get('available_after_days', '0').strip()

        if title:
            Lesson.objects.create(
                module=module,
                title=title,
                video_url=video_url,
                notes=notes,
                order=int(order),
                available_after_days=int(available_after_days),
            )
            return redirect('instructor_edit_course', course_id=module.course.id)
        else:
            error = "Title is required."

    return render(request, 'instructor/add_lesson.html', {
        'module': module,
        'error': error,
    })

@login_required
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course__instructor=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        video_url = request.POST.get('video_url', '').strip()
        notes = request.POST.get('notes', '').strip()
        order = request.POST.get('order', '1')
        available_after_days = request.POST.get('available_after_days', '0')  # <-- Add this

        if title:
            lesson.title = title
            lesson.video_url = video_url
            lesson.notes = notes
            lesson.order = int(order)
            lesson.available_after_days = int(available_after_days)  # <-- Add this
            lesson.save()
            return redirect('instructor_edit_course', course_id=lesson.module.course.id)
        else:
            error = "Title is required."
    else:
        error = None

    return render(request, 'instructor/edit_lesson.html', {'lesson': lesson, 'error': error})


@login_required
def instructor_edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    modules = course.modules.order_by('order').all()

    # For each module, fetch lessons ordered
    modules_with_lessons = []
    for module in modules:
        lessons = module.lessons.order_by('order').all()
        modules_with_lessons.append((module, lessons))

    return render(request, 'instructor/edit_course.html', {
        'course': course,
        'modules_with_lessons': modules_with_lessons,
    })





# Student Dashboard
@login_required
def student_dashboard(request):
    user=request.user
    if user.is_instructor == True:
        return redirect('instructor_dashboard')
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'student/dashboard.html', {'enrollments': enrollments})


# View Course Modules (Drip Content)
@login_required
def view_course(request, course_id):
    enrollment = get_object_or_404(Enrollment, course_id=course_id, student=request.user)
    available_modules = enrollment.course.module_set.filter(
        available_after_days__lte=(timezone.now() - enrollment.enrolled_on).days
    )
    return render(request, 'student/view_course.html', {'enrollment': enrollment, 'modules': available_modules})







# Zoom Meeting Info (dummy view)
@login_required
def zoom_classroom(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    zoom_link = "https://zoom.us/j/1234567890"  # Replace with dynamic logic
    return render(request, 'student/zoom_classroom.html', {'course': course, 'zoom_link': zoom_link})


from django.utils import timezone


@login_required
def classroom_view(request, course_id, lesson_id=None):
    course = get_object_or_404(Course, id=course_id)
    modules = Module.objects.filter(course=course).prefetch_related('lessons').all()
    enrollment = Enrollment.objects.filter(student=request.user,course=course_id)
    if not enrollment:
        return redirect('home')

    all_lessons = Lesson.objects.filter(module__course=course).order_by('module__id', 'order')  # Add 'order' if available

    selected_lesson = all_lessons.first()

    if lesson_id:
        selected_lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)




    # ✅ FIXED: Correct filtering by course via related fields
    completed_lessons = StudentProgress.objects.filter(
        student=request.user,
        lesson__module__course=course,
                completed=True

    ).values_list('lesson_id', flat=True)

 

    is_completed = False
    if selected_lesson:
        is_completed = selected_lesson.id in completed_lessons


    # Count total vs completed lessons
    all_lessons = Lesson.objects.filter(module__course=course)
    all_completed = all_lessons.count() == len(completed_lessons)

    # 🔥 Related courses in the same category (excluding current course)
    related_courses = Course.objects.filter(category=course.category).exclude(id=course.id)[:4]


    return render(request, 'classroom.html', {
        'course': course,
        'modules': modules,
        'selected_lesson': selected_lesson,
        'completed_lessons': list(completed_lessons),
        "is_completed":is_completed,
        'all_completed': all_completed,
        'related_courses': related_courses,  # 👈 pass to template


    })


@login_required
def mark_lesson_complete(request, course_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    progress, created = StudentProgress.objects.get_or_create(student=request.user, lesson=lesson)

    if not progress.completed:
        progress.completed = True
        progress.save()

    return redirect('classroom_view', course_id=course_id)




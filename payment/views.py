import stripe
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404, render
from app.models import Course, Enrollment

stripe.api_key = settings.STRIPE_SECRET_KEY

def buy_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # If already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return redirect('classroom_view', course_id=course.id)

    # Free course - auto enroll
    if course.is_free or course.price == 0:
        Enrollment.objects.create(student=request.user, course=course)
        return redirect('classroom_view', course_id=course.id)

    # Stripe Checkout
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(course.price * 100),
                'product_data': {
                    'name': course.title,
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(f'/payment-success/{course.id}/'),
        cancel_url=request.build_absolute_uri(f'/course/{course.id}/'),
        customer_email=request.user.email
    )

    return redirect(checkout_session.url)

def payment_success(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Enroll student
    Enrollment.objects.get_or_create(student=request.user, course=course)

    # Add course price to instructor balance
    instructor = course.instructor
    instructor.balance += course.price
    instructor.save()

    return render(request, 'payment_success.html', {'course': course})



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PayoutRequest
from django.utils import timezone
from decimal import Decimal

@login_required
def payout_request_view(request):
    instructor = request.user

    if request.method == "POST":
        amount = Decimal(request.POST.get('amount'))  # convert POST value to Decimal
        try:
           amount = Decimal(request.POST.get('amount'))  # convert POST value to Decimal
        except (ValueError, TypeError):
            messages.error(request, "Enter a valid amount.")
            return redirect('payout_request')

        if amount <= 0:
            messages.error(request, "Amount must be greater than zero.")
        elif amount > instructor.balance:
            messages.error(request, "Cannot request more than available balance.")
        else:
            PayoutRequest.objects.create(instructor=instructor, amount=amount)
            instructor.balance -= amount
            instructor.save()
            messages.success(request, "Payout request submitted successfully!")

        return redirect('payout_request')

    # Show payout requests history
    requests = PayoutRequest.objects.filter(instructor=instructor).order_by('-requested_at')

    return render(request, "instructor/payout_request.html", {
        "balance": instructor.balance,
        "requests": requests,
    })



from django.core.paginator import Paginator
from django.db.models import Q
from app.models import User

def all_courses(request):
    courses = Course.objects.all()

    # Search
    query = request.GET.get('q')
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )

    # Filters
    course_type = request.GET.get('course_type')
    if course_type:
        courses = courses.filter(course_type=course_type)

    is_free = request.GET.get('is_free')
    if is_free == '1':
        courses = courses.filter(is_free=True)
    elif is_free == '0':
        courses = courses.filter(is_free=False)

    # Pagination
    paginator = Paginator(courses, 9)  # 9 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'all_courses.html', {
        'page_obj': page_obj,
        'query': query,
        'course_type': course_type,
        'is_free': is_free,
    })

from django.shortcuts import render
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from app.models import User, Course

def about(request):
    # Search instructors
    query = request.GET.get('q', '')
    instructors = User.objects.filter(is_instructor=True)
    if query:
        instructors = instructors.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    # Filters for courses
    course_type = request.GET.get('course_type', '')
    is_free = request.GET.get('is_free', '')

    course_filter = Q()
    if course_type:
        course_filter &= Q(course_type=course_type)
    if is_free == '1':
        course_filter &= Q(is_free=True)
    elif is_free == '0':
        course_filter &= Q(is_free=False)

    instructors = instructors.prefetch_related(
        Prefetch('course_set', queryset=Course.objects.filter(course_filter).order_by('-created_at'))
    )

    # Pagination per instructor: 6 courses per page
    instructor_courses_pages = {}
    for instructor in instructors:
        paginator = Paginator(list(instructor.course_set.all()), 6)
        page_number = request.GET.get(f'page_{instructor.id}', 1)
        instructor_courses_pages[instructor.id] = paginator.get_page(page_number)

    return render(request, 'about.html', {
        'instructors': instructors,
        'query': query,
        'course_type': course_type,
        'is_free': is_free,
        'instructor_courses_pages': instructor_courses_pages
    })


from django.shortcuts import get_object_or_404, redirect


def delete_cus(request, id):
    cus = get_object_or_404(Course, id=id)
    cus.delete()
    return redirect("instructor_dashboard")

    
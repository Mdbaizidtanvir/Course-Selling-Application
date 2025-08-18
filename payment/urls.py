from django.urls import path
from payment import views

urlpatterns = [
    path('buy/<int:course_id>/', views.buy_course, name='buy_course'),
    path('payment-success/<int:course_id>/', views.payment_success, name='payment_success'),
    path('instructor/payout-request/', views.payout_request_view, name='payout_request'),
    path('all_courses',views.all_courses,name="all_courses"),
    path('about',views.about,name="about"),
    path("delete/<int:id>/", views.delete_cus, name="delete_cus"),

]

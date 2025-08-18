from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone  # ✅ Add this
from cloudinary.models import CloudinaryField

class User(AbstractUser):
    is_instructor = models.BooleanField(default=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,blank=True)
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)  # Stripe Connect Account ID


from django.utils import timezone



class Course(models.Model):
    COURSE_TYPE_CHOICES = [
        ("BEGINNER", "Beginner"),
        ("INTERMEDIATE", "Intermediate"),
        ("ADVANCED", "Advanced"),
    ]

    title = models.CharField(max_length=200)
    thmb=models.URLField(max_length=90000,blank=True)
    cover_url = models.URLField(max_length=90000,blank=True)
    category = models.CharField(max_length=900, blank=True)
    course_type = models.CharField(max_length=50, choices=COURSE_TYPE_CHOICES, blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)  # ✅ Added created date

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,blank=True)
    is_free = models.BooleanField(default=False)


    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course,related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField()
    available_after_days = models.IntegerField(default=0)  # Days after enrollment


class Lesson(models.Model):
    module = models.ForeignKey(Module,related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    available_after_days = models.IntegerField(default=0)  # Days after enrollment


class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    question = models.TextField()
    correct_answer = models.CharField(max_length=200)
    choices = models.JSONField()




class StudentProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False,blank=True)




class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')  # 🚫 prevent duplicates
    
    def available_modules(self):
        now = timezone.now()
        return self.course.modules.filter(
            available_after_days__lte=(now - self.enrolled_on).days
        )

class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title} Certificate"

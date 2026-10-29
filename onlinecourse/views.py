"""Course browsing, enrollment and assessment views."""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic
from django.views.decorators.http import require_http_methods, require_POST

from .models import Choice, Course, Enrollment, Submission


@require_http_methods(["GET", "POST"])
def registration_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("psw", "")
        if not username or len(password) < 8:
            context["message"] = "Enter a username and a password of at least eight characters."
        elif User.objects.filter(username=username).exists():
            context["message"] = "User already exists."
        else:
            user = User.objects.create_user(
                username=username, password=password,
                first_name=request.POST.get("firstname", ""),
                last_name=request.POST.get("lastname", ""),
            )
            login(request, user)
            return redirect("onlinecourse:index")
    return render(request, "onlinecourse/user_registration_bootstrap.html", context)


@require_http_methods(["GET", "POST"])
def login_request(request):
    context = {}
    if request.method == "POST":
        user = authenticate(
            request, username=request.POST.get("username", ""),
            password=request.POST.get("psw", ""),
        )
        if user is not None:
            login(request, user)
            return redirect("onlinecourse:index")
        context["message"] = "Invalid username or password."
    return render(request, "onlinecourse/user_login_bootstrap.html", context)


@require_POST
def logout_request(request):
    logout(request)
    return redirect("onlinecourse:index")


def check_if_enrolled(user, course):
    return user.is_authenticated and Enrollment.objects.filter(user=user, course=course).exists()


class CourseListView(generic.ListView):
    template_name = "onlinecourse/course_list_bootstrap.html"
    context_object_name = "course_list"

    def get_queryset(self):
        courses = list(Course.objects.order_by("-total_enrollment")[:10])
        for course in courses:
            course.is_enrolled = check_if_enrolled(self.request.user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = "onlinecourse/course_details_bootstrap.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_enrolled"] = check_if_enrolled(self.request.user, self.object)
        return context


@login_required
@require_POST
@transaction.atomic
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    _, created = Enrollment.objects.get_or_create(
        user=request.user, course=course, defaults={"mode": "honor"},
    )
    if created:
        Course.objects.filter(pk=course.pk).update(total_enrollment=F("total_enrollment") + 1)
    return redirect("onlinecourse:course_details", pk=course.pk)


def extract_answers(request):
    """Collect all checked choices, including multiple answers per question."""
    return {
        int(value)
        for key in request.POST if key.startswith("choice_")
        for value in request.POST.getlist(key)
    }


@login_required
@require_POST
@transaction.atomic
def submit(request, course_id):
    """Validate selected choices and save a submission for the enrolled learner."""
    course = get_object_or_404(Course, pk=course_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    try:
        selected_ids = extract_answers(request)
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Invalid answer selection.")

    choices = list(Choice.objects.filter(pk__in=selected_ids, question__course=course))
    if {choice.pk for choice in choices} != selected_ids:
        return HttpResponseBadRequest("A selected answer does not belong to this course.")

    submission = Submission.objects.create(enrollment=enrollment)
    submission.choices.set(choices)
    return redirect("onlinecourse:show_exam_result", course_id=course.pk, submission_id=submission.pk)


@login_required
def show_exam_result(request, course_id, submission_id):
    """Calculate a weighted score and show results only to the submission owner."""
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(
        Submission, pk=submission_id,
        enrollment__course=course, enrollment__user=request.user,
    )
    selected_ids = set(submission.choices.values_list("pk", flat=True))
    total = 0
    earned = 0
    results = []
    for question in course.question_set.prefetch_related("choice_set"):
        correct = question.is_get_score(selected_ids)
        total += question.grade
        if correct:
            earned += question.grade
        results.append({
            "question": question,
            "correct": correct,
            "earned": question.grade if correct else 0,
            "choices": [
                {"choice": choice, "selected": choice.pk in selected_ids}
                for choice in question.choice_set.all()
            ],
        })
    grade = round(100 * earned / total, 2) if total else 0
    return render(request, "onlinecourse/exam_result_bootstrap.html", {
        "course": course, "submission": submission, "results": results,
        "grade": grade, "earned": earned, "total": total,
        "passed": total > 0 and grade >= 80,
    })

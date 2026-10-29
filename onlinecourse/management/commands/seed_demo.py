"""Create local sample content and an administrator for the project demo."""

import json
from pathlib import Path
import secrets

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from onlinecourse.models import Choice, Course, Enrollment, Instructor, Learner, Lesson, Question


class Command(BaseCommand):
    help = "Create an example course and save local-only demo credentials."

    @transaction.atomic
    def handle(self, *args, **options):
        credential_path = Path(settings.BASE_DIR) / ".demo-credentials.json"
        if credential_path.exists():
            credentials = json.loads(credential_path.read_text(encoding="utf-8"))
        else:
            credentials = {"username": "admin", "password": secrets.token_urlsafe(24)}
            credential_path.write_text(json.dumps(credentials, indent=2), encoding="utf-8")
        user, created = User.objects.get_or_create(
            username=credentials["username"],
            defaults={"first_name": "Student", "is_staff": True, "is_superuser": True},
        )
        if created:
            user.set_password(credentials["password"])
            user.save()
        instructor, _ = Instructor.objects.get_or_create(user=user, defaults={"total_learners": 1})
        Learner.objects.get_or_create(user=user, defaults={"social_link": "https://github.com/wexer02"})
        course, _ = Course.objects.get_or_create(
            name="Django Application Development",
            defaults={
                "description": "Learn Django models, views, templates and assessment workflows.",
                "image": "course_images/django.png", "total_enrollment": 1,
            },
        )
        course.instructors.add(instructor)
        Enrollment.objects.get_or_create(user=user, course=course, defaults={"mode": "honor"})
        lessons = [
            ("Models and databases", "Django models describe database records. The ORM lets you create, retrieve and update records using Python."),
            ("Views and templates", "Views handle HTTP requests and return responses. Templates render course information and exam forms."),
        ]
        for order, (title, content) in enumerate(lessons):
            Lesson.objects.get_or_create(course=course, order=order, defaults={"title": title, "content": content})
        questions = [
            ("What does a Django view return?", 40, [
                ("An HTTP response", True), ("A database table", False), ("A CSS stylesheet only", False),
            ]),
            ("Which Django component maps Python models to database records?", 30, [
                ("The ORM", True), ("The template engine", False), ("The URL path converter", False),
            ]),
            ("Which are HTTP request methods? Select all correct answers.", 30, [
                ("GET", True), ("POST", True), ("CSS", False),
            ]),
        ]
        for text, grade, choices in questions:
            question, _ = Question.objects.get_or_create(
                course=course, question_text=text, defaults={"grade": grade},
            )
            for text, correct in choices:
                Choice.objects.get_or_create(question=question, choice_text=text, defaults={"is_correct": correct})
        self.stdout.write(self.style.SUCCESS(f"Demo course ready: /onlinecourse/{course.pk}/"))
        self.stdout.write(f"Local credentials saved in {credential_path.name}; this file is ignored by Git.")

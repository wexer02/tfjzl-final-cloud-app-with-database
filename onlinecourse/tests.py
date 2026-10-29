"""Assessment scoring and access-control regression tests."""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Choice, Course, Enrollment, Question, Submission


class ExamTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("learner", password="test-password")
        self.other = User.objects.create_user("other", password="test-password")
        self.course = Course.objects.create(name="Django basics", description="Learn Django")
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course)
        self.question = Question.objects.create(course=self.course, question_text="Pick two", grade=2)
        self.correct = Choice.objects.create(question=self.question, choice_text="A", is_correct=True)
        self.second = Choice.objects.create(question=self.question, choice_text="B", is_correct=True)
        self.wrong = Choice.objects.create(question=self.question, choice_text="C", is_correct=False)
        self.url = reverse("onlinecourse:submit", args=[self.course.pk])
        self.client.force_login(self.user)

    def submit(self, ids):
        return self.client.post(self.url, {f"choice_{self.question.pk}": ids}, follow=True)

    def test_exact_correct_choices_score_full_marks(self):
        response = self.submit([self.correct.pk, self.second.pk])
        self.assertEqual(response.context["grade"], 100)
        self.assertContains(response, "Congratulations")
        self.assertEqual(Submission.objects.get().choices.count(), 2)

    def test_partial_or_extra_choices_score_zero(self):
        for ids in ([self.correct.pk], [self.correct.pk, self.second.pk, self.wrong.pk], []):
            with self.subTest(ids=ids):
                self.assertEqual(self.submit(ids).context["grade"], 0)

    def test_weighted_score(self):
        q = Question.objects.create(course=self.course, question_text="One more", grade=3)
        Choice.objects.create(question=q, choice_text="D", is_correct=True)
        self.assertEqual(self.submit([self.correct.pk, self.second.pk]).context["grade"], 40)

    def test_eighty_percent_is_a_pass(self):
        self.question.grade = 4
        self.question.save()
        q = Question.objects.create(course=self.course, question_text="Last point", grade=1)
        Choice.objects.create(question=q, choice_text="Answer", is_correct=True)
        response = self.submit([self.correct.pk, self.second.pk])
        self.assertEqual(response.context["grade"], 80)
        self.assertTrue(response.context["passed"])

    def test_repeated_enrollment_does_not_create_duplicates(self):
        url = reverse("onlinecourse:enroll", args=[self.course.pk])
        self.client.post(url)
        self.client.post(url)
        self.assertEqual(Enrollment.objects.filter(user=self.user, course=self.course).count(), 1)

    def test_unenrolled_learner_cannot_see_exam(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("onlinecourse:course_details", args=[self.course.pk]))
        self.assertNotContains(response, 'name="choice_')
        self.assertContains(response, "Enroll to take the exam")

    def test_foreign_course_choice_is_rejected(self):
        course = Course.objects.create(name="Other", description="Other course")
        q = Question.objects.create(course=course, question_text="Other", grade=1)
        choice = Choice.objects.create(question=q, choice_text="Other", is_correct=True)
        self.assertEqual(self.client.post(self.url, {"choice_x": choice.pk}).status_code, 400)
        self.assertFalse(Submission.objects.exists())

    def test_invalid_choice_is_rejected(self):
        for value in ("invalid", "999999"):
            self.assertEqual(self.client.post(self.url, {"choice_x": value}).status_code, 400)
        self.assertFalse(Submission.objects.exists())

    def test_submission_requires_post(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_submission_requires_authentication(self):
        self.client.logout()
        self.assertEqual(self.client.post(self.url).status_code, 302)

    def test_submission_requires_enrollment(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(self.url).status_code, 404)

    def test_another_user_cannot_view_results(self):
        submission = Submission.objects.create(enrollment=self.enrollment)
        self.client.force_login(self.other)
        url = reverse("onlinecourse:show_exam_result", args=[self.course.pk, submission.pk])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_result_must_belong_to_course(self):
        submission = Submission.objects.create(enrollment=self.enrollment)
        other_course = Course.objects.create(name="Other", description="Other")
        url = reverse("onlinecourse:show_exam_result", args=[other_course.pk, submission.pk])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_empty_exam_does_not_pass(self):
        self.course.question_set.all().delete()
        response = self.submit([])
        self.assertEqual(response.context["grade"], 0)
        self.assertNotContains(response, "Congratulations")

    def test_csrf_is_required(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(self.url).status_code, 403)

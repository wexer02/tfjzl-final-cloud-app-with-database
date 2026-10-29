# Online Course Assessment Implementation Plan

**Goal:** Complete the seven grading tasks with a working assessment flow.
**Architecture:** Extend the official starter's models, admin, views and templates.
Use Django authentication, SQLite and server-side grading of stored submissions.
**Tech stack:** Python 3.13, Django 5.2, Pillow, Bootstrap 4.5.2.
**Spec:** docs/superpowers/specs/2026-10-29-course-assessment-design.md

## Global constraints
- Public answer files: models.py, admin.py, course_details_bootstrap.html,
  views.py and urls.py under onlinecourse/.
- Screenshots: 03-admin-site.png and 07-final.png, captured from the running app.
- No credentials or database in the public repository.

## 1. Models and admin
- [x] Add regression tests in onlinecourse/tests.py for exact-match scoring,
  weighted percentages, invalid choices, enrollment and result ownership.
- [x] Run `.venv/Scripts/python.exe manage.py test` and confirm missing-model failure.
- [x] Define Question, Choice and Submission in onlinecourse/models.py and
  generate initial migrations with `manage.py makemigrations onlinecourse`.
- [x] Register seven models, QuestionInline, ChoiceInline, QuestionAdmin and
  LessonAdmin in onlinecourse/admin.py; set OnlineCourse in apps.py.

## 2. Exam flow
- [x] Implement submit(request, course_id), show_exam_result(request, course_id,
  submission_id), and extract_answers(request) in onlinecourse/views.py.
- [x] Add named submit and show_exam_result paths to onlinecourse/urls.py.
- [x] Build course_details_bootstrap.html and exam_result_bootstrap.html with
  course lessons, CSRF-protected checkbox inputs, score and per-question results.
- [x] Configure local-only hosts, generated local secret and updated dependencies.
- [x] Run `manage.py check`, `manage.py test` and migration consistency checks.

## 3. Deliver evidence
- [x] Add seed_demo management command using an ignored local credentials file.
- [x] Migrate and seed, start the localhost server, sign in through the browser.
- [x] Capture admin home, submit correct exam choices and capture results.
- [x] Visually inspect both screenshots and verify 100% and Congratulations.
- [x] Fork the official repository under wexer02, commit and push tested files.
- [x] Verify all five public URLs and deliver them in grading-task order.

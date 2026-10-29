# Final Project: Online Course Assessment

Completed from the IBM Developer Skills Network starter:
https://github.com/ibm-developer-skills-network/tfjzl-final-cloud-app-with-database

The app provides courses, lessons, enrollment, multiple-choice exams, saved
submissions, weighted grading, and a Django administration site.

## Run locally on Windows

Use Python 3.13:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Open http://127.0.0.1:8000/onlinecourse/ for courses or
http://127.0.0.1:8000/admin/ for administration. The seed command saves the
local demo username and randomly generated password in `.demo-credentials.json`.
That file, the local secret key and the SQLite database are excluded from Git.

On Linux or macOS, use `.venv/bin/python` instead of `.venv\Scripts\python.exe`.

## Assessment behavior

- Enrolled learners can select one or more choices for each question.
- Each question awards its full weight only when all correct choices and no
  incorrect choices are selected. Unanswered questions receive zero.
- The overall percentage is earned points divided by possible points.
- The passing score for the sample course exam is 80%.
- Results include the score, pass/fail message and a review of every question.
- Only the owner can view a submission. Invalid and cross-course choices are
  rejected before saving; submission and enrollment require POST and CSRF.

## Verify

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test
```

Tests cover exact-match and weighted grading, the passing boundary, unanswered
and empty exams, malformed and cross-course choices, enrollment, authentication,
CSRF, and result ownership.

## Grading files

1. `onlinecourse/models.py`: Question, Choice and Submission.
2. `onlinecourse/admin.py`: seven registered models and assessment inlines.
3. Screenshot `03-admin-site.png`: admin home with both required sections.
4. `onlinecourse/templates/onlinecourse/course_details_bootstrap.html`:
   course details, lessons and the exam form.
5. `onlinecourse/views.py`: submit and show_exam_result.
6. `onlinecourse/urls.py`: assessment paths.
7. Screenshot `07-final.png`: a real successful sample-exam submission.

Screenshots are captured from the running local app and delivered separately.
Bootstrap 4.5.2 CSS is included locally so course pages do not depend on a CDN.
The starter's cloud deployment manifests are historical; these instructions use
Django's local development server. Set a deployment-specific secret key, hosts,
HTTPS, static-file serving and DEBUG=False before any production deployment.

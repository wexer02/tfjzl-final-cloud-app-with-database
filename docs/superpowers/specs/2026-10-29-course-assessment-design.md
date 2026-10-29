# Online Course assessment

Extend the official IBM tfjzl-final-cloud-app-with-database starter in place.
Use Django 5.2, Python 3.13, SQLite and the starter's Bootstrap styling.

Question belongs to Course and contains question_text and a positive grade.
Choice belongs to Question and contains choice_text and is_correct.
Submission belongs to Enrollment and contains selected choices.
Question.is_get_score awards the question's full weight only for an exact,
nonempty match to all correct choices. Extra incorrect choices receive zero.

The admin imports Course, Lesson, Instructor, Learner, Question, Choice and
Submission. CourseAdmin includes LessonInline and QuestionInline;
QuestionAdmin includes ChoiceInline; LessonAdmin displays title, course, order.
The application label is OnlineCourse.

The course_details_bootstrap.html template displays the course title, all
ordered lessons, and an exam for authenticated enrolled users. The submit
view accepts POST with CSRF, validates every choice against the current course,
saves the submission, and redirects to show_exam_result. Only the submission's
owner can view it. Scores are weighted percentages; 80% passes. Empty exams fail.

Deliver five verified public GitHub file URLs and two genuine browser captures:
03-admin-site.png and 07-final.png. Seed a local demonstration course and local
administrator; keep its credentials, database and secret key out of Git.

Verify correct and incorrect answers, multiple selections, invalid/cross-course
choices, authentication, enrollment, CSRF, result ownership and empty exams.
Capture a real 100% submission through the browser, not injected result text.

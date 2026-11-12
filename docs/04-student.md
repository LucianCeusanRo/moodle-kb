# 4. Student-side legitimate features

Sources:
- https://docs.moodle.org/en/Grades
- https://docs.moodle.org/en/Quiz_reports
- https://docs.moodle.org/en/Activity_completion
- https://docs.moodle.org/en/Calendar
- https://moodledev.io/general/app
- https://moodledev.io/general/app/development/apis
- https://docs.moodle.org/en/Moodle_app

## Own grades
- WS: `gradereport_user_get_grade_items`, `gradereport_user_get_grades_table`, `gradereport_overview_get_course_grades`
- Requires user token (student) or teacher token viewing that user with caps
- LSPilot student app: show "My grades", progress bars, missing activities — never alter grades

## Review finished quiz attempts
- `mod_quiz_get_user_attempts` → attempt ids
- `mod_quiz_get_attempt_review` → questions/responses **filtered by review options**
- `mod_quiz_get_combined_review_options` → gate UI
- **Learn from mistakes**: only after attempt state `finished`/`abandoned` and only fields allowed (correctness, right answer, feedback). If teacher hid right answers until `timeclose`, wait.

## Calendar / deadlines
- `core_calendar_get_calendar_upcoming_view`
- `core_calendar_get_action_events_by_courses`
- `core_calendar_get_action_events_by_timesort`
- Surface quiz `timeclose`, assignment `duedate` as study reminders (not during attempt)

## Completion tracking
- `core_completion_get_activities_completion_status`
- `core_completion_get_course_completion_status`
- Help students see what's left; optional study plan

## Course contents for study mode
- `core_course_get_contents` — list resources/pages/books for summarisation / flashcards
- Files: download via `pluginfile.php` with token (`tokenpluginfile.php` / webservice) — respect copyright; summarise, don't redistribute

## Moodle App / Mobile API
- Same REST web services; app uses a built-in mobile service (`moodle_mobile_app`) with a fixed function list
- Site must enable mobile app; tokens via `/login/token.php` (avoid storing passwords in LSPilot — use OAuth/OIDC if school supports)
- Custom LSPilot functions in `local_lspilot` are **not** in the mobile service unless admin adds them to a service the app/token uses
- For in-browser Moodle (desktop), content-script guard + optional student personal token for grades/calendar only

## Legitimate student feature set (product)
1. Explain / hint / summarise on resources & practice quizzes
2. Flashcards + similar exercises from course materials
3. Learn-from-mistakes on allowed reviews
4. Deadline calendar + completion checklist
5. Study plan from weak grade items
6. Explicit OFF on graded attempts / SEB / password / timed exams

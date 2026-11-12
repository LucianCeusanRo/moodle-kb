# 1. Moodle Architecture (4.x / 5.x)

Sources:
- https://docs.moodle.org/en/Courses
- https://docs.moodle.org/en/Course_sections
- https://docs.moodle.org/en/Activities
- https://docs.moodle.org/en/Resources
- https://docs.moodle.org/en/Question_bank
- https://docs.moodle.org/en/Roles_and_capabilities
- https://docs.moodle.org/en/Context
- https://docs.moodle.org/en/Enrolment
- https://docs.moodle.org/en/Grades
- https://docs.moodle.org/en/Activity_completion
- https://moodledev.io/docs/apis/subsystems/access
- https://moodledev.io/docs/apis/plugintypes/mod
- https://moodledev.io/general/development/policies/codingstyle/sql (mdl_ tables)

## Hierarchy

```
Site (contextlevel 10 SYSTEM)
 └── Course category (40 COURSECAT)
      └── Course (50 COURSE)
           └── Section (topics / weeks / custom)
                └── Course module = cm (70 MODULE)
                     └── Activity instance (quiz / assign / …)
```

Other contexts: USER (30), BLOCK (80). Permissions inherit downward; a capability denied at course level blocks the module even if allowed at system.

URL patterns (classic theme / Boost):
- Course: `/course/view.php?id=<courseid>`
- Module: `/mod/<modname>/view.php?id=<cmid>`  (cmid = course_modules.id)
- Quiz attempt: `/mod/quiz/attempt.php?attempt=<aid>&cmid=<cmid>`
- Quiz review: `/mod/quiz/review.php?attempt=<aid>&cmid=<cmid>`
- Quiz summary: `/mod/quiz/summary.php?attempt=<aid>&cmid=<cmid>`
- Question bank: `/question/edit.php?courseid=<id>` or `/question/bank/…` (4.x+ pluginised)

## Courses & sections

- Course formats: topics, weeks, singleactivity, social, and plugins (`format_*`).
- Sections have `section`, `name`, `summary`, `visible`, `availability` (JSON availability conditions).
- Hidden sections / stealth activities exist; students may still have a direct URL depending on settings.

## Activities / modules (stock, relevant to LSPilot)

| Module | Plugin | Typical use | Graded? |
|--------|--------|-------------|---------|
| Quiz | `mod_quiz` | Timed/untimed tests from question bank | Yes (gradebook) |
| Assignment | `mod_assign` | File/online text submissions | Yes |
| Lesson | `mod_lesson` | Branched pages + questions | Optional |
| Forum | `mod_forum` | Discussion; can be rated | Optional |
| H5P activity | `mod_h5pactivity` | Interactive content + xAPI attempts | Optional |
| Resource (file) | `mod_resource` | PDF/DOC download or inline | No |
| Page | `mod_page` | HTML page | No |
| Book | `mod_book` | Multi-chapter resource | No |
| URL | `mod_url` | External link | No |
| Folder | `mod_folder` | File collection | No |
| Label / Text and media | `mod_label` | Inline course content | No |
| SCORM | `mod_scorm` | Packaged e-learning | Optional |
| Workshop | `mod_workshop` | Peer assessment | Yes |
| Feedback / Questionnaire | `mod_feedback` / contrib | Surveys | Usually no |

Each module has: `intro`, `introformat`, availability, completion conditions, and optionally a grade item.

## Question bank & categories

- Questions live in **question categories** scoped to: course, course category, system, or (Moodle 4.0+) **shared question banks** / activity context.
- A quiz does **not** own questions permanently in modern Moodle; it references **question bank entries** via **slots** (`quiz_slots`) and versions (`question_versions`).
- Random questions pick from a category (+ optionally subcategories) at attempt time.
- Core question types (`qtype_*`): `multichoice`, `truefalse`, `shortanswer`, `numerical`, `match`, `essay`, `calculated`, `calculatedmulti`, `calculatedsimple`, `ddwtos`, `ddimageortext`, `ddmarker`, `gapselect`, `multianswer` (cloze), `description`, `randomsamatch`, plus 3rd-party.
- Import/export formats: GIFT, Moodle XML, Aiken, Blackboard, Examview, Word table (plugin), etc. UI: Question bank → Import. **No stock web service creates questions.**

## Roles & capabilities

Default archetypes (site / course):
- `manager` – almost admin without site config
- `coursecreator` – create courses in categories
- `editingteacher` – full course edit, grade, manage activities
- `teacher` (non-editing) – grade, view, limited edit
- `student` – participate
- `guest` – view if guest access on
- `user` / `frontpage` – authenticated / front page

Key capabilities for LSPilot:
- Student: `mod/quiz:attempt`, `mod/quiz:reviewmyattempts`, `mod/assign:submit`, `moodle/grade:view`, `moodle/calendar:manageownentries`
- Teacher: `moodle/course:manageactivities`, `mod/quiz:manage`, `mod/quiz:addinstance`, `mod/quiz:viewreports`, `moodle/question:add`, `moodle/question:editmine` / `editall`, `moodle/question:useall`, `moodle/course:viewparticipants`, `moodle/grade:edit`
- Web service tokens run **as a user**; the token inherits that user's roles/capabilities. Prefer a dedicated service account with least privilege + a custom external service that whitelists only needed functions.

## Enrolments

Plugins: `manual`, `self`, `guest`, `cohort`, `meta` (meta-course), `lti`, `paypal`, LDAP, etc.
- `core_enrol_get_users_courses` – courses for a user
- `core_enrol_get_enrolled_users` – users in a course
Enrolment gives a role at course context.

## Gradebook

- Categories → grade items (mod-linked or manual) → grades.
- Aggregation: natural, mean, weighted mean, etc.
- Activity modules push grades via gradebook API; LTI AGS / Outcome can too.
- Student view: User report; teacher: Grader, Overview, Single view.
- Relevant WS: `gradereport_user_get_grade_items`, `gradereport_user_get_grades_table`, `gradereport_overview_get_course_grades`, `core_grades_get_gradeitems`, `core_grades_update_grades`.

## Completion & availability

- Activity completion: manual tick or automatic (view / grade / submit).
- Course completion: aggregation of activities + other criteria.
- Restrict access: date, grade, group, profile field, previous completion, language (availability JSON).
- WS: `core_completion_get_activities_completion_status`, `core_completion_get_course_completion_status`.

## Safe Exam Browser (SEB)

Configured under Quiz → Extra restrictions on attempts → Browser security. Moodle can require SEB, validate config keys / quit passwords, and block leaving fullscreen. For LSPilot exam-mode guard: treat SEB presence (UA contains `SEB`, quiz `browsersecurity` = `securewindow` / `safebrowser`) as hard exam mode — assistant must stay off.

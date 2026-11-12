# 2. Moodle Web Services / REST API

Sources:
- https://docs.moodle.org/en/Using_web_services
- https://docs.moodle.org/en/Web_services
- https://docs.moodle.org/en/Create_a_web_service_and_a_token
- https://docs.moodle.org/en/Web_service_API_functions
- https://moodledev.io/docs/apis/subsystems/external
- https://moodledev.io/general/app/development/apis
- Verified against: https://github.com/moodle/moodle/blob/main/lib/db/services.php
  and module `db/services.php` files (see `functions_verified.json`, 492 functions on `main` / Moodle 5.x).

## How a school enables API access (admin checklist)

1. **Site administration → Advanced features → Enable web services**
2. **Plugins → Web services → Manage protocols** → enable **REST** (JSON). Optionally XML-RPC (deprecated) / SOAP.
3. Create a **External service** (Custom service):
   - Short name e.g. `lspilot`
   - Enabled, Authorised users only (recommended) OR available to all users with capability
   - Add **only** the functions LSPilot needs (principle of least privilege)
4. Create a **service account user** (e.g. `lspilot-integration`) enrolled as editing teacher / manager in target courses, OR use per-teacher tokens.
5. **Plugins → Web services → Manage tokens** → Create token for that user + that service.
6. Capabilities the token user needs include (depending on scope):
   - `webservice/rest:use`
   - `moodle/course:view`, `moodle/course:viewhiddencourses` (if needed)
   - `moodle/question:add`, `moodle/question:editall`, `moodle/question:useall`
   - `mod/quiz:addinstance`, `mod/quiz:manage`, `moodle/course:manageactivities`
   - Grade / enrol caps only if those features are used
7. Call pattern:
   ```
   POST https://<moodle>/webservice/rest/server.php
     wstoken=<token>
     wsfunction=<fname>
     moodlewsrestformat=json
     + function params
   ```
   File upload: `POST /webservice/upload.php?token=<token>` then pass `itemid` to `core_files_upload` / draft-file APIs.

**Security:** Prefer school-issued tokens (not password login). Rotate tokens. Never embed tokens in the student Chrome extension — teacher flows use server-side LSPilot backend that holds the token encrypted per-tenant.

## Catalog of relevant functions (verified present)

### Core / site
| Function | Type | Caps (from services.php) | LSPilot use |
|----------|------|--------------------------|-------------|
| `core_webservice_get_site_info` | read | — | Handshake, version, user id, site name |
| `core_course_get_courses` | read | `moodle/course:view`, `moodle/course:viewhiddencourses` | List courses token can see |
| `core_course_get_courses_by_field` | read | | Lookup by id/shortname/idnumber |
| `core_course_get_contents` | read | | Sections + modules (cmid, modname, name, url) |
| `core_course_get_course_module` | read | | Single cm details |
| `core_course_get_course_module_by_instance` | read | | Resolve instance→cm |
| `core_course_create_courses` | write | | Provision course (rare; school admin) |
| `core_course_update_courses` | write | | Update course fields |
| `core_course_edit_module` | write | | Show/hide/duplicate/delete/move cm (**not** full quiz config) |
| `core_course_delete_modules` | write | | Delete activities |
| `core_course_import_course` | write | | Import content between courses |
| `core_course_duplicate_course` | write | | Duplicate |
| `core_course_get_enrolled_courses_by_timeline_classification` | read | | Student "my courses" |
| `core_enrol_get_users_courses` | read | | Courses for a userid |
| `core_enrol_get_enrolled_users` | read | | Participants |
| `core_user_get_users_by_field` | read | | Resolve users |
| `core_role_assign_roles` / `unassign_roles` | write | | Rare; prefer enrol plugins |
| `core_files_upload` | write | | Upload to draft area |
| `core_calendar_get_calendar_upcoming_view` | read | | Deadlines |
| `core_calendar_get_action_events_by_courses` | read | | Action events |
| `core_calendar_get_action_events_by_timesort` | read | | Sorted events |
| `core_completion_get_activities_completion_status` | read | | Per-activity completion |
| `core_completion_get_course_completion_status` | read | | Course completion |
| `core_grades_get_gradeitems` | read | | Grade items |
| `core_grades_update_grades` | write | | Push grades (careful) |
| `gradereport_user_get_grade_items` | read | | Student/teacher grade items |
| `gradereport_user_get_grades_table` | read | | Formatted user report |
| `gradereport_overview_get_course_grades` | read | | Overview |

### Quiz (`mod/quiz/db/services.php`)
| Function | Type | LSPilot use |
|----------|------|-------------|
| `mod_quiz_get_quizzes_by_courses` | read | List quizzes + settings (timeopen/close, timelimit, attempts, preferredbehaviour, …) |
| `mod_quiz_get_quiz_access_information` | read | Can attempt? preventions |
| `mod_quiz_get_user_attempts` | read | Past attempts |
| `mod_quiz_get_user_quiz_attempts` | read | Alias-style listing |
| `mod_quiz_get_attempt_access_information` | read | Can continue / finish |
| `mod_quiz_get_attempt_summary` | read | Summary before submit |
| `mod_quiz_get_attempt_data` | read | Questions in in-progress attempt (**do not use for cheating**) |
| `mod_quiz_get_attempt_review` | read | Review after finish (**respect review options**) |
| `mod_quiz_get_combined_review_options` | read | What student may see when |
| `mod_quiz_get_user_best_grade` | read | Best grade |
| `mod_quiz_get_overrides` / `save_overrides` / `delete_overrides` | r/w | Per-user/group overrides |
| `mod_quiz_start_attempt` | write | Start attempt — **student app only if school allows; never auto-answer** |
| `mod_quiz_save_attempt` | write | Save responses |
| `mod_quiz_process_attempt` | write | Save / finish |
| `mod_quiz_view_quiz` / `view_attempt` / `view_attempt_summary` / `view_attempt_review` | write | Logging/view events |
| `mod_quiz_add_random_questions` | write | Add random from category (needs existing bank) |
| `mod_quiz_update_slots` | write | Reorder/update slots |
| `mod_quiz_set_question_version` | write | Pin question version |
| `mod_quiz_create_grade_items` / `update_grade_items` / `delete_grade_items` | write | Quiz grade items (sections) |

### Assign / Lesson / H5P
- `mod_assign_get_assignments`, `get_submission_status`, `get_submissions`, `save_submission`, `submit_for_grading`, `save_grade(s)`, overrides…
- `mod_lesson_get_lessons_by_courses`, `get_lesson`, `get_lesson_access_information`, `get_pages`, `get_page_data`, attempts/grades…
- `mod_h5pactivity_get_h5pactivities_by_courses`, `get_attempts`, `get_user_attempts`, `get_results`, access info

### Question bank (stock — LIMITED)
Only these exist in core `services.php`:
- `core_question_update_flag`
- `core_question_get_random_question_summaries`
- `core_question_move_questions`
- `core_question_search_shared_banks`

**There is NO** `core_question_create_questions`, **NO** quiz-create-with-questions WS, **NO** GIFT/XML import WS in stock Moodle.

## What is NOT possible via stock web services

| Desired action | Stock WS? | Workaround |
|----------------|-----------|------------|
| Create question(s) in bank | ❌ | `local_lspilot` plugin external function wrapping `question_bank` APIs / import from string |
| Import GIFT or Moodle XML | ❌ (UI only) | Same local plugin calling `\qformat_gift` / `\qformat_xml` |
| Create a Quiz activity with full settings | ❌ (only `core_course_edit_module` for show/hide etc.) | Plugin: `add_moduleinfo()` / `quiz_add_instance`, or restore a template course backup |
| Add specific (non-random) questions to quiz | Partial: slots update exists but questions must already exist | Plugin creates questions then `mod_quiz_update_slots` / quiz structure API |
| Auto-publish quiz at datetime | Partial: need instance + `timeopen`/`timeclose` | Plugin sets quiz fields; or create hidden then reveal via `core_course_edit_module` |
| Bulk course create from CSV | ❌ WS | Admin tool `tool_uploadcourse` (CLI/UI) |
| Full course restore | Limited | Backup/restore API in plugin or MBZ upload by admin |

## Recommended architecture: `local_lspilot`

```
local/lspilot/
  version.php, settings.php
  db/services.php          # declare custom external functions
  classes/external/
    import_questions.php   # GIFT/XML string → category
    create_quiz_from_spec.php  # settings + slot list → cmid
    schedule_quiz.php      # timeopen/timeclose + visibility
    get_teacher_dashboard.php
  classes/privacy/provider.php  # GDPR Privacy API
  lang/en/local_lspilot.php
```

Expose only via a dedicated external service `local_lspilot`. School installs from ZIP / private Git; LSPilot cloud talks REST with school token.

Alternatives (worse):
- Simulate browser UI (fragile, ToS risk)
- Only generate GIFT file for manual import (good MVP, no auto-publish)
- Course restore from prebuilt MBZ templates (clunky)

## Auth models for LSPilot

1. **Teacher MVP:** generate GIFT/XML download → teacher imports manually (zero Moodle install).
2. **School plugin:** `local_lspilot` + token → auto import + create quiz + schedule.
3. **LTI 1.3 tool:** deep link content / launch generator from within Moodle without storing passwords (see `05-integration.md`).

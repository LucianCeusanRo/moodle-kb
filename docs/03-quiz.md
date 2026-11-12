# 3. Quiz details, question formats, exam-mode detection

Sources:
- https://docs.moodle.org/en/Quiz_settings
- https://docs.moodle.org/en/Quiz_activity
- https://docs.moodle.org/en/Using_Safe_Exam_Browser
- https://docs.moodle.org/en/Question_types
- https://docs.moodle.org/en/GIFT_format
- https://docs.moodle.org/en/Moodle_XML_format
- https://docs.moodle.org/en/Import_questions
- https://moodledev.io/docs/apis/plugintypes/qtype
- Quiz table fields: https://github.com/moodle/moodle/blob/main/mod/quiz/db/install.xml
- WS: `mod_quiz_get_quizzes_by_courses` returns many of these fields

## Key quiz settings (`mdl_quiz`)

| Field | Meaning |
|-------|---------|
| `timeopen` / `timeclose` | Unix timestamps; 0 = unset |
| `timelimit` | Seconds; 0 = no limit |
| `overduehandling` | autosubmit / graceperiod / autoabandon |
| `graceperiod` | Seconds after timeclose |
| `attempts` | Max attempts; 0 = unlimited |
| `grademethod` | highest / average / first / last |
| `questionsperpage` | Pagination |
| `navmethod` | free / sequential |
| `shuffleanswers` | 0/1 |
| `preferredbehaviour` | deferredfeedback, adaptive, adaptivenopenalty, immediatefeedback, immediatecbm, deferredcbm, interactive |
| `attemptonlast` | Build on last attempt |
| `decimalpoints` / `questiondecimalpoints` | Display |
| **Review options** | Bitfields / separate columns: `reviewattempt`, `reviewcorrectness`, `reviewmarks`, `reviewspecificfeedback`, `reviewgeneralfeedback`, `reviewrightanswer`, `reviewoverallfeedback` — each for: during, immediately after, later while open, after close |
| `subnet` | Allowed IP subnet |
| `password` / `quizpassword` | Require password |
| `browsersecurity` | `''`, `securewindow`, or SEB-related values |
| `seb_*` fields / quizaccess_seb plugin | SEB config key, template, quit password |
| `delay1` / `delay2` | Delay between attempts |
| `canredoquestions` | Redo within attempt (some behaviours) |

`mod_quiz_get_combined_review_options` tells the client what the current user may see for an attempt **right now**.

### Graded vs practice (product logic)

Treat as **EXAM / graded (assistant OFF)** if any of:
- `grademax` / grade item weight > 0 AND not clearly formative
- `timeopen`/`timeclose` window active with limited attempts
- `timelimit` > 0
- `password` set
- `subnet` set
- `browsersecurity` non-empty or SEB required
- Course module availability restricted to exam window
- Teacher flag / LSPilot school policy "exam"

Treat as **PRACTICE (assistant ON)** if:
- Unlimited attempts + no time limit + grade item excluded from aggregation / max grade 0
- Or explicitly tagged (idnumber `practice`, category "Formative")
- Or review/lesson/book/resource/page context

When unsure: **default OFF** on `attempt.php`; ON on course resources and post-close `review.php` only if review options allow seeing questions/right answers.

## Question types (core)

`multichoice`, `truefalse`, `shortanswer`, `numerical`, `match`, `essay`, `calculated*`, `ddwtos`, `ddimageortext`, `ddmarker`, `gapselect`, `multianswer` (Cloze), `description`, `randomsamatch`.

Teacher generator MVP should emit: multichoice, truefalse, shortanswer, matching, numerical, essay. Cloze later (M).

## GIFT examples

```gift
// True/False
The Earth is flat.{FALSE}

// Multiple choice
Who wrote Hamlet?{
  ~Shakespeare
  ~Goethe
  =Shakespeare
  ~Dante
}

// Better MC with feedback
::Q1::Who wrote Hamlet?{
  ~%0%Goethe#Wrong era
  =%100%Shakespeare#Correct
  ~%0%Dante#Italian poet
}

// Short answer
What is 2+2?{=4 =four}

// Numerical
How many continents?{#7:0}

// Matching
Match countries::{
  =France -> Paris
  =Italy -> Rome
  =Spain -> Madrid
}

// Essay
Write a short paragraph about photosynthesis{}
```

Encoding: UTF-8. Special chars `~ = # { } :` escaped with `\`. Categories: `$CATEGORY: Course/Topic1`.

## Moodle XML (abbreviated)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<quiz>
  <question type="category">
    <category><text>$course$/Imported/LSPilot</text></category>
  </question>
  <question type="multichoice">
    <name><text>Hamlet author</text></name>
    <questiontext format="html"><text><![CDATA[<p>Who wrote Hamlet?</p>]]></text></questiontext>
    <answernumbering>abc</answernumbering>
    <answer fraction="100" format="html"><text>Shakespeare</text></answer>
    <answer fraction="0" format="html"><text>Goethe</text></answer>
    <answer fraction="0" format="html"><text>Dante</text></answer>
  </question>
  <question type="truefalse">
    <name><text>Earth flat</text></name>
    <questiontext format="html"><text>The Earth is flat.</text></questiontext>
    <answer fraction="0"><text>true</text></answer>
    <answer fraction="100"><text>false</text></answer>
  </question>
</quiz>
```

Import UI: Question bank → Import → choose format → file → category. Plugin path: `question/format/gift`, `question/format/xml`.

## DOM / URL detection for exam-mode guard (student extension)

Run on every navigation / MutationObserver; **fail closed** (disable assistant).

### URL heuristics
| Pattern | Mode |
|---------|------|
| `/mod/quiz/attempt.php` | EXAM_OFF |
| `/mod/quiz/summary.php` | EXAM_OFF |
| `/mod/quiz/processattempt.php` | EXAM_OFF |
| `/mod/quiz/startattempt.php` | EXAM_OFF |
| `/mod/quiz/review.php` | LEARN_FROM_MISTAKES only if review shows questions; still no "solve live" |
| `/mod/quiz/view.php` | Soft: read page for attempt buttons / time limit text; default cautious OFF if "Attempt quiz now" + timer info |
| `/mod/assign/view.php` with submission form | OFF if graded assign (optional policy) |
| `/mod/lesson/` during timed lesson | OFF if timed |
| `/mod/resource/`, `/mod/page/`, `/mod/book/`, `/course/view.php`, `/mod/forum/` | ON (learning) |
| Path contains `seb` / SEB config download | OFF |
| Moodle App WebView | Same rules; prefer Mobile API for grades/review |

### DOM / body class heuristics (Boost / Classic)
- `body#page-mod-quiz-attempt`, `page-mod-quiz-summary`, `page-mod-quiz-review`, `page-mod-quiz-view`
- `#mod_quiz_navblock`, `.que` question containers on attempt
- Timer: `#quiz-timer`, `.quiz-timer-wrapper`, `[data-region="quiz-timer"]`, `#quiz-time-left`
- SEB: `navigator.userAgent` includes `SEB` or `SafeExamBrowser`
- Password gate: form with quiz password field before attempt
- Access rule messages: `.quizaccessdenied`, region `access-messages`

### API cross-check (if school token + student identity available — rare for extension)
`mod_quiz_get_quiz_access_information` / `get_quizzes_by_courses` for `timelimit`, `browsersecurity`, attempts left.

### UX when OFF
Visible banner: "Mod examen – asistentul este oprit" / "Exam mode – assistant paused". No OCR, no answer suggestions, no auto-fill. Session reset button only clears local LSPilot state (not Moodle).

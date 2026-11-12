# 6. Gap list — what LSPilot must build

Prioritized for the legitimate pivot (student learning assistant + teacher quiz generator). Effort: S ≈ days, M ≈ 1–2 weeks, L ≈ multi-week.

## P0 — Must have for honest launch

| ID | Gap | Why | Effort |
|----|-----|-----|--------|
| G1 | Teacher PDF → questions → **human review UI** → export GIFT + Moodle XML | Stock Moodle has no create/import WS; export is the universal path | M |
| G2 | Exam-mode guard: URL/DOM/SEB detection, fail-closed, visible banner | Legal/compliance; Netlify already rejected bypass framing | M |
| G3 | Strip remaining bypass / "invisible" / panic-button claims from **all** binaries still downloadable (Win/iOS/Safari zips) | Trust + store + Cloudflare risk | S–M |
| G4 | Learn-from-mistakes only on `review.php` / API review with options respected | Core student value without cheating | M |
| G5 | Privacy policy + academic integrity page aligned with real behaviour; processor DPA template for schools | GDPR + sales | S |
| G6 | `local_lspilot` Moodle plugin skeleton: `import_questions`, `create_quiz_from_spec`, Privacy API | Unlocks auto-publish for paying schools | L |

## P1 — Institution sales

| ID | Gap | Why | Effort |
|----|-----|-----|--------|
| G7 | LTI 1.3 tool (register, deep link file/link, basic launch) | Schools that refuse plugins | L |
| G8 | School admin console: tenants, tokens, course mapping, audit log | B2B requirement | M |
| G9 | Teacher dashboard: schedule `timeopen`/`timeclose`, difficulty, category, attempt limits | Matches user request "publică la orele…" | M (needs G6) |
| G10 | Pricing pages: Student / Teacher free tier / School seat license | Conversion; currently weak/offer-on-request only | S |
| G11 | Romanian + DE-CH/FR-CH school landing case studies | SEO / discoverability | M |

## P2 — Product depth

| ID | Gap | Why | Effort |
|----|-----|-----|--------|
| G12 | Similar-question generator from wrong answers + spaced repetition | Differentiator vs Photomath-in-Moodle | M |
| G13 | Student grades + calendar + completion via student token | Sticky daily use | M |
| G14 | H5P / Lesson practice mode support | Moodle content variety | M |
| G15 | Question quality checks (bloom level, ambiguity, duplicate) before teacher approve | Trust in AI items | M |
| G16 | Moodle XML round-trip tests against Moodle 4.1, 4.5, 5.0 | Avoid import failures | S |
| G17 | Browser extension store listings rewritten for learning-only | Distribution | S |

## P3 — Later

| ID | Gap | Why | Effort |
|----|-----|-----|--------|
| G18 | Official plugin directory submission | Discoverability | M |
| G19 | AGS grade pass-back for LTI activities | Complete LTI story | M |
| G20 | SCORM summarise (careful with copyright) | Niche | L |
| G21 | On-prem LLM option for ministries | Enterprise RFPs | L |

## Explicit non-goals (do not build)

- Auto-answer during `attempt.php`
- Hidden/invisible overlay, panic hide, SEB bypass, focus-steal
- Scraping teacher passwords
- Chargeback / harassment campaigns against competitors

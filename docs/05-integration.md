# 5. Integration options: LTI 1.3, plugins, privacy/GDPR

Sources:
- https://docs.moodle.org/en/LTI
- https://docs.moodle.org/en/LTI_External_tool
- https://moodledev.io/general/development/lti
- https://www.imsglobal.org/spec/lti/v1p3/
- https://www.imsglobal.org/spec/lti-dl/v2p0 (Deep Linking)
- https://www.imsglobal.org/spec/lti-ags/v2p0 (Assignment and Grade Services)
- https://docs.moodle.org/en/Installing_plugins
- https://moodledev.io/general/community/plugincontribution
- https://moodledev.io/docs/apis/subsystems/privacy
- https://docs.moodle.org/en/GDPR
- https://docs.moodle.org/en/Privacy_API

## LTI 1.3 (institution-friendly)

Best for schools that will not install a local plugin quickly.

**Tool registration (Moodle as platform):**
1. Site admin → Plugins → Activity modules → External tool → Manage tools → configure tool manually / enter tool URL / dynamic registration
2. Moodle provides: Issuer, Auth request URL, Token URL, Public keyset URL, Deployment ID
3. LSPilot tool provides: Client ID (issued by Moodle), JWKS, initiate-login URL, redirect URIs, Deep Linking URL

**Launches:**
- Resource link launch: teacher/student opens LSPilot from course
- **Deep Linking**: teacher picks generated quiz / content → returns content item (file GIFT/XML, link, or LTI resource) into Moodle
- **AGS**: LSPilot can send scores back for LTI-launched graded activities (not for native `mod_quiz` attempts unless bridged)

**Limits:** Deep Linking can drop a file or link; creating a native Moodle quiz still needs plugin or manual import. Hybrid: LTI for teacher UX + optional `local_lspilot` for native quiz publish.

## Moodle plugin directory requirements

For public listing (https://moodle.org/plugins):
- Correct `version.php` (`component`, `version`, `requires`, `supported` Moodle versions)
- English lang strings; Privacy API provider implemented
- No bundled secrets; follow coding style; third-party libs declared
- Automated checks + human review; keep versions updated for 4.1+ / 5.x
- Prefer `local_lspilot` private distribution for paid B2B until mature; then publish free "connector" + cloud SaaS

Plugin types useful to LSPilot:
- `local_lspilot` — WS + scheduled tasks + settings
- Optional `mod_lspilot` — course activity wrapper
- Optional `qbank_lspilot` / import format plugin `qformat_lspilot` if custom format needed (usually GIFT/XML enough)
- Optional `quizaccess_lspilot` — **do not** build access rules that weaken proctoring

## Privacy API / GDPR

Moodle sites in EU/EEA (and RO schools) need:
- LSPilot as **processor**: DPA with school (controller)
- Plugin `classes/privacy/provider.php`: export/delete user data Moodle stores locally
- Cloud LSPilot: retention limits, encryption at rest, EU region option, no training on customer content without consent
- Document: what student extension stores locally vs sends to API; exam-mode must not transmit question text
- Lawful basis: contract with school / legitimate interest for student consumer — prefer school contract for institution sales
- Subprocessors list (Gemini/LLM provider etc.) in privacy policy — align with site privacy pages
- Company identifiers on marketing pages must match the official trade register entry

## Auth comparison

| Method | Install needed | Auto-create quiz | Trust |
|--------|----------------|------------------|-------|
| Manual GIFT/XML download | No | No | Highest (MVP) |
| Token + stock WS only | No (enable WS) | No | High but limited |
| `local_lspilot` plugin | Yes | Yes | High for IT |
| LTI 1.3 | Tool register | Partial (file/link) | Highest for IT |
| Scraping UI / password | No | Fragile | **Do not** |

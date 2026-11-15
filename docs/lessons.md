# Lessons

What this project's past changes taught us. Read all of this before changing an API, a format or an
agreed behaviour here. For the full story of a line, find the entry with the same date and name in
`lessons-full.md`.

When one has to change, add the full entry to `lessons-full.md` and one line here, newest last, in the
same commit as the change. Never merge lines to save space; before this file passes 80 KB (what one
Claude Code read returns, measured 2026-11-15), ask the user.

- **2026-11-14 statblk 1.62: a copy you carry is no requirement**: declare only what the program needs from outside it. A library it embeds and picks by version at import needs no install requirement, and one left behind guarantees nothing while the installer's own failures (pip 9 upgrading an old multiCMD, `DuplicateOptionError`) stop your install.
- **2026-11-14 statblk 1.62: a source the timeout cut is named, and a check it hid is unknown**: read the exit status of every command whose output fills the result, not only its output; one stopped part way is named where the operator reads (stderr, after the table), with what it leaves missing, and a health check counts what the cut could hide from it as "could not tell", never as healthy; a cut that hides nothing it reads leaves a healthy run's answer and silence as they were.

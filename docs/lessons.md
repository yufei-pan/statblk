# Lessons

What this project's past changes taught us. Read all of this before changing an API, a format or an
agreed behaviour here. For the full story of a line, find the entry with the same date and name in
`lessons-full.md`.

When one has to change, add the full entry to `lessons-full.md` and one line here, newest last, in the
same commit as the change. Keep this file under 20 KB: at the cap, merge lines before adding.

- **2026-11-14 statblk 1.62: a copy you carry is no requirement**: declare only what the program needs from outside it. A library it embeds and picks by version at import needs no install requirement, and one left behind guarantees nothing while the installer's own failures (pip 9 upgrading an old multiCMD, `DuplicateOptionError`) stop your install.
- **2026-11-14 statblk 1.62: a source the timeout cut is named, and a check it hid is unknown**: read the exit status of every command whose output fills the result, not only its output; one stopped part way is named where the operator reads (stderr, after the table), with what it leaves blank, and a health check counts what it could not see as "could not tell", never as healthy.

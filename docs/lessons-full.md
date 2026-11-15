# Lessons: full entries

Why this project's APIs, formats and agreed behaviours had to change. `lessons.md` has one line per
entry: read that first, and look entries up here by date and name rather than reading this whole. New
entries go last, in the same commit as the change:

```markdown
## YYYY-MM-DD <short name>
- Changed: ...
- Why we had to change: ...
- Original design was wrong because: ...
- Lesson: ...
```

## 2026-11-14 statblk 1.62: a copy you carry is no requirement
- Changed: statblk's package metadata requires no multiCMD (`install_requires` drops `multiCMD>=1.56`). statblk runs the multiCMD it embeds (1.67 in 1.62) wherever the installed one is older than that copy, missing, or does not import, and an installed one at least as new, as before.
- Why we had to change: the floor (1.56) was below the copy statblk uses (1.61 in 1.61), so the requirement guaranteed nothing statblk relied on; it only made pip install or upgrade a multiCMD that statblk then passed over. And pip 9.0.3 (stock on EL7 and EL8) upgrades every requirement under `-U`, which stopped the install: with multiCMD 1.55 or 1.57 installed, `pip install -U statblk==1.61` exited 2 with `configparser.DuplicateOptionError` (those versions' `mcmd`, `multicmd` and `multiCMD` entry points, which pip 9 reads as one name). Without the requirement, pip 9.0.3 upgrades 1.61 to 1.62 there (exit 0, multiCMD left as it was, statblk running its embedded 1.67), and with multiCMD 1.67 installed statblk imports that one (the CI's python:3.6 image, 2026-11-14). hpcp dropped its requirement for the same reason in 9.89; the user chose "Drop it, as hpcp did (Recommended)".
- Original design was wrong because: the requirement dates from when statblk needed an installed multiCMD; once statblk carried its own copy and chose between the two by version at import, it stated no need, and a requirement that states no need still hands the installer's own failures to every install.
- Lesson: declare as a requirement only what the program needs from outside it. A library it carries a copy of and picks by version at import is not one.

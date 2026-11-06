# Limitations

Approved known limitations and deferrals. Reviewers: read this first, and don't raise these again.

### The stuck-smartctl check sees only processes in statblk's /proc
- Kind: known limitation
- What the operator sees: statblk 1.58 starts no new smartctl on a disk where one older than `--timeout` is still
  running, but it can only find that one in its own `/proc`. Two cases where it can't: `/proc` mounted with
  `hidepid` (common on shared nodes) and a non-root user running `statblk --sudo -w` or a non-root cron
  `statblk --sudo --check` (the stuck smartctl runs as root and is hidden); or statblk in a fresh container with its
  own process namespace (a stuck smartctl from earlier runs or from the host is not visible). There, as in 1.57,
  each refresh or run whose smartctl gets stuck adds one more stuck process.
- Why: nothing statblk can do makes `/proc` show processes the kernel hides from it.
- Revisit when: someone runs statblk that way on a host with a dying disk.
- Approved: 2026-10-29, the user chose "Known limitation (Recommended)".

### `-t 0` does not wait for lsblk
- Kind: deferred
- What the operator sees: `statblk -t 0` does not wait for lsblk, because `lsblk_result.thread.join(0)` returns at once, where the SMART path takes 0 as no limit. With lsblk delayed 0.6 s by a fake, SERIAL stayed blank where `-t 2` showed it; the real lsblk won the race 5 of 5 times. Same in 1.58.
- Why: old and rare. The fix is `join(_remaining(deadline))`.
- Revisit when: the next statblk release.

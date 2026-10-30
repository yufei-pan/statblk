import pytest

import statblk
from fakes import make_proc_process


@pytest.fixture(autouse=True)
def boot_1000(monkeypatch):
    monkeypatch.setattr(statblk, "_boot_seconds", lambda: 1000)


def test_old_smartctl_marks_its_disk(tmp_path):
    make_proc_process(tmp_path, 41, ["/usr/sbin/smartctl", "-n", "standby", "-H", "/dev/sda"], age=30)
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == {"/dev/sda"}


def test_young_smartctl_is_not_stuck(tmp_path):
    make_proc_process(tmp_path, 41, ["smartctl", "-H", "/dev/sda"], age=1)
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == set()


def test_other_process_naming_the_disk_is_ignored(tmp_path):
    make_proc_process(tmp_path, 41, ["dd", "if=/dev/zero", "of=/dev/sda"], age=30, comm="dd")
    make_proc_process(tmp_path, 42, ["vi", "/dev/sda"], age=30, comm="vi")
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == set()


def test_smartctl_under_sudo_is_found_by_the_real_process(tmp_path):
    make_proc_process(tmp_path, 40, ["sudo", "smartctl", "-H", "/dev/sdb"], age=30, comm="sudo")
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == set()
    make_proc_process(tmp_path, 41, ["smartctl", "-H", "/dev/sdb"], age=30)
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == {"/dev/sdb"}


def test_matching_is_by_comm_not_argv0(tmp_path):
    # A script named smartctl run through its shebang has argv[0] "python3" but comm "smartctl".
    make_proc_process(tmp_path, 41, ["python3", "-H", "/dev/sda"], age=30)
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == {"/dev/sda"}


def test_smartctl_sudo_ran_by_file_descriptor_is_found_by_argv0(tmp_path):
    # sudo with a digest in sudoers runs smartctl by fexecve: before Linux 6.14 its comm is the fd number.
    make_proc_process(tmp_path, 41, ["/usr/sbin/smartctl", "-n", "standby", "-H", "/dev/sda"], age=30, comm="4")
    make_proc_process(tmp_path, 42, ["/usr/bin/python3", "/dev/sdb"], age=30, comm="5")  # another fexecve'd program
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == {"/dev/sda"}


def test_comm_with_parentheses_is_not_cut_at_the_first_one(tmp_path):
    # comm "smartctl) (x" must not be read as "smartctl" (cut at the first ')').
    make_proc_process(tmp_path, 41, ["smartctl", "-H", "/dev/sda"], age=30, comm="smartctl) (x")
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == set()


def test_no_cmdline_read_for_other_processes(tmp_path, monkeypatch):
    # Reading another process's cmdline touches its memory and can hang on a wedged one.
    make_proc_process(tmp_path, 41, ["dd", "of=/dev/sda"], age=30, comm="dd")
    make_proc_process(tmp_path, 42, ["smartctl", "-H", "/dev/sdb"], age=30)
    make_proc_process(tmp_path, 43, ["smartctl", "-H", "/dev/sdc"], age=1)
    opened = []
    real_read_text = statblk.read_text
    monkeypatch.setattr(statblk, "read_text", lambda path: opened.append(path) or real_read_text(path))
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == {"/dev/sdb"}
    cmdlines = [p for p in opened if p.endswith("/cmdline")]
    assert cmdlines == [str(tmp_path / "42" / "cmdline")]  # not 41, and not the young 43


def test_age_comes_from_boot_clock_not_proc_uptime(tmp_path):
    # lxcfs: /proc/uptime is the container's (50 s), starttime counts from host boot.
    make_proc_process(tmp_path, 41, ["smartctl", "-H", "/dev/sda"], age=30, uptime=50)
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == {"/dev/sda"}


def test_unreadable_or_vanished_pid_is_skipped(tmp_path):
    make_proc_process(tmp_path, 41, ["smartctl", "-H", "/dev/sda"], age=30)
    (tmp_path / "42").mkdir()  # exited between listdir and read: no files
    make_proc_process(tmp_path, 43, ["smartctl", "-H", "/dev/sdb"], age=30)
    (tmp_path / "43" / "stat").write_text("garbage")
    make_proc_process(tmp_path, 44, ["smartctl", "-H", "/dev/sdc"], age=30)
    (tmp_path / "44" / "stat").write_text("44 (smartctl) D 1 2")  # truncated
    make_proc_process(tmp_path, 45, ["smartctl", "-H", "/dev/sdd"], age=30)
    (tmp_path / "45" / "cmdline").unlink()  # exited after stat
    (tmp_path / "self").mkdir()
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == {"/dev/sda"}


def test_no_proc_is_an_empty_set(tmp_path, monkeypatch):
    make_proc_process(tmp_path, 41, ["smartctl", "-H", "/dev/sda"], age=30)
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path / "missing")) == set()
    # no boot clock (macOS, odd platform): nothing to compare against
    def no_clock():
        raise OSError("no CLOCK_BOOTTIME")
    monkeypatch.setattr(statblk, "_boot_seconds", no_clock)
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == set()


def test_by_id_symlink_argument_resolves_to_the_disk(tmp_path, monkeypatch):
    # /dev/disk/by-id/... is a symlink to the disk; the argument is matched by real path.
    import os
    real_realpath = os.path.realpath
    monkeypatch.setattr(
        os.path, "realpath",
        lambda p: "/dev/sda" if p == "/dev/disk/by-id/ata-FAKE" else real_realpath(p),
    )
    make_proc_process(tmp_path, 41, ["smartctl", "-H", "/dev/disk/by-id/ata-FAKE"], age=30)
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == {"/dev/sda"}

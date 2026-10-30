import os

import statblk
from fakes import make_proc_process


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


def test_comm_with_spaces_and_parenthesis(tmp_path):
    make_proc_process(tmp_path, 41, ["smartctl", "-H", "/dev/sda"], age=30, comm="smart ctl) (x 1")
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == {"/dev/sda"}


def test_unreadable_or_vanished_pid_is_skipped(tmp_path):
    make_proc_process(tmp_path, 41, ["smartctl", "-H", "/dev/sda"], age=30)
    (tmp_path / "42").mkdir()  # exited between listdir and read: no files
    make_proc_process(tmp_path, 43, ["smartctl", "-H", "/dev/sdb"], age=30)
    (tmp_path / "43" / "stat").write_text("garbage")
    make_proc_process(tmp_path, 44, ["smartctl", "-H", "/dev/sdc"], age=30)
    (tmp_path / "44" / "stat").write_text("44 (smartctl) D 1 2")  # truncated
    (tmp_path / "self").mkdir()
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == {"/dev/sda"}


def test_no_proc_is_an_empty_set(tmp_path):
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path / "missing")) == set()
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == set()  # no uptime


def test_by_id_symlink_argument_resolves_to_the_disk(tmp_path, monkeypatch):
    # /dev/disk/by-id/... is a symlink to the disk; the argument is matched by real path.
    real_realpath = os.path.realpath
    monkeypatch.setattr(
        os.path, "realpath",
        lambda p: "/dev/sda" if p == "/dev/disk/by-id/ata-FAKE" else real_realpath(p),
    )
    make_proc_process(tmp_path, 41, ["smartctl", "-H", "/dev/disk/by-id/ata-FAKE"], age=30)
    assert statblk.find_stuck_smartctl(2, proc=str(tmp_path)) == {"/dev/sda"}

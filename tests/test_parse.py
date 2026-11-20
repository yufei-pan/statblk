import os
import subprocess
import sys
from pathlib import Path

import pytest

import statblk
from fakes import LSBLK_PAIRS_SAMPLE


def test_parse_lsblk_pairs_label_with_spaces():
    fields = statblk.parse_lsblk_pairs_line(LSBLK_PAIRS_SAMPLE[0])
    assert fields["NAME"] == "/dev/sda1"
    assert fields["LABEL"] == "boot vol"
    assert fields["SIZE"] == "1073741824"


def test_parse_lsblk_pairs_decodes_hex_escapes():
    # lsblk -P escapes " \\ ` $ and non-printable bytes (incl. UTF-8) as \\xNN.
    fields = statblk.parse_lsblk_pairs_line(
        'NAME="/dev/sdb1" LABEL="say\\x22hi\\x22 \\xe6\\x97\\xa5"'
    )
    assert fields["LABEL"] == 'say"hi" 日'


def test_compile_filter_invalid_regex_exits(capsys):
    with pytest.raises(SystemExit) as ei:
        statblk.compile_filter_pattern(["[unterminated"])
    assert ei.value.code == 1
    assert "Invalid filter pattern" in capsys.readouterr().err


def test_decode_proc_path_space():
    assert statblk._decode_proc_path("/mnt\\040disk") == "/mnt disk"


def test_decode_proc_path_tab_newline_backslash():
    assert statblk._decode_proc_path("/mnt/a\\011b\\012c\\134d") == "/mnt/a\tb\nc\\d"


def test_mountinfo_mountpoint_with_backslash():
    dev, ent = statblk.parse_mountinfo_line(
        "100 99 8:1 / /mnt/back\\134slash rw - ext4 /dev/sdz1 rw"
    )
    assert ent.MOUNTPOINT == "/mnt/back\\slash"


def test_build_symlink_dict_decodes_udev_escapes(tmp_path):
    target = tmp_path / "sdz1"
    target.write_text("")
    by_label = tmp_path / "by-label"
    by_label.mkdir()
    os.symlink(target, by_label / "my\\x20label")
    mapping = statblk.build_symlink_dict(str(by_label))
    assert mapping == {str(target): "my label"}



@pytest.mark.parametrize("line", [
    "Device is in STANDBY mode, exit(2)",
    "Device is in SLEEP mode, exit(2)",
    "Device is in STANDBY_Y mode, exit(2)",
])
def test_parse_smart_health_standby(line):
    # smartctl -n standby skips a spun-down drive instead of waking it.
    assert statblk.parse_smart_health(["smartctl 7.5 2025-04-30 r5714", line]) == "STANDBY"


def test_parse_smart_health_idle_is_not_standby():
    # IDLE drives are still spinning and get checked normally.
    assert statblk.parse_smart_health([
        "Device is in IDLE mode",
        "SMART overall-health self-assessment test result: PASSED",
    ]) == "OK"


def test_mountinfo_source_outside_dev_is_kept_as_written():
    # realpath read the SMB share //server/share as the path /server/share; a /dev source still has its links resolved.
    dev, ent = statblk.parse_mountinfo_line("120 99 0:55 / /mnt/share rw - cifs //server/share rw,vers=3.1.1")
    assert dev == "//server/share" and ent.MOUNTPOINT == "/mnt/share"


@pytest.mark.skipif(sys.platform != "linux", reason="mountinfo is Linux's, and macOS names are UTF-8 only")
def test_mountinfo_mount_point_that_is_not_utf8_reaches_statvfs_intact(tmp_path, monkeypatch):
    # The kernel writes a mount point's bytes as they are; 1.63 read them as UTF-8 and dropped the rest, so statvfs ran
    # on another path (FSUSE% ERROR, and a healthy --check exited 3).
    target = os.path.join(os.fsencode(str(tmp_path)), b"caf\xe9 (latin-1)")
    os.mkdir(target)
    mountinfo = tmp_path / "mountinfo"
    mountinfo.write_bytes(b"100 99 8:1 / " + target.replace(b" ", b"\\040") + b" rw - ext4 /dev/sdz1 rw\n")
    monkeypatch.setattr(statblk, "IS_DARWIN", False)
    monkeypatch.setattr(statblk, "MOUNTINFO_PATH", str(mountinfo))
    (entry,) = statblk.parseMount()["/dev/sdz1"]
    assert os.fsencode(entry.MOUNTPOINT) == target
    assert statblk.get_statvfs_use_size(entry.MOUNTPOINT, timeout=5) is not None


@pytest.mark.skipif(sys.platform != "linux", reason="mountinfo is Linux's")
def test_mountinfo_utf8_mount_point_reaches_statvfs_in_the_c_locale(tmp_path):
    # Python 3.6 in the C locale (EL7 and EL8 under cron) encodes paths as ASCII: a UTF-8 mount point read as UTF-8
    # could not be encoded for statvfs. Read as the filesystem encoding reads paths, it goes back as the same bytes.
    # (Python 3.7 and later take the C locale for UTF-8, where both ways work.)
    target = tmp_path / "caf\u00e9"
    target.mkdir()
    mountinfo = tmp_path / "mountinfo"
    mountinfo.write_bytes(b"100 99 8:1 / " + os.fsencode(str(target)) + b" rw - ext4 /dev/sdz1 rw\n")
    code = ("import statblk; statblk.IS_DARWIN = False; statblk.MOUNTINFO_PATH = %r; "
            "(e,) = statblk.parseMount()['/dev/sdz1']; print(statblk.get_statvfs_use_size(e.MOUNTPOINT) is not None)"
            % str(mountinfo))
    env = dict(os.environ, LC_ALL="C", LANG="C", PYTHONPATH=str(Path(statblk.__file__).resolve().parent))
    env.pop("PYTHONUTF8", None)
    out = subprocess.run([sys.executable, "-c", code], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=True)
    assert (out.returncode, out.stdout.strip()) == (0, "True"), out.stderr

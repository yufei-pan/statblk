import os

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

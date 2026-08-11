import pytest

import statblk
from fakes import LSBLK_PAIRS_SAMPLE, LSBLK_RAW_SAMPLE


def test_parse_lsblk_pairs_label_with_spaces():
    name, size, fstype, uuid, label = statblk.parse_lsblk_pairs_line(LSBLK_PAIRS_SAMPLE[0])
    assert name == "/dev/sda1"
    assert label == "boot vol"
    assert size == "1073741824"


def test_parse_lsblk_raw_label_with_spaces():
    name, size, fstype, uuid, label = statblk.parse_lsblk_raw_line(LSBLK_RAW_SAMPLE[0])
    assert label == "boot vol"
    assert fstype == "ext4"


def test_parse_lsblk_raw_short_line():
    name, size, fstype, uuid, label = statblk.parse_lsblk_raw_line("/dev/sda 100")
    assert (name, size, fstype, uuid, label) == ("/dev/sda", "100", "", "", "")


def test_compile_filter_invalid_regex_exits(capsys):
    with pytest.raises(SystemExit) as ei:
        statblk.compile_filter_pattern(["[unterminated"])
    assert ei.value.code == 1
    assert "Invalid filter pattern" in capsys.readouterr().err


def test_decode_proc_path_space():
    assert statblk._decode_proc_path("/mnt\\040disk") == "/mnt disk"

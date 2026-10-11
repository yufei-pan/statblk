import json

import pytest

import statblk

HEADER = ["NAME", "FSUSE%", "SMART"]


@pytest.mark.parametrize("use, flagged", [("89%", False), ("90%", True), ("91%", True)])
def test_fsuse_threshold_boundary(use, flagged):
    rows = [HEADER, ["sda1", use, "OK"]]
    assert statblk.check_rows(rows, 90) == ((rows, 1) if flagged else ([HEADER], 0))


@pytest.mark.parametrize("row", [
    ["nfs", "TIMEOUT", ""],  # hung mount
    ["sdb", "", "TIMEOUT"],  # smartctl stuck on the disk
    ["sdc", "", "FAILED!"],
    ["sdd", "", "HARDWARE IMPENDING FAILURE GENERAL HARD DRIVE FAILURE"],
])
def test_problem_values_flagged(row):
    assert statblk.check_rows([HEADER, row], 90) == ([HEADER, row], 1)


@pytest.mark.parametrize("row", [
    ["loop0", "", ""],  # virtual device: no SMART to read
    ["sda1", "N/A", "OK"],
    ["sda2", "10%", "OK"],
])
def test_healthy_values_ignored(row):
    assert statblk.check_rows([HEADER, row], 90) == ([HEADER], 0)


@pytest.mark.parametrize("smart", ["NO SMARTCTL", "UNKNOWN", "DENIED"])
def test_unreadable_smart_is_unknown(smart):
    row = ["sda", "10%", smart]
    assert statblk.check_rows([HEADER, row], 90) == ([HEADER, row], 3)


def test_problem_beats_unknown_and_both_reported():
    rows = [HEADER, ["sda1", "95%", "OK"], ["sdb", "", "UNKNOWN"], ["sdc", "10%", "OK"]]
    assert statblk.check_rows(rows, 90) == ([HEADER, rows[1], rows[2]], 1)


def test_unknown_row_over_threshold_is_a_problem():
    row = ["sda1", "95%", "DENIED"]
    assert statblk.check_rows([HEADER, row], 90) == ([HEADER, row], 1)


def test_only_problem_rows_kept_in_order():
    rows = [HEADER, ["sda1", "95%", "OK"], ["sda2", "10%", "OK"], ["sdb", "", "FAILED!"]]
    assert statblk.check_rows(rows, 90) == ([HEADER, rows[1], rows[3]], 1)


def test_missing_column_skips_that_check():
    # -x SMART / -x FSUSE% drop the column, which turns that check off.
    assert statblk.check_rows([["NAME", "FSUSE%"], ["sda1", "95%"]], 90) == ([["NAME", "FSUSE%"], ["sda1", "95%"]], 1)
    assert statblk.check_rows([["NAME", "SMART"], ["sda", "FAILED!"]], 90) == ([["NAME", "SMART"], ["sda", "FAILED!"]], 1)
    assert statblk.check_rows([["NAME", "MOUNTPOINT"], ["sda1", "/"]], 90) == ([["NAME", "MOUNTPOINT"]], 0)


def test_empty_rows_unchanged():
    assert statblk.check_rows([], 90) == ([], 0)


CHECK_ROWS = [
    ["NAME", "FSUSE%", "SMART", "MOUNTPOINT"],
    ["sda1", "95%", "OK", "/data"],
    ["sda2", "10%", "OK", "/boot"],
]


def _run_main(monkeypatch, argv, rows=CHECK_ROWS):
    """Run main() with canned rows; return (exit value, gdi kwargs, printed tables)."""
    seen, tables = {}, []
    monkeypatch.setattr(statblk, "get_drives_info", lambda **k: seen.update(k) or [list(r) for r in rows])
    monkeypatch.setattr(statblk.multiCMD, "set_sudo", lambda x: None)
    monkeypatch.setattr(statblk.multiCMD, "pretty_format_table", lambda r, **k: tables.append(r) or "T")
    monkeypatch.setattr(statblk.sys, "argv", argv)
    return statblk.main(), seen, tables


def test_check_prints_problem_rows_and_exits_1(monkeypatch):
    code, _, tables = _run_main(monkeypatch, ["statblk", "--check"])
    assert code == 1
    assert tables == [[CHECK_ROWS[0], CHECK_ROWS[1]]]


def test_check_silent_and_exit_0_when_healthy(monkeypatch, capsys):
    code, _, tables = _run_main(monkeypatch, ["statblk", "--check"], rows=[CHECK_ROWS[0], CHECK_ROWS[2]])
    assert not code
    assert tables == []
    assert capsys.readouterr().out == ""


def test_max_use_threshold(monkeypatch):
    code, _, tables = _run_main(monkeypatch, ["statblk", "--check", "--max_use", "5"])
    assert code == 1
    assert [r[0] for r in tables[0][1:]] == ["sda1", "sda2"]


@pytest.mark.parametrize("argv, output", [
    (["statblk", "--check"], "all"),
    (["statblk", "--check", "-o", "NAME"], "NAME,FSUSE%,SMART"),
    (["statblk", "--check", "-o", "NAME,smart"], "NAME,smart,FSUSE%"),
    (["statblk", "--check", "-o", "NAME", "-x", "SMART"], "NAME,FSUSE%"),
    (["statblk", "-o", "NAME"], "NAME"),  # no --check: untouched
])
def test_check_adds_check_columns(monkeypatch, argv, output):
    _, seen, _ = _run_main(monkeypatch, argv)
    assert seen["output"] == output


def test_check_json_objects(monkeypatch, capsys):
    code, _, _ = _run_main(monkeypatch, ["statblk", "--check", "-J"])
    assert code == 1
    assert [o["NAME"] for o in json.loads(capsys.readouterr().out)] == ["sda1"]


@pytest.mark.parametrize("flag, expected", [("-J", []), ("-j", [CHECK_ROWS[0]])])
def test_check_json_when_healthy(monkeypatch, capsys, flag, expected):
    code, _, _ = _run_main(monkeypatch, ["statblk", "--check", flag], rows=[CHECK_ROWS[0], CHECK_ROWS[2]])
    assert not code
    assert json.loads(capsys.readouterr().out) == expected


@pytest.mark.parametrize("argv", [["statblk", "--check", "-w", "5"], ["statblk", "--check", "5"]])
def test_check_rejects_watch(monkeypatch, capsys, argv):
    with pytest.raises(SystemExit) as exc:
        _run_main(monkeypatch, argv)
    assert exc.value.code == 2
    assert "--check runs once" in capsys.readouterr().err


UNKNOWN_ROWS = [
    ["NAME", "FSUSE%", "SMART", "MOUNTPOINT"],
    ["sda1", "10%", "NO SMARTCTL", "/data"],
    ["loop1", "10%", "", "/mnt/image"],
]


def test_check_unknown_exits_3_and_lists_rows(monkeypatch):
    code, _, tables = _run_main(monkeypatch, ["statblk", "--check"], rows=UNKNOWN_ROWS)
    assert code == 3
    assert tables == [[UNKNOWN_ROWS[0], UNKNOWN_ROWS[1]]]


def test_check_unknown_json_objects(monkeypatch, capsys):
    code, _, _ = _run_main(monkeypatch, ["statblk", "--check", "-J"], rows=UNKNOWN_ROWS)
    assert code == 3
    assert [(o["NAME"], o["SMART"]) for o in json.loads(capsys.readouterr().out)] == [("sda1", "NO SMARTCTL")]


def test_check_exclude_smart_is_space_only(monkeypatch):
    # get_drives_info drops the excluded column, so no row can be "unknown".
    rows = [["NAME", "FSUSE%"], ["sda1", "10%"]]
    code, seen, tables = _run_main(monkeypatch, ["statblk", "--check", "-x", "SMART"], rows=rows)
    assert seen["exclude"] == "SMART" and seen["output"] == "all"
    assert not code and tables == []

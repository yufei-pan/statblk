import json

import pytest

import statblk


def test_watch_flag_and_trailing_int(monkeypatch):
    calls = []

    def fake_gdi(**kwargs):
        calls.append(kwargs.get("filter_patterns"))
        return [["NAME"], ["sda"]]

    sleeps = []

    monkeypatch.setattr(statblk, "get_drives_info", fake_gdi)
    monkeypatch.setattr(statblk.multiCMD, "set_sudo", lambda x: None)
    monkeypatch.setattr(statblk.multiCMD, "pretty_format_table", lambda r, **k: "TABLE")
    monkeypatch.setattr(statblk.time, "sleep", lambda s: sleeps.append(s) or (_ for _ in ()).throw(KeyboardInterrupt()))

    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "-w", "5", "sda"])
    statblk.main()
    assert sleeps == [5]
    assert calls[0] == ["sda"]

    sleeps.clear()
    calls.clear()
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "sda", "3"])
    monkeypatch.setattr(statblk.time, "sleep", lambda s: sleeps.append(s) or (_ for _ in ()).throw(KeyboardInterrupt()))
    statblk.main()
    assert sleeps == [3]
    assert calls[0] == ["sda"]


def test_watch_flag_wins_over_trailing(monkeypatch):
    sleeps = []
    monkeypatch.setattr(statblk, "get_drives_info", lambda **k: [["NAME"], ["x"]])
    monkeypatch.setattr(statblk.multiCMD, "set_sudo", lambda x: None)
    monkeypatch.setattr(statblk.multiCMD, "pretty_format_table", lambda r, **k: "T")
    monkeypatch.setattr(statblk.time, "sleep", lambda s: sleeps.append(s) or (_ for _ in ()).throw(KeyboardInterrupt()))
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "-w", "5", "sda", "9"])
    statblk.main()
    assert sleeps == [5]


def test_trailing_zero_is_not_watch(monkeypatch):
    sleeps = []
    patterns = []

    def fake_gdi(**kwargs):
        patterns.append(kwargs.get("filter_patterns"))
        return [["NAME"], ["nvme0"]]

    monkeypatch.setattr(statblk, "get_drives_info", fake_gdi)
    monkeypatch.setattr(statblk.multiCMD, "set_sudo", lambda x: None)
    monkeypatch.setattr(statblk.multiCMD, "pretty_format_table", lambda r, **k: "T")
    monkeypatch.setattr(statblk.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "nvme0", "0"])
    statblk.main()
    assert sleeps == []
    assert patterns[0] == ["nvme0"]


def test_version(monkeypatch, capsys):
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "-V"])
    with pytest.raises(SystemExit) as ei:
        statblk.main()
    assert ei.value.code == 0
    assert statblk.version in capsys.readouterr().out


def test_json_output(monkeypatch, capsys):
    monkeypatch.setattr(statblk, "get_drives_info", lambda **k: [["NAME"], ["sda"]])
    monkeypatch.setattr(statblk.multiCMD, "set_sudo", lambda x: None)
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "-j"])
    statblk.main()
    data = json.loads(capsys.readouterr().out)
    assert data[0] == ["NAME"]


def _sleep_once_then_interrupt():
    calls = []

    def sleep(s):
        calls.append(s)
        if len(calls) > 1:
            raise KeyboardInterrupt()

    return sleep


@pytest.mark.parametrize("darwin, expected", [
    (False, [False, True]),  # Linux: auto-enable after first refresh
    (True, [False, False]),  # macOS: no throughput data, so never auto-enable
])
def test_watch_auto_active_only(monkeypatch, darwin, expected):
    seen = []

    def fake_gdi(**kwargs):
        seen.append(kwargs["active_only"])
        return [["NAME"], ["disk0"]]

    monkeypatch.setattr(statblk, "IS_DARWIN", darwin)
    monkeypatch.setattr(statblk, "get_drives_info", fake_gdi)
    monkeypatch.setattr(statblk.multiCMD, "set_sudo", lambda x: None)
    monkeypatch.setattr(statblk.multiCMD, "pretty_format_table", lambda r, **k: "T")
    monkeypatch.setattr(statblk.time, "sleep", _sleep_once_then_interrupt())
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "-w", "1"])
    statblk.main()
    assert seen == expected


def _patch_main_basics(monkeypatch, gdi):
    monkeypatch.setattr(statblk, "get_drives_info", gdi)
    monkeypatch.setattr(statblk.multiCMD, "set_sudo", lambda x: None)
    monkeypatch.setattr(statblk.multiCMD, "pretty_format_table", lambda r, **k: "T")


def test_ctrl_c_during_refresh_exits_130(monkeypatch):
    def interrupted_gdi(**kwargs):
        raise KeyboardInterrupt()

    _patch_main_basics(monkeypatch, interrupted_gdi)
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "-w", "1"])
    assert statblk.main() == 130


def test_ctrl_c_during_sleep_exits_130(monkeypatch):
    _patch_main_basics(monkeypatch, lambda **k: [["NAME"]])
    monkeypatch.setattr(statblk.time, "sleep", lambda s: (_ for _ in ()).throw(KeyboardInterrupt()))
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "-w", "1"])
    assert statblk.main() == 130


def test_single_run_returns_success(monkeypatch):
    _patch_main_basics(monkeypatch, lambda **k: [["NAME"]])
    monkeypatch.setattr(statblk.sys, "argv", ["statblk"])
    assert not statblk.main()


class _ClosedPipe:
    def write(self, _s):
        raise BrokenPipeError()

    def flush(self):
        raise BrokenPipeError()

    def fileno(self):
        raise OSError("no fd")


def test_broken_pipe_exits_quietly(monkeypatch):
    _patch_main_basics(monkeypatch, lambda **k: [["NAME"]])
    monkeypatch.setattr(statblk.sys, "stdout", _ClosedPipe())
    monkeypatch.setattr(statblk.sys, "argv", ["statblk"])
    assert statblk.main() == 1


def test_json_objects_output(monkeypatch, capsys):
    seen = {}

    def fake_gdi(**kwargs):
        seen.update(kwargs)
        return [
            ["NAME", "SIZE", "FSUSE%", "READ", "WRITE", "MOUNTPOINT"],
            ["sda1", "1000", "35%", "512", "0", "/data"],
            ["sda2", "2000", "", "", "", ""],
            ["host:/export", "", "TIMEOUT", "", "", "/mnt/gone"],
        ]

    _patch_main_basics(monkeypatch, fake_gdi)
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "-J"])
    statblk.main()
    assert seen["print_bytes"] is True  # raw byte counts regardless of -b
    assert json.loads(capsys.readouterr().out) == [
        {"NAME": "sda1", "SIZE": 1000, "FSUSE%": 35, "READ": 512, "WRITE": 0, "MOUNTPOINT": "/data"},
        {"NAME": "sda2", "SIZE": 2000, "FSUSE%": None, "READ": None, "WRITE": None, "MOUNTPOINT": ""},
        {"NAME": "host:/export", "SIZE": None, "FSUSE%": None, "READ": None, "WRITE": None, "MOUNTPOINT": "/mnt/gone"},
    ]


HOSTILE_ROWS = [
    ["NAME", "LABEL", "MOUNTPOINT"],
    # A USB stick label / mount path can carry terminal control sequences.
    ["sdz1", "\x1b]0;pwned\x07\x1b[2J", "/mnt/a\nb‮"],
]


def test_table_output_escapes_control_characters(monkeypatch, capsys):
    real_table = statblk.multiCMD.pretty_format_table
    _patch_main_basics(monkeypatch, lambda **k: [list(r) for r in HOSTILE_ROWS])
    monkeypatch.setattr(statblk.multiCMD, "pretty_format_table", real_table)
    monkeypatch.setattr(statblk.sys, "argv", ["statblk"])
    statblk.main()
    out = capsys.readouterr().out
    assert not any(c in out for c in "\x1b\x07‮")
    assert "\\x1b]0;pwned\\x07\\x1b[2J" in out
    assert "/mnt/a\\x0ab\\u202e" in out


def test_json_output_keeps_values_but_no_raw_control_characters(monkeypatch, capsys):
    _patch_main_basics(monkeypatch, lambda **k: [list(r) for r in HOSTILE_ROWS])
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "-j"])
    statblk.main()
    out = capsys.readouterr().out
    assert "\x1b" not in out
    assert json.loads(out)[1] == HOSTILE_ROWS[1]


SPARSE_ROWS = [
    ["NAME", "SMART", "LABEL", "MOUNTPOINT"],
    ["sda1", "OK", "", "/data"],
    ["sda2", "OK", "", ""],
]


def _captured_table(monkeypatch, argv, rows=SPARSE_ROWS):
    tables = []
    _patch_main_basics(monkeypatch, lambda **k: [list(r) for r in rows])
    monkeypatch.setattr(statblk.multiCMD, "pretty_format_table", lambda r, **k: tables.append(r) or "T")
    monkeypatch.setattr(statblk.sys, "argv", argv)
    statblk.main()
    return tables[0]


def test_table_hides_empty_columns_by_default(monkeypatch):
    assert _captured_table(monkeypatch, ["statblk"]) == [
        ["NAME", "SMART", "MOUNTPOINT"],
        ["sda1", "OK", "/data"],
        ["sda2", "OK", ""],
    ]


def test_table_hides_empty_columns_with_exclude(monkeypatch):
    assert _captured_table(monkeypatch, ["statblk", "-x", "SMART"])[0] == ["NAME", "SMART", "MOUNTPOINT"]


@pytest.mark.parametrize("argv", [
    ["statblk", "--show_empty_columns"],
    ["statblk", "-o", "NAME,SMART,LABEL,MOUNTPOINT"],  # explicitly asked for LABEL
])
def test_table_keeps_empty_columns_when_asked(monkeypatch, argv):
    assert _captured_table(monkeypatch, argv) == SPARSE_ROWS


def test_table_keeps_header_when_no_rows(monkeypatch):
    assert _captured_table(monkeypatch, ["statblk"], rows=[SPARSE_ROWS[0]]) == [SPARSE_ROWS[0]]


@pytest.mark.parametrize("flag", ["-j", "-J"])
def test_json_keeps_empty_columns(monkeypatch, capsys, flag):
    _patch_main_basics(monkeypatch, lambda **k: [list(r) for r in SPARSE_ROWS])
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", flag])
    statblk.main()
    data = json.loads(capsys.readouterr().out)
    assert "LABEL" in data[0]  # header row for -j, first object's keys for -J

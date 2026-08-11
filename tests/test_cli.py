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

import json
import re
import socket

import pytest

import statblk

ROWS = [["NAME", "READ"], ["sda", "1 MiB/s"]]
CLEAR = "\x1b[H\x1b[J"


def _run(monkeypatch, argv, tty=False, refreshes=2):
    """Run main() for up to `refreshes` refreshes; return (sleeps, get_drives_info kwargs).

    Needs capsys active so sys.stdout is the capture object whose isatty is patched.
    """
    sleeps, calls = [], []

    def sleep(s):
        sleeps.append(s)
        if len(sleeps) >= refreshes:
            raise KeyboardInterrupt()

    monkeypatch.setattr(statblk, "get_drives_info", lambda **k: calls.append(k) or [list(r) for r in ROWS])
    monkeypatch.setattr(statblk.multiCMD, "set_sudo", lambda x: None)
    monkeypatch.setattr(statblk.multiCMD, "pretty_format_table", lambda r, **k: "TABLE")
    monkeypatch.setattr(statblk.time, "sleep", sleep)
    monkeypatch.setattr(statblk.sys.stdout, "isatty", lambda: tty)
    monkeypatch.setattr(statblk.sys, "argv", argv)
    statblk.main()
    return sleeps, calls


def _header_re(interval):
    return re.compile(rf"^Every {re.escape(interval)} on {re.escape(socket.gethostname())}: \d{{4}}-\d\d-\d\d \d\d:\d\d:\d\d$", re.M)


def test_watch_prints_header_each_refresh(monkeypatch, capsys):
    _run(monkeypatch, ["statblk", "-w", "2"])
    out = capsys.readouterr().out
    assert len(_header_re("2s").findall(out)) == 2  # "2s", not "2.0s"
    assert CLEAR not in out  # not a terminal: keep every refresh in the log


def test_single_run_has_no_header(monkeypatch, capsys):
    _run(monkeypatch, ["statblk"], tty=True)
    out = capsys.readouterr().out
    assert "Every" not in out and "\x1b" not in out


def test_watch_on_tty_redraws_in_place(monkeypatch, capsys):
    _run(monkeypatch, ["statblk", "-w", "2"], tty=True)
    out = capsys.readouterr().out
    # Clear, header and table go out in one write per refresh.
    assert out.count(CLEAR) == 2
    assert all(chunk.startswith("Every 2s on ") for chunk in out.split(CLEAR)[1:])


def test_fractional_watch_interval(monkeypatch, capsys):
    sleeps, _ = _run(monkeypatch, ["statblk", "-w", "0.5"])
    assert sleeps == [0.5, 0.5]
    assert len(_header_re("0.5s").findall(capsys.readouterr().out)) == 2


def test_fractional_timeout(monkeypatch, capsys):
    _, calls = _run(monkeypatch, ["statblk", "-t", "1.5"])
    assert calls[0]["timeout"] == 1.5


def test_trailing_fraction_stays_a_pattern(monkeypatch, capsys):
    sleeps, calls = _run(monkeypatch, ["statblk", "sda", "0.5"])
    assert sleeps == []
    assert calls[0]["filter_patterns"] == ["sda", "0.5"]


@pytest.mark.parametrize("flag", ["-j", "-J"])
def test_watch_json_is_ndjson(monkeypatch, capsys, flag):
    _run(monkeypatch, ["statblk", "-w", "1", flag], tty=True)
    out = capsys.readouterr().out
    lines = out.splitlines()
    assert len(lines) == 2  # one compact document per refresh
    assert all(json.loads(line) for line in lines)
    assert "Every" not in out and "\x1b" not in out  # machine output: no header or clearing


@pytest.mark.parametrize("flag", ["-j", "-J"])
def test_single_run_json_stays_indented(monkeypatch, capsys, flag):
    _run(monkeypatch, ["statblk", flag])
    out = capsys.readouterr().out
    assert "\n " in out
    json.loads(out)


def _no_lsblk(monkeypatch):
    real_which = statblk.shutil.which
    monkeypatch.setattr(statblk, "IS_DARWIN", False)
    monkeypatch.setattr(statblk.shutil, "which", lambda name, **k: None if name == "lsblk" else real_which(name, **k))


def test_missing_lsblk_noted_once_after_a_single_run(monkeypatch, capsys):
    _no_lsblk(monkeypatch)
    _run(monkeypatch, ["statblk"])
    out, err = capsys.readouterr()
    assert "TABLE" in out
    assert err.count("lsblk not found") == 1 and "util-linux" in err


def test_missing_lsblk_noted_once_when_watch_output_is_piped(monkeypatch, capsys):
    _no_lsblk(monkeypatch)
    _run(monkeypatch, ["statblk", "-w", "2"], refreshes=3)
    assert capsys.readouterr().err.count("lsblk not found") == 1


def test_missing_lsblk_noted_under_every_redrawn_table(monkeypatch, capsys):
    _no_lsblk(monkeypatch)
    _run(monkeypatch, ["statblk", "-w", "2"], tty=True, refreshes=3)
    assert capsys.readouterr().err.count("lsblk not found") == 3


def test_no_lsblk_note_when_lsblk_is_installed(monkeypatch, capsys):
    monkeypatch.setattr(statblk, "IS_DARWIN", False)
    monkeypatch.setattr(statblk.shutil, "which", lambda name, **k: "/usr/bin/" + name)
    _run(monkeypatch, ["statblk", "-w", "2"], tty=True, refreshes=2)
    assert "lsblk" not in capsys.readouterr().err


@pytest.mark.parametrize("flag", ["-j", "-J"])
def test_missing_lsblk_noted_once_in_json_watch_on_a_terminal(monkeypatch, capsys, flag):
    _no_lsblk(monkeypatch)
    _run(monkeypatch, ["statblk", "-w", "2", flag], tty=True, refreshes=3)
    assert capsys.readouterr().err.count("lsblk not found") == 1

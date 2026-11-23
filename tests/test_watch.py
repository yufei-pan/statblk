import json
import re
import socket

import pytest

import statblk

ROWS = [["NAME", "READ", "FSTYPE"], ["sda", "1 MiB/s", "ext4"]]
CLEAR = "\x1b[H\x1b[J"


def _run(monkeypatch, argv, tty=False, refreshes=2, rows=ROWS, cuts=([],), stderr_tty=None):
    """Run main() for up to `refreshes` refreshes; return (sleeps, get_drives_info kwargs).

    tty: whether stdout is a terminal; stderr_tty: whether stderr is (None: the same as stdout, as when both are the
    screen, or both are redirected).
    cuts: what get_drives_info records at each refresh (the last item repeats): a dict of the commands that did not
    answer in full and their return codes, or a list of commands --timeout stopped.

    Needs capsys active so sys.stdout and sys.stderr are the capture objects whose isatty is patched.
    """
    sleeps, calls = [], []

    def sleep(s):
        sleeps.append(s)
        if len(sleeps) >= refreshes:
            raise KeyboardInterrupt()

    def gdi(**k):
        step = cuts[min(len(calls), len(cuts) - 1)]
        k["unanswered"].update(step if isinstance(step, dict) else dict.fromkeys(step, statblk.TIMEOUT_RETURNCODE))
        calls.append(k)
        return [list(r) for r in rows]

    monkeypatch.setattr(statblk, "get_drives_info", gdi)
    monkeypatch.setattr(statblk.multiCMD, "set_sudo", lambda x: None)
    monkeypatch.setattr(statblk.multiCMD, "pretty_format_table", lambda r, **k: "TABLE")
    monkeypatch.setattr(statblk.time, "sleep", sleep)
    monkeypatch.setattr(statblk.sys.stdout, "isatty", lambda: tty)
    if statblk.sys.stderr is not None:
        monkeypatch.setattr(statblk.sys.stderr, "isatty", lambda: tty if stderr_tty is None else stderr_tty)
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


# What get_drives_info records on a host with no lsblk (multiCMD's 127) when FSTYPE, UUID, MODEL or SERIAL is shown
# or collected, or -F needs it.
NO_LSBLK = ({"lsblk": statblk.NOT_FOUND_RETURNCODE},)
LSBLK_NOTE = statblk.cut_note("lsblk", 2, statblk.NOT_FOUND_RETURNCODE)


def test_missing_lsblk_noted_once_after_a_single_run(monkeypatch, capsys):
    _run(monkeypatch, ["statblk"], cuts=NO_LSBLK)
    out, err = capsys.readouterr()
    assert "TABLE" in out
    assert err == LSBLK_NOTE + "\n" and "lsblk not found (it comes with util-linux)" in err


def test_missing_lsblk_noted_once_when_watch_output_is_piped(monkeypatch, capsys):
    _run(monkeypatch, ["statblk", "-w", "2"], refreshes=3, cuts=NO_LSBLK)
    assert capsys.readouterr().err.count("lsblk not found") == 1


def test_missing_lsblk_noted_under_every_redrawn_table(monkeypatch, capsys):
    _run(monkeypatch, ["statblk", "-w", "2"], tty=True, refreshes=3, cuts=NO_LSBLK)
    assert capsys.readouterr().err.count("lsblk not found") == 3


def test_no_note_when_nothing_was_unanswered(monkeypatch, capsys):
    _run(monkeypatch, ["statblk", "-w", "2"], tty=True, refreshes=2)
    assert "lsblk" not in capsys.readouterr().err


@pytest.mark.parametrize("flag", ["-j", "-J"])
def test_missing_lsblk_noted_once_in_json_watch_on_a_terminal(monkeypatch, capsys, flag):
    _run(monkeypatch, ["statblk", "-w", "2", flag], tty=True, refreshes=3, cuts=NO_LSBLK)
    assert capsys.readouterr().err.count("lsblk not found") == 1


def test_no_lsblk_note_for_a_healthy_check(monkeypatch, capsys):
    # --check prints nothing when healthy, and cron mails stderr.
    _run(monkeypatch, ["statblk", "--check"], rows=[["NAME", "FSTYPE", "FSUSE%", "SMART"], ["sda1", "ext4", "10%", "OK"]],
         cuts=NO_LSBLK)
    out, err = capsys.readouterr()
    assert out == "" and err == ""


def test_lsblk_note_with_a_failing_check(monkeypatch, capsys):
    _run(monkeypatch, ["statblk", "--check"], rows=[["NAME", "FSTYPE", "FSUSE%", "SMART"], ["sda1", "ext4", "95%", "OK"]],
         cuts=NO_LSBLK)
    assert capsys.readouterr().err.count("lsblk not found") == 1


def test_missing_lsblk_noted_when_no_row_is_left(monkeypatch, capsys):
    # A pattern may have missed a FSTYPE only lsblk fills: the note says so even when no row is left (1.63 said
    # nothing here for a missing lsblk, and named a stopped one).
    _run(monkeypatch, ["statblk", "ext4"], rows=[["NAME", "FSTYPE"]], cuts=NO_LSBLK)
    assert capsys.readouterr().err == LSBLK_NOTE + "\n"


@pytest.mark.parametrize("returncode, line", [
    (1, "lsblk failed (exit 1): "),
    (127, "lsblk not found (it comes with util-linux): "),
    (124, "lsblk was stopped by -t 2 before it finished: "),
])
def test_the_note_says_how_the_command_did_not_answer(monkeypatch, capsys, returncode, line):
    _run(monkeypatch, ["statblk"], cuts=({"lsblk": returncode},))
    assert capsys.readouterr().err.startswith(line + statblk.LSBLK_LACKS)


def test_no_lsblk_note_when_stderr_is_closed(monkeypatch, capsys):
    # With fd 2 closed sys.stderr is None, and print(file=None) would write the note into stdout (and into -j JSON).
    monkeypatch.setattr(statblk.sys, "stderr", None)
    _run(monkeypatch, ["statblk", "-j"], cuts=NO_LSBLK)
    json.loads(capsys.readouterr().out)


def test_cut_note_once_per_run_when_watch_output_is_piped(monkeypatch, capsys):
    # 1.61 printed none; a line per refresh would fill a log with the same sentence.
    _run(monkeypatch, ["statblk", "-w", "2", "-t", "0.5"], refreshes=3, cuts=(["diskutil", "mount"],))
    err = capsys.readouterr().err
    assert err == statblk.cut_note("diskutil", 0.5) + "\n" + statblk.cut_note("mount", 0.5) + "\n"


def test_cut_note_is_per_command_not_per_run_start(monkeypatch, capsys):
    # A command first cut at a later refresh is still said once, and one cut again later is not repeated.
    _run(monkeypatch, ["statblk", "-w", "2", "-t", "0.5"], refreshes=4, cuts=(["mount"], [], ["mount", "diskutil"], ["mount"]))
    err = capsys.readouterr().err
    assert err.count("mount was stopped") == 1 and err.count("diskutil was stopped") == 1


def test_cut_note_under_every_redrawn_table(monkeypatch, capsys):
    # The next redraw wipes the screen, so the note goes under each table, as the missing-lsblk note does.
    _run(monkeypatch, ["statblk", "-w", "2", "-t", "0.5"], tty=True, refreshes=3, cuts=(["mount"],))
    assert capsys.readouterr().err.count("mount was stopped") == 3


@pytest.mark.parametrize("cuts, line", [(NO_LSBLK, "lsblk not found"), ((["mount"],), "mount was stopped")],
                         ids=["not found", "stopped"])
def test_note_once_per_run_when_stderr_is_not_the_redrawn_terminal(monkeypatch, capsys, cuts, line):
    # `statblk -w 2 2>>log` on a terminal: the redraw clears the screen, not the log, so the note goes there once
    # (1.64 wrote it on every refresh).
    _run(monkeypatch, ["statblk", "-w", "2", "-t", "0.5"], tty=True, refreshes=3, cuts=cuts, stderr_tty=False)
    out, err = capsys.readouterr()
    assert out.count(CLEAR) == 3 and err.count(line) == 1

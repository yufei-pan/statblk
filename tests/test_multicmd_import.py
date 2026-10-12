import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("installed_version, uses_installed", [
    ("1.53", True),
    ("1.100", True),   # float('1.100') == 1.1 would wrongly reject it
    ("2.0", True),
    ("1.52", False),   # older than the embedded copy
    ("1.5", False),    # minor 5 < 53, though float('1.5') > 1.47
    ("garbage", False),
    (None, False),     # module without a version attribute
])
def test_installed_multicmd_used_only_if_not_older_than_embedded(tmp_path, installed_version, uses_installed):
    fake = "INSTALLED = True\n"
    if installed_version is not None:
        fake += f"version = {installed_version!r}\n"
    (tmp_path / "multiCMD.py").write_text(fake)
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(tmp_path), str(ROOT)]))
    out = subprocess.run(
        [sys.executable, "-c",
         "import statblk; print(getattr(statblk.multiCMD, 'INSTALLED', False), statblk.multiCMD.version)"],
        cwd=tmp_path, env=env, capture_output=True, text=True, check=True,
    ).stdout.split()
    assert out[0] == str(uses_installed)
    if not uses_installed:
        assert out[1] == "1.53"  # the embedded copy


def test_embedded_multicmd_table_lines_up_cjk_text(tmp_path):
    # The embedded copy sizes table columns in terminal columns: a CJK character takes two.
    (tmp_path / "multiCMD.py").write_text("version = '1.0'\n")  # too old: the embedded copy is used
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(tmp_path), str(ROOT)]))
    out = subprocess.run(
        [sys.executable, "-c",
         "import statblk; print(statblk.multiCMD.pretty_format_table([['name', 'v'], ['中文', '1']], full=True), end='')"],
        cwd=tmp_path, env=env, capture_output=True, check=True,
    ).stdout.decode("utf-8")
    assert out == "name | v\n-----+--\n中文 | 1\n"

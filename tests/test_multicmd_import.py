import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("installed_version, uses_installed", [
    ("1.61", True),
    ("1.100", True),   # float('1.100') == 1.1 would wrongly reject it
    ("2.0", True),
    ("1.60", False),   # older than the embedded copy
    ("1.58", False),   # what statblk 1.60 embedded
    ("1.9", False),    # minor 9 < 61, though float('1.9') > 1.61
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
        cwd=tmp_path, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True,
    ).stdout.split()
    assert out[0] == str(uses_installed)
    if not uses_installed:
        assert out[1] == "1.61"  # the embedded copy


def test_embedded_multicmd_is_used_when_the_installed_one_fails_to_import(tmp_path):
    # Any failure, not only ImportError: a half-upgraded install must not stop the tool.
    (tmp_path / "multiCMD.py").write_text("raise RuntimeError('broken install')\n")
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(tmp_path), str(ROOT)]))
    out = subprocess.run(
        [sys.executable, "-c", "import statblk; print(statblk.multiCMD.version)"],
        cwd=tmp_path, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True,
    ).stdout.split()
    assert out == ["1.61"]

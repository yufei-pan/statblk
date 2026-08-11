import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import statblk  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "live: soft smoke against real host")
    config.addinivalue_line("markers", "live_strict: strict df/lsblk comparisons")


@pytest.fixture(autouse=True)
def _clear_statblk_caches():
    for fn in (statblk.parseMount, statblk.get_macos_diskutil_info):
        clear = getattr(fn, "cache_clear", None)
        if clear:
            clear()
    yield
    for fn in (statblk.parseMount, statblk.get_macos_diskutil_info):
        clear = getattr(fn, "cache_clear", None)
        if clear:
            clear()


def skip_unless_linux_block():
    if sys.platform != "linux":
        pytest.skip("Linux only")
    if not Path("/sys/class/block").is_dir():
        pytest.skip("no /sys/class/block")


def skip_unless_df_lsblk():
    import shutil
    if not shutil.which("df") or not shutil.which("lsblk"):
        pytest.skip("df/lsblk required")

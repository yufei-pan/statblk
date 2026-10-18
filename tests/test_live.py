import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import statblk

try:
	from conftest import skip_unless_df_lsblk, skip_unless_linux_block
except ImportError:
	def skip_unless_linux_block():
		if sys.platform != "linux":
			pytest.skip("Linux only")
		if not Path("/sys/class/block").is_dir():
			pytest.skip("no /sys/class/block")

	def skip_unless_df_lsblk():
		if not shutil.which("df") or not shutil.which("lsblk"):
			pytest.skip("df/lsblk required")


@pytest.mark.live
def test_live_soft_smoke():
	skip_unless_linux_block()
	rows = statblk.get_drives_info(output="NAME,SIZE,MOUNTPOINT", timeout=5)
	assert rows and rows[0][0] == "NAME"
	assert len(rows) >= 2
	for col in rows[0]:
		assert col in statblk.ALL_OUTPUT_FIELDS


@pytest.mark.live_strict
def test_live_strict_fsuse_root_matches_df():
	skip_unless_linux_block()
	skip_unless_df_lsblk()
	rows = statblk.get_drives_info(
		output="NAME,FSUSE%,MOUNTPOINT", mounted_only=True, best_only=True, timeout=5
	)
	root_rows = [r for r in rows[1:] if r[2] == "/"]
	assert root_rows, "no row for mountpoint /"
	statblk_pct = root_rows[0][1]
	df_out = subprocess.check_output(["df", "-P", "/"], universal_newlines=True).strip().splitlines()
	# Filesystem 1024-blocks Used Available Capacity Mounted on
	m = re.search(r"\s(\d+)%\s+/\s*$", df_out[-1])
	assert m, df_out[-1]
	assert statblk_pct == f"{m.group(1)}%"


@pytest.mark.live_strict
def test_live_strict_names_subset_of_lsblk():
	skip_unless_linux_block()
	skip_unless_df_lsblk()
	rows = statblk.get_drives_info(output="NAME", show_zero_size_devices=True, timeout=5)
	names = {r[0].replace("/dev/", "") for r in rows[1:]}
	# -l: no tree glyphs; -a: include empty loops present in sysfs;
	# KNAME + NAME: kernel names (dm-N) and mapper aliases (pve-root, shown for dm).
	lsblk = subprocess.check_output(["lsblk", "-n", "-l", "-a", "-o", "KNAME,NAME"], universal_newlines=True)
	lsblk_names = {name for line in lsblk.splitlines() for name in line.split()}
	assert names <= lsblk_names

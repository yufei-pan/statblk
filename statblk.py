#!/usr/bin/env python3
# requires-python = ">=3.6"
# -*- coding: utf-8 -*-



import os
import re
import stat
from collections import defaultdict, namedtuple
import argparse
import shutil
import subprocess
import multiCMD
import time
try:
	import functools
	import typing
	# Check if functiools.cache is available
	# cache_decorator = functools.cache
	def cache_decorator(user_function):
		def _make_hashable(item):
			if isinstance(item, typing.Mapping):
				# Sort items so that {'a':1, 'b':2} and {'b':2, 'a':1} hash the same
				return tuple(
					( _make_hashable(k), _make_hashable(v) )
					for k, v in sorted(item.items(), key=lambda item: item[0])
				)
			if isinstance(item, (list, set, tuple)):
				return tuple(_make_hashable(e) for e in item)
			# Fallback: assume item is already hashable
			return item
		def decorating_function(user_function):
			# Create the real cached function
			cached_func = functools.lru_cache(maxsize=None)(user_function)
			@functools.wraps(user_function)
			def wrapper(*args, **kwargs):
				# Convert all args/kwargs to hashable equivalents
				hashable_args = tuple(_make_hashable(a) for a in args)
				hashable_kwargs = {
					k: _make_hashable(v) for k, v in kwargs.items()
				}
				# Call the lru-cached version
				return cached_func(*hashable_args, **hashable_kwargs)
			# Expose cache statistics and clear method
			wrapper.cache_info = cached_func.cache_info
			wrapper.cache_clear = cached_func.cache_clear
			return wrapper
		return decorating_function(user_function)
except :
	import sys
	# If lrucache is not available, use a dummy decorator
	print('Warning: functools.lru_cache is not available, multiSSH3 will run slower without cache.',file=sys.stderr)
	def cache_decorator(func):
		return func

version = '1.20'
VERSION = version
__version__ = version
COMMIT_DATE = '2025-09-10'

SMARTCTL_PATH = shutil.which("smartctl")

def read_text(path):
	try:
		with open(path, "r", encoding="utf-8", errors="ignore") as f:
			return f.read().strip()
	except Exception:
		return None

def read_int(path):
	s = read_text(path)
	if s is None:
		return None
	try:
		return int(s)
	except Exception:
		return None

def build_symlink_dict(dir_path):
	"""
	Build map: devname -> token (uuid or label string) using symlinks under
	/dev/disk/by-uuid or /dev/disk/by-label.
	"""
	mapping = {}
	if not os.path.isdir(dir_path):
		return mapping
	try:
		for entry in os.listdir(dir_path):
			p = os.path.join(dir_path, entry)
			try:
				if os.path.islink(p):
					tgt = os.path.realpath(p)
					mapping.setdefault(tgt, entry)
			except Exception:
				continue
	except Exception:
		pass
	return mapping

def get_statvfs_use_size(mountpoint):
	try:
		st = os.statvfs(mountpoint)
		block_size = st.f_frsize if st.f_frsize > 0 else st.f_bsize
		total = st.f_blocks * block_size
		avail = st.f_bavail * block_size
		used = total - avail
		return total, used
	except Exception:
		return 0, 0

@cache_decorator
def read_discard_support(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return 'N/A'
	dmbytes = read_int(os.path.join(sysfs_block_path, "queue", "discard_max_bytes"))
	try:
		if (dmbytes or 0) > 0:
			return 'Yes'
		else:
			return 'No'
	except Exception:
		return 'N/A'

@cache_decorator
def get_parent_device_sysfs(sysfs_block_path):
	"""
	Return the sysfs 'device' directory for this block node (resolves partition
	to its parent device as well).
	"""
	dev_link = os.path.join(sysfs_block_path, "device")
	try:
		return os.path.realpath(dev_link)
	except Exception:
		return dev_link

@cache_decorator
def read_model_and_serial(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return '', ''
	device_path = get_parent_device_sysfs(sysfs_block_path)
	model = read_text(os.path.join(device_path, "model"))
	serial = read_text(os.path.join(device_path, "serial"))
	if serial is None:
		serial = read_text(os.path.join(device_path, "wwid"))
	if model:
		model = " ".join(model.split())
	else:
		model = ''
	if serial:
		serial = " ".join(serial.split())
	else:
		serial = ''
	return model, serial

MountEntry = namedtuple("MountEntry", ["MOUNTPOINT", "FSTYPE", "OPTIONS"])
def parseMount():
	rtn = multiCMD.run_command('mount',timeout=1,quiet=True)
	mount_table = defaultdict(list)
	for line in rtn:
		device_name, _, line = line.partition(' on ')
		mount_point, _, line = line.partition(' type ')
		fstype, _ , options = line.partition(' (')
		options = options.rstrip(')').split(',')
		mount_table[device_name].append(MountEntry(mount_point, fstype, options))
	return mount_table

def get_blocks():
	# get entries in /sys/class/block
	block_devices = []
	for entry in os.listdir("/sys/class/block"):
		if os.path.isdir(os.path.join("/sys/class/block", entry)):
			block_devices.append(f'/dev/{entry}')
	return block_devices

@cache_decorator
def is_block_device(devpath):
	try:
		st_mode = os.stat(devpath).st_mode
		return stat.S_ISBLK(st_mode)
	except Exception:
		return False

def is_partition(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return False
	return os.path.exists(os.path.join(sysfs_block_path, "partition"))

@cache_decorator
def get_partition_parent_name(name):
	if not name:
		return None
	name = os.path.basename(name)
	sysfs_block_path = os.path.realpath(os.path.join('/sys/class/block', name))
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return None
	part_file = os.path.join(sysfs_block_path, "partition")
	if not os.path.exists(part_file):
		return os.path.join('/dev', name) if is_block_device(os.path.join('/dev', name)) else None
	parent = os.path.basename(os.path.dirname(sysfs_block_path))
	return os.path.join('/dev', parent) if parent and parent != name else None

@cache_decorator
def get_sector_size(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return 512
	if get_partition_parent_name(sysfs_block_path):
		sysfs_block_path = os.path.join('/sys/class/block', os.path.basename(get_partition_parent_name(sysfs_block_path)))
	sector_size = read_int(os.path.join(sysfs_block_path, "queue", "hw_sector_size"))
	if sector_size is None:
		sector_size = read_int(os.path.join(sysfs_block_path, "queue", "logical_block_size"))
	return sector_size if sector_size else 512

def get_read_write_rate_throughput_iter(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		while True:
			yield 0, 0
	rx_path = os.path.join(sysfs_block_path, "stat")
	start_time = time.monotonic()
	sector_size = get_sector_size(sysfs_block_path)
	previous_bytes_read = 0
	previous_bytes_written = 0
	try:
		with open(rx_path, "r", encoding="utf-8", errors="ignore") as f:
			fields = f.read().strip().split()
		if len(fields) < 7:
			yield 0, 0
		sectors_read = int(fields[2])
		read_time = int(fields[3]) / 1000.0
		sectors_written = int(fields[6])
		write_time = int(fields[7]) / 1000.0
		read_throughput = (sectors_read * sector_size) / read_time if read_time > 0 else 0
		write_throughput = (sectors_written * sector_size) / write_time if write_time > 0 else 0
		previous_bytes_read = sectors_read * sector_size
		previous_bytes_written = sectors_written * sector_size
		yield int(read_throughput), int(write_throughput)
	except Exception:
		yield 0, 0
	while True:
		try:
			with open(rx_path, "r", encoding="utf-8", errors="ignore") as f:
				fields = f.read().strip().split()
			if len(fields) < 7:
				yield 0, 0
			# fields: https://www.kernel.org/doc/html/latest/block/stat.html
			# 0 - reads completed successfully
			# 1 - reads merged
			# 2 - sectors read
			# 3 - time spent reading (ms)
			# 4 - writes completed
			# 5 - writes merged
			# 6 - sectors written
			# 7 - time spent writing (ms)
			# 8 - I/Os currently in progress
			# 9 - time spent doing I/Os (ms)
			# 10 - weighted time spent doing I/Os (ms)
			sectors_read = int(fields[2])
			sectors_written = int(fields[6])
			bytes_read = sectors_read * sector_size
			bytes_written = sectors_written * sector_size
			end_time = time.monotonic()
			elapsed_time = end_time - start_time
			start_time = end_time
			read_throughput = (bytes_read - previous_bytes_read) / elapsed_time if elapsed_time > 0 else 0
			write_throughput = (bytes_written - previous_bytes_written) / elapsed_time if elapsed_time > 0 else 0
			previous_bytes_read = bytes_read
			previous_bytes_written = bytes_written
			yield int(read_throughput), int(write_throughput)
		except Exception:
			yield 0, 0

# DRIVE_INFO = namedtuple("DRIVE_INFO", 
# 	["NAME", "FSTYPE", "SIZE", "FSUSEPCT", "MOUNTPOINT", "SMART","RTPT",'WTPT', "LABEL", "UUID", "MODEL", "SERIAL", "DISCARD"])
def get_drives_info(print_bytes = False, use_1024 = False, mounted_only=False, best_only=False, formated_only=False, show_zero_size_devices=False,pseudo=False,tptDict = {},full=False):
	lsblk_result = multiCMD.run_command(f'lsblk -brnp -o NAME,SIZE,FSTYPE,UUID,LABEL',timeout=2,quiet=True,wait_for_return=False,return_object=True)
	block_devices = get_blocks()
	smart_infos = {}
	for block_device in block_devices:
		parent_name = get_partition_parent_name(block_device)
		if parent_name:
			if parent_name not in smart_infos:
				smart_infos[parent_name] = multiCMD.run_command(f'{SMARTCTL_PATH} -H {parent_name}',timeout=2,quiet=True,wait_for_return=False,return_object=True)
		if block_device not in tptDict:
			sysfs_block_path = os.path.realpath(os.path.join('/sys/class/block', os.path.basename(block_device)))
			tptDict[block_device] = get_read_write_rate_throughput_iter(sysfs_block_path)
	mount_table = parseMount()
	target_devices = set(block_devices)
	if pseudo:
		target_devices.update(mount_table.keys())
	target_devices = sorted(target_devices)
	uuid_dict = build_symlink_dict("/dev/disk/by-uuid")
	label_dict = build_symlink_dict("/dev/disk/by-label")
	fstype_dict = {}
	size_dict = {}
	lsblk_result.thread.join()
	if lsblk_result.returncode == 0:
		for line in lsblk_result.stdout:
			lsblk_name, lsblk_size, lsblk_fstype, lsblk_uuid, lsblk_label = line.split(' ', 4)
			# the label can be \x escaped, we need to decode it
			lsblk_uuid = bytes(lsblk_uuid, "utf-8").decode("unicode_escape")
			lsblk_fstype = bytes(lsblk_fstype, "utf-8").decode("unicode_escape")
			lsblk_label = bytes(lsblk_label, "utf-8").decode("unicode_escape")
			if lsblk_uuid:
				uuid_dict[lsblk_name] = lsblk_uuid
			if lsblk_fstype:
				fstype_dict[lsblk_name] = lsblk_fstype
			if lsblk_label:
				label_dict[lsblk_name] = lsblk_label
			try:
				size_dict[lsblk_name] = int(lsblk_size)
			except Exception:
				pass
	output = [["NAME", "FSTYPE", "SIZE", "FSUSE%", "MOUNTPOINT", "SMART", "LABEL", "UUID", "MODEL", "SERIAL", "DISCARD","RTPT",'WTPT']]
	for device_name in target_devices:
		if mounted_only and device_name not in mount_table:
			continue
		fstype = ''
		size = ''
		fsusepct = ''
		mountpoint = ''
		smart = ''
		label = ''
		uuid = ''
		model = ''
		serial = ''
		discard = ''
		rtpt = ''
		wtpt = ''
		# fstype, size, fsuse%, mountpoint, rtpt, wtpt, lable, uuid are partition specific
		# smart, model, serial, discard are device specific, and only for block devices
		# fstype, size, fsuse%, mountpoint does not require block device and can have multiple values per device
		if is_block_device(device_name):
			parent_name = get_partition_parent_name(device_name)
			parent_sysfs_path = os.path.realpath(os.path.join('/sys/class/block', os.path.basename(parent_name))) if parent_name else None
			model, serial = read_model_and_serial(parent_sysfs_path)
			discard = read_discard_support(parent_sysfs_path)
			if parent_name in smart_infos and SMARTCTL_PATH:
				smart_info_obj = smart_infos[parent_name]
				smart_info_obj.thread.join()
				for line in smart_info_obj.stdout:
					line = line.lower()
					if "health" in line:
						smartinfo = line.rpartition(':')[2].strip().upper()
						smart = smartinfo.replace('PASSED', 'OK')
						break
					elif "denied" in line:
						smart = 'DENIED'
						break
		if device_name in tptDict:
			try:
				rtpt, wtpt = next(tptDict[device_name])
				if print_bytes:
					rtpt = str(rtpt)
					wtpt = str(wtpt)
				else:
					rtpt = multiCMD.format_bytes(rtpt, use_1024_bytes=use_1024, to_str=True,str_format='.1f') + 'B/s'
					wtpt = multiCMD.format_bytes(wtpt, use_1024_bytes=use_1024, to_str=True,str_format='.1f') + 'B/s'
			except Exception:
				rtpt = ''
				wtpt = ''
		if device_name in label_dict:
			label = label_dict[device_name]
		if device_name in uuid_dict:
			uuid = uuid_dict[device_name]
		mount_points = mount_table.get(device_name, [])
		if best_only:
			if mount_points:
				mount_points = [sorted(mount_points, key=lambda x: len(x.MOUNTPOINT))[0]]
		if mount_points:
			for mount_entry in mount_points:
				fstype = mount_entry.FSTYPE
				if formated_only and not fstype:
					continue
				mountpoint = mount_entry.MOUNTPOINT
				size_bytes, used_bytes = get_statvfs_use_size(mountpoint)
				if size_bytes == 0 and not show_zero_size_devices:
					continue
				fsusepct = f"{int(round(100.0 * used_bytes / size_bytes))}%" if size_bytes > 0 else "N/A"
				if print_bytes:
					size = str(size_bytes)
				else:
					size = multiCMD.format_bytes(size_bytes, use_1024_bytes=use_1024, to_str=True) + 'B'
				if not full:
					device_name = device_name.lstrip('/dev/')
				output.append([device_name, fstype, size, fsusepct, mountpoint, smart, label, uuid, model, serial, discard, rtpt, wtpt])
		else:
			if formated_only and device_name not in fstype_dict:
				continue
			fstype = fstype_dict.get(device_name, '')
			size_bytes = size_dict.get(device_name, 0)
			if size_bytes == 0 and not show_zero_size_devices:
				continue
			if print_bytes:
				size = str(size_bytes)
			else:
				size = multiCMD.format_bytes(size_bytes, use_1024_bytes=use_1024, to_str=True) + 'B'
			if not full:
				device_name = device_name.lstrip('/dev/')
			output.append([device_name, fstype, size, fsusepct, mountpoint, smart, label, uuid, model, serial, discard, rtpt, wtpt])
	return output


def main():
	parser = argparse.ArgumentParser(description="Gather disk and partition info for block devices.")
	parser.add_argument('-j','--json', help="Produce JSON output", action="store_true")
	parser.add_argument('-b','--bytes', help="Print the SIZE column in bytes rather than in a human-readable format", action="store_true")
	parser.add_argument('-H','--si', help="Use powers of 1000 not 1024 for SIZE column", action="store_true")
	parser.add_argument('-F','-fo','--formated_only', help="Show only formated filesystems", action="store_true")
	parser.add_argument('-M','-mo','--mounted_only', help="Show only mounted filesystems", action="store_true")
	parser.add_argument('-B','-bo','--best_only', help="Show only shortest mount point for each device", action="store_true")
	parser.add_argument('-a','--full', help="Show full device information, do not collapse drive info when length > console length", action="store_true")
	parser.add_argument('-P','--pseudo', help="Include pseudo file systems as well (tmpfs / nfs / cifs etc.)", action="store_true")
	parser.add_argument('--show_zero_size_devices', help="Show devices with zero size", action="store_true")
	parser.add_argument('print_period', nargs='?', default=0, type=int, help="If specified as a number, repeat the output every N seconds")
	parser.add_argument('-V', '--version', action='version', version=f"%(prog)s {version} @ {COMMIT_DATE} stat drives by pan@zopyr.us")

	args = parser.parse_args()
	tptDict = {}
	while True:
		results = get_drives_info(print_bytes = args.bytes, use_1024 = not args.si, 
							mounted_only=args.mounted_only, best_only=args.best_only, 
							formated_only=args.formated_only, show_zero_size_devices=args.show_zero_size_devices,
							pseudo=args.pseudo,tptDict=tptDict,full=args.full)
		if args.json:
			import json
			print(json.dumps(results, indent=1))
		else:
			print(multiCMD.pretty_format_table(results,full=args.full))
		if args.print_period > 0:
			try:
				time.sleep(args.print_period)
			except KeyboardInterrupt:
				break
		else:
			break


if __name__ == "__main__":
	main()
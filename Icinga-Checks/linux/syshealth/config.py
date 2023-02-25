"""
"""


high_cpu_percent = 90
low_free_memory_percent = 10
low_free_disk_space = 10

# Dictionary of expected windows volumes with default capacity.
# When the file system is checked we expect the default values to be replaced.
windows_volumes = {'C:\\':0}

# Dictionary of expected mountpoints with default capacity.
# When the file system is checked we expect the default values to be replaced.
oracle_mount_points = {'/u01': 0, '/u02': 0, '/u03': 0, '/u03/backup': 0, '/redo01': 0, '/redo02': 0}

# === Oracle expected return values ===
db_check_positive = 'OK'

RETURN_OK = 0
RETURN_WARN = 1
RETURN_CRITICAL = 2
RETURN_UNKNOWN = 3
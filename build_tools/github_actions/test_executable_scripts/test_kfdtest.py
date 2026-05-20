# Copyright Advanced Micro Devices, Inc.
# SPDX-License-Identifier: MIT

import logging
import os
import platform
import shlex
import subprocess
from pathlib import Path

THEROCK_BIN_DIR = os.getenv("THEROCK_BIN_DIR")
AMDGPU_FAMILIES = os.getenv("AMDGPU_FAMILIES")
os_type = platform.system().lower()

logging.basicConfig(level=logging.INFO)

cwd_dir = Path(THEROCK_BIN_DIR)
environ_vars = os.environ.copy()

# kfdtest should be run via run_kfdtest.sh script which handles
# platform-specific test exclusions from kfdtest.exclude
cmd = ["./run_kfdtest.sh"]

# Additional test exclusions beyond kfdtest.exclude
# These are tests that are known to be flaky or problematic in CI
ADDITIONAL_EXCLUDE = {
    "gfx90a": {
        "linux": [
            "KFDSVMRangeTest.HMMProfilingEvent*",
        ]
    },
    "gfx94X-dcgpu": {
        "linux": [
            "KFDSVMRangeTest.HMMProfilingEvent*",
        ]
    },
    "gfx942": {
        "linux": [
            "KFDSVMRangeTest.HMMProfilingEvent*",
        ]
    },
    "gfx950-dcgpu": {
        "linux": [
            "KFDSVMRangeTest.HMMProfilingEvent*",
        ]
    },
}

# Build additional exclude filter
exclude_tests = []
if (
    AMDGPU_FAMILIES in ADDITIONAL_EXCLUDE
    and os_type in ADDITIONAL_EXCLUDE[AMDGPU_FAMILIES]
):
    exclude_tests = ADDITIONAL_EXCLUDE[AMDGPU_FAMILIES][os_type]

if exclude_tests:
    # Pass additional exclusions to run_kfdtest.sh via -e flag
    exclude_filter = ":".join(exclude_tests)
    cmd.extend(["-e", exclude_filter])

# Check if quick tests are requested
test_type = os.getenv("TEST_TYPE", "standard")

if test_type == "quick":
    # For quick tests, use the core_sws test suite which is a minimal set
    # that tends to succeed consistently
    cmd.extend(["-p", "core_sws"])

logging.info(f"++ Exec [{cwd_dir}]$ {shlex.join(cmd)}")
subprocess.run(cmd, cwd=cwd_dir, check=True, env=environ_vars)

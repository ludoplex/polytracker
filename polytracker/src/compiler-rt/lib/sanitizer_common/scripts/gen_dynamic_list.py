#!/usr/bin/env python
# ===- lib/sanitizer_common/scripts/gen_dynamic_list.py ---------------------===#
#
# Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# ===------------------------------------------------------------------------===#
#
# Generates the list of functions that should be exported from sanitizer
# runtimes. The output format is recognized by --dynamic-list linker option.
# Usage:
#   gen_dynamic_list.py libclang_rt.*san*.a [ files ... ]
#
# ===------------------------------------------------------------------------===#
from __future__ import print_function
import argparse
import os
import re
import subprocess
import sys
import platform

new_delete = {
    "_Znam",
    "_ZnamRKSt9nothrow_t",
    "_Znwm",
    "_ZnwmRKSt9nothrow_t",
    "_Znaj",
    "_ZnajRKSt9nothrow_t",
    "_Znwj",
    "_ZnwjRKSt9nothrow_t",
    "_ZnwmSt11align_val_t",
    "_ZnwmSt11align_val_tRKSt9nothrow_t",
    "_ZnwjSt11align_val_t",
    "_ZnwjSt11align_val_tRKSt9nothrow_t",
    "_ZnamSt11align_val_t",
    "_ZnamSt11align_val_tRKSt9nothrow_t",
    "_ZnajSt11align_val_t",
    "_ZnajSt11align_val_tRKSt9nothrow_t",
    "_ZdaPv",
    "_ZdaPvRKSt9nothrow_t",
    "_ZdlPv",
    "_ZdlPvRKSt9nothrow_t",
    "_ZdaPvm",
    "_ZdlPvm",
    "_ZdaPvj",
    "_ZdlPvj",
    "_ZdlPvSt11align_val_t",
    "_ZdlPvSt11align_val_tRKSt9nothrow_t",
    "_ZdaPvSt11align_val_t",
    "_ZdaPvSt11align_val_tRKSt9nothrow_t",
    "_ZdlPvmSt11align_val_t",
    "_ZdaPvmSt11align_val_t",
    "_ZdlPvjSt11align_val_t",
    "_ZdaPvjSt11align_val_t",
}

versioned_functions = {
    "memcpy",
    "pthread_attr_getaffinity_np",
    "pthread_cond_broadcast",
    "pthread_cond_destroy",
    "pthread_cond_init",
    "pthread_cond_signal",
    "pthread_cond_timedwait",
    "pthread_cond_wait",
    "realpath",
    "sched_getaffinity",
}


def get_global_functions(nm_executable, library):
    functions = []
    nm = os.environ.get("NM", nm_executable)
    nm_proc = subprocess.Popen(
        [nm, library], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    nm_out = nm_proc.communicate()[0].decode().split("\n")
    if nm_proc.returncode != 0:
        raise subprocess.CalledProcessError(nm_proc.returncode, nm)
    func_symbols = ["T", "W"]
    # On PowerPC, nm prints function descriptors from .data section.
    if platform.uname()[4] in ["powerpc", "ppc64"]:
        func_symbols += ["D"]
    for line in nm_out:
        cols = line.split(" ")
        if len(cols) == 3 and cols[1] in func_symbols:
            functions.append(cols[2])
    return functions


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--version-list", action="store_true")
    parser.add_argument("--extra", default=[], action="append")
    parser.add_argument("libraries", default=[], nargs="+")
    parser.add_argument("--nm-executable", required=True)
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    result = []

    all_functions = []
    for library in args.libraries:
        all_functions.extend(get_global_functions(args.nm_executable, library))
    function_set = set(all_functions)
    for func in all_functions:
        # Export new/delete operators.
        if func in new_delete:
            result.append(func)
            continue
        if match := re.match("__interceptor_(.*)", func):
            result.append(func)
            # We have to avoid exporting the interceptors for versioned library
            # functions due to gold internal error.
            orig_name = match[1]
            if orig_name in function_set and (
                args.version_list or orig_name not in versioned_functions
            ):
                result.append(orig_name)
            continue
        # Export sanitizer interface functions.
        if re.match("__sanitizer_(.*)", func):
            result.append(func)

    # Additional exported functions from files.
    for fname in args.extra:
        f = open(fname, "r")
        result.extend(line.rstrip() for line in f)
    # Print the resulting list in the format recognized by ld.
    with open(args.output, "w") as f:
        print("{", file=f)
        if args.version_list:
            print("global:", file=f)
        result.sort()
        for sym in result:
            print(f"  {sym};", file=f)
        if args.version_list:
            print("local:", file=f)
            print("  *;", file=f)
        print("};", file=f)


if __name__ == "__main__":
    main(sys.argv)

#!/usr/bin/env python
# ===- lib/dfsan/scripts/build-libc-list.py ---------------------------------===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
# ===------------------------------------------------------------------------===#
# The purpose of this script is to identify every function symbol in a set of
# libraries (in this case, libc and libgcc) so that they can be marked as
# uninstrumented, thus allowing the instrumentation pass to treat calls to those
# functions correctly.

import os
import subprocess
import sys
from optparse import OptionParser


def defined_function_list(object):
    functions = []
    readelf_proc = subprocess.Popen(
        ["readelf", "-s", "-W", object], stdout=subprocess.PIPE
    )
    readelf = readelf_proc.communicate()[0].decode(errors="replace").split("\n")
    if readelf_proc.returncode != 0:
        raise subprocess.CalledProcessError(readelf_proc.returncode, "readelf")
    # NOTE For something like the ABI if you are stubbing it out you might want locally defined functions
    for line in readelf:
        if (
            (line[31:35] == "FUNC" or line[31:36] == "IFUNC")
            and line[39:44] != "LOCAL"
            and line[55:58] != "UND"
        ):
            function_name = line[59:].split("@")[0]
            functions.append(function_name)
    return functions


p = OptionParser()

"""
p.add_option('--libc-dso-path', metavar='PATH',
             help='path to libc DSO directory',
             default='/lib/x86_64-linux-gnu')
p.add_option('--libc-archive-path', metavar='PATH',
             help='path to libc archive directory',
             default='/usr/lib/x86_64-linux-gnu')

p.add_option('--libgcc-dso-path', metavar='PATH',
             help='path to libgcc DSO directory',
             default='/lib/x86_64-linux-gnu')
p.add_option('--libgcc-archive-path', metavar='PATH',
             help='path to libgcc archive directory',
             default='/usr/lib/gcc/x86_64-linux-gnu/4.6')

p.add_option('--with-libstdcxx', action='store_true',
             dest='with_libstdcxx',
             help='include libstdc++ in the list (inadvisable)')
p.add_option('--libstdcxx-dso-path', metavar='PATH',
             help='path to libstdc++ DSO directory',
             default='/usr/lib/x86_64-linux-gnu')
"""

(options, args) = p.parse_args()
# libs = glob.glob("/polytracker/the_klondike/pdfium/out/pdfium/obj/third_party/libjpeg_turbo/simd_asm/*.o")
libs = [sys.argv[1]]
"""
libs = [os.path.join(options.libc_dso_path, name) for name in
        ['ld-linux-x86-64.so.2',
         'libanl.so.1',
         'libBrokenLocale.so.1',
         'libcidn.so.1',
         'libcrypt.so.1',
         'libc.so.6',
         'libdl.so.2',
         'libm.so.6',
         'libnsl.so.1',
         'libpthread.so.0',
         'libresolv.so.2',
         'librt.so.1',
         'libthread_db.so.1',
         'libutil.so.1']]

libs += [os.path.join(options.libc_archive_path, name) for name in
         ['libc_nonshared.a',
          'libpthread_nonshared.a']]

libs.append(os.path.join(options.libgcc_dso_path, 'libgcc_s.so.1'))
libs.append(os.path.join(options.libgcc_archive_path, 'libgcc.a'))

if options.with_libstdcxx:
  libs.append(os.path.join(options.libstdcxx_dso_path, 'libstdc++.so.6'))
"""
functions = []
for lib in libs:
    if os.path.exists(lib):
        functions += defined_function_list(lib)
    else:
        sys.stderr.write("warning: library %s not found\n" % lib)

functions = sorted(set(functions))
for f in functions:
    f = f.replace("dfsw$", "")
    f = f.replace("dfs$", "")
    print(f"fun:{f}=uninstrumented")
    print(f"fun:{f}=discard")

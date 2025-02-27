import subprocess
import sys


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


def undefined_function_list(object):
    functions = []
    readelf_proc = subprocess.Popen(
        ["readelf", "-s", "-W", object], stdout=subprocess.PIPE
    )
    readelf = readelf_proc.communicate()[0].decode(errors="replace").split("\n")
    if readelf_proc.returncode != 0:
        raise subprocess.CalledProcessError(readelf_proc.returncode, "readelf")
    # NOTE For something like the ABI if you are stubbing it out you might want locally defined functions
    for line in readelf:
        if (line[31:35] == "FUNC" or line[31:36] == "IFUNC") and "UND" in line:
            function_name = line[59:].split("@")[0]
            functions.append(function_name)
    return functions


cxx_lib = sys.argv[1]
cxx_abi = sys.argv[2]

cxx_funcs = defined_function_list(cxx_lib)
cxx_undef = undefined_function_list(cxx_lib)
abi_funcs = defined_function_list(cxx_abi)
abi_undef = undefined_function_list(cxx_abi)

all_def = cxx_funcs + abi_funcs

all_undef = [func for func in cxx_undef if func not in abi_funcs]
all_undef += abi_funcs

functions = sorted(set(all_undef))
print("#### ALL FUNCS NOT DEF IN LIBCXX THAT ARE NOT IN LIBCXXABI ####")
for f in functions:
    f = f.replace("dfsw$", "")
    f = f.replace("dfs$", "")
    print(f"fun:{f}=uninstrumented")
    print(f"fun:{f}=discard")

functions = sorted(set(abi_funcs))
print("######## GENERATED ABI IGNORE #########")
for f in functions:
    f = f.replace("dfsw$", "")
    f = f.replace("dfs$", "")
    print(f"fun:{f}=uninstrumented")
    print(f"fun:{f}=discard")

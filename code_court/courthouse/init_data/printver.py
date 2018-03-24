"""Prints out the version numbers of the languages in the executor in JSON"""

import json
import subprocess

def main():
    version_commands = {
        "python": ["python3", "-V"],
        "python2": ["python2", "-V"],
        "perl": ["perl", "-e print$];"],
        "lua": ["lua", "-v"],
        "nodejs": ["node", "-v"],
        "guile": ["guile", "--version"],
        "fortran": ["gcc", "-dumpversion"],
        "c": ["gcc", "-dumpversion"],
        "c++": ["gcc", "-dumpversion"],
        "java": ["java", "-version"],
        "ruby": ["ruby", "-v"],
        "rust": ["rustc", "-V"]
    }

    versions = {}

    for lang, command in version_commands.items():
        if lang == "lua" or lang == "guile" or lang == "java" or lang == "rust" or lang == "ruby":
            versions[lang] = get_version(subprocess.check_output(command, stderr=subprocess.STDOUT).decode("utf-8").strip())
        else:
            versions[lang] = subprocess.check_output(command, stderr=subprocess.STDOUT).decode("utf-8").strip()

    print(json.dumps(versions))

def get_version(string):
    i = 0
    while string[i].isdigit() == False:
        i += 1
    for j in range(i, len(string)):
        if(string[j] == " " or string[j] == "\'" or string[j] == "\"" or string[j] == '\n'):
            break
    return string[i:j].strip()

main()

#Prints out the version numbers of the langauges in the executor in JSON

import subprocess
import json

def main():

    lua_ver = subprocess.check_output(["lua", "-v"], stderr=subprocess.STDOUT).decode("utf-8")
    scheme_ver = subprocess.check_output(["guile", "--version"], stderr=subprocess.STDOUT).decode("utf-8")
    java_ver = subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT).decode("utf-8")
    ruby_ver = subprocess.check_output(["ruby", "-v"], stderr=subprocess.STDOUT).decode("utf-8")
    rust_ver = subprocess.check_output(["rustc", "-V"], stderr=subprocess.STDOUT).decode("utf-8")

    #print(lua_ver)
    #print(scheme_ver)
    #print(java_ver)
    #print(ruby_ver)    

    print(json.dumps({
    "python": subprocess.check_output(["python3", "-V"], stderr=subprocess.STDOUT).decode("utf-8").strip(),
    "python2": subprocess.check_output(["python2", "-V"], stderr=subprocess.STDOUT).decode("utf-8").strip(),
    "perl": subprocess.check_output(["perl", "-e print$];"], stderr=subprocess.STDOUT).decode("utf-8").strip(),
    "lua": get_version(lua_ver),
    "nodejs": subprocess.check_output(["node", "-v"], stderr=subprocess.STDOUT).decode("utf-8").strip(),
    "guile": get_version(scheme_ver),
    "fortran": subprocess.check_output(["gcc", "-dumpversion"], stderr=subprocess.STDOUT).decode("utf-8").strip(),
    "c": subprocess.check_output(["gcc", "-dumpversion"], stderr=subprocess.STDOUT).decode("utf-8").strip(),
    "c++": subprocess.check_output(["gcc", "-dumpversion"], stderr=subprocess.STDOUT).decode("utf-8").strip(),
    "java": get_version(java_ver),
    "ruby": get_version(ruby_ver),
    "rust": get_version(rust_ver)}))


def get_version(string):
    i = 0
    while(string[i].isdigit() == False):
        i += 1
    for j in range(i, len(string)):
        if(string[j] == " " or string[j] == "\'" or string[j] == "\"" or string[j] == '\n'):
            break
    return string[i:j].strip()

main()

## Setup for Windows

## Courthouse setup
The courthouse contains the admin interface and acts as the central coordinating
server for the system. All database access goes through the courthouse, mostly by
using its api (code is in courthouse/views/api.py)

```bash
# Create a virtualenv for the courthouse
cd code_court/code_court/courthouse
py -m venv env

# Activate the virtual environment server
.\env\Scripts\activate

# Install the courthouse python dependencies
pip install -r requirements.txt
```

Note: If you get this error,
```bash
Error: pg_config executable not found.

    Please add the directory containing pg_config to the PATH
    or specify the full executable path with the option:

        python setup.py build_ext --pg-config /path/to/pg_config build ...

    or with the pg_config option in 'setup.cfg'.
```
then remove these lines from the requirements.txt:
```bash
py-postgresql==1.2.1
psycopg2==2.7.3.1
```
Note: If you get this error,
```bash
Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "C:\Users\colli\AppData\Local\Temp\pip-install-l59j4i5s\uWSGI\setup.py", line 3, in <module>
        import uwsgiconfig as uc
      File "C:\Users\colli\AppData\Local\Temp\pip-install-l59j4i5s\uWSGI\uwsgiconfig.py", line 8, in <module>
        uwsgi_os = os.uname()[0]
    AttributeError: module 'os' has no attribute 'uname'
```
then remove `uWSGI==2.0.15` from the requirements.txt.

Note: If you get this error,
```bash
Could not find function xmlCheckVersion in library libxml2. Is libxml2 installed?
```
then download lxml-4.2.4-cp37-cp37m-win32.whl from https://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml.

Then run:
```bash
pip install C:\path\to\downloaded\file\lxml-4.2.4-cp37-cp37m-win32.whl
```
Then remove `lxml==3.7.2` from the requirements.txt file.

Note: If you get an error about pycrypto, then there are several steps to getting this to work.
You will want to download to pycrypto binary at http://www.voidspace.org.uk/downloads/pycrypto26/pycrypto-2.6.win-amd64-py3.3.exe.
You will need to download Python 3.3.x in order to install the pycrypto package.
Once it installs, copy the `site-package` `Crypto` folder from the 3.3.x Python installation folder to your virtual envrionment's `site-package` folder.
Then remove `pycrypto==2.6.1` from requirements.txt.

Whenever you delete dependencies from the requirements.txt file, make sure to run the pip installation on the requirements.txt file
until you go through the whole thing without errors.

Now you are ready to run the start.sh file.  Windows does not have bash.exe. In order to get it you must download a bunch
of linux-tools from http://win-bash.sourceforge.net/.  In the zip file, there is bash.exe.  Extract bash.exe and all the linux tools wherever you want
and make sure that the directory you extract it to is in your PATH.

To run the start.sh script successfully, you will need to use the uwsgi command from linux. Unfortunately, this is not linux.
You will have to install Cygwin from https://www.cygwin.com/.

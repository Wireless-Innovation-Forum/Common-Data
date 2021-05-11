# Winnforum propagation models

This folder holds the Winnforum-approved propagation models, currently:
 - `itm`: The ITM (Longley-Rice) model
 - `ehata`: The NTIA Extended-Hata model
 
These implementations are derived from the original ITS/NTIA C++ source code
with minimal modifications when required.

They are wrapped as python extension modules and these models needs to be compiled.

## Compilation in Linux

A Python wrapper is provided to generate a Python extension module.
To build this extension, use the make command:

    `make all`
    
which basically runs:

    `python setup.py build_ext --inplace`


## Compilation in Windows

The easiest way is to to use the MinGW GCC port for Windows.

### Using gcc provided by MinGW32

Download and install MingW32 from http://www.mingw.org:

 - The download section of this page will redirect you to SourceForge where you can
 download the MinGW installer: `mingw-get-setup.exe`

 - Run the installer and select both the *mingw32-base* and *mingw32-gcc-g++* packages.
 Optionally you can also select the *mingw-developer-toolkit* package to be able to use makefiles.
 
 - After making selections, proceed with installation by choosing Installation->Update Catalog->Review Changes->Apply

 - By default the MinGW will be installed in `C:/MinGW/`.

Configuration:

 - Open a command prompt and make sure the directory `C:/MinGW/bin` is in the Windows path, by typing: `PATH`
 
 - If not, add it either:
 
   + in the global path settings, under Control Panel => System => Advanced System Settings => Environment Variables
   + or directly in your working command prompt, as the leading directory:
     `set PATH=C:/MinGW/bin;%PATH%`
 
 - If the developer-toolkit package has been installed, you should now be able able to use *make* in the `winnf/propag` directory, as is done for linux. If any issue, you might need to specify the compiler (see below).
 
 - If the developer-toolkit package has not been selected, then you will need to manually call the python distutils commmand on each of the itm/ and ehata/ subdirectories:

```
     python setup.py build_ext --inplace --compiler=mingw32
```
   
   The *--compiler* option may be unnecessary if there is no conflict with other compilers in your system.
   
If during this process, you experience some issues with wrong compiler, or compilation errors, create the file `distutils.cfg` in your PYTHONPATH\Lib\distutils\ directory, holding the following content:

```
    [build]
    compiler=mingw32
```

In case you are using a 64bit version of Python, the previous steps shall be moified to install and use the MinGW 64 bits instead, and compiler directives `compiler=mingw64`

### Using Microsoft VCC compiler

The configuration steps should be similar to the MinGW, except that the compiler directive to be used (if necessary) is `--compiler=msvc`.

If issue with vcvarsall.bat not being found, try to set the following variables in your command terminal:

```
    set MSSDK=1 
    set DISTUTILS_USE_SDK=1
```

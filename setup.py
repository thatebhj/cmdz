# This file is placed in the Public Domain.


"write your own commands"


import os


from setuptools import setup


def read():
    return open("README.rst", "r").read()


def uploadlist(dir):
    upl = []
    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        if file.endswith(".pyc") or file.startswith("__pycache"):
            continue
        print(file)
        d = dir + os.sep + file
        if not os.path.isdir(d):
            upl.append(d)
        else:
            upl.extend(uploadlist(d))
    return upl


setup(
    name="cmdz",
    version="5",
    author="B.H.J. Thate",
    author_email="thatebhj@gmail.com",
    url="http://github.com/thatebhj/cmdz",
    description="write your own commands",
    long_description=read(),
    long_description_content_type="text/x-rst",
    license="Public Domain",
    packages=["cmdz", "modz"],
    include_package_data=True,
    data_files=[
                ("cmdz/modz", uploadlist("modz")),
                ("share/doc/cmdz", ("README.rst",))
               ],
    scripts=["bin/cmdz"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: Public Domain",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python",
        "Intended Audience :: System Administrators",
        "Topic :: Communications :: Chat :: Internet Relay Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
     ],
)

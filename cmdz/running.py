# This file is placed in the Public Domain.
# pylint: disable=C0115,C0116,C0411,C0413,W0212,R0903,W0201,E0402,W0613


"runtime"


import atexit
import importlib
import importlib.util
import os
import readline
import rlcompleter
import sys
import termios
import time
import traceback


from .message import Event, Parsed
from .handler import Handler, Command, scan
from .objects import Default, Object, last, spl, update
from .threads import launch


def __dir__():
    return (
            "Cfg",
            "Console",
            "boot",
            "command",
            "parse",
            'scanner',
            'scandir',
            "wait"
           )


class Config(Default):

    pass


def boot():
    prs = parse()
    if "c" in prs.opts:
        Cfg.console = True
    if "d" in prs.opts:
        Cfg.daemon= True
    if "v" in prs.opts:
        Cfg.verbose = True
    if "w" in prs.opts:
        Cfg.wait = True
    update(Cfg.prs, prs)
    update(Cfg, prs.sets)


def command(cli, txt, event=None):
    evt = (event() if event else Event())
    evt.parse(txt)
    evt.orig = repr(cli)
    cli.handle(evt)
    evt.wait()
    return evt


def include(name, namelist):
    for nme in namelist:
        if nme in name:
            return True
    return False


def listmod(path):
    res = []
    if not os.path.exists(path):
        return res
    for fnm in os.listdir(path):
        if fnm.endswith("~") or fnm.startswith("__"):
            continue
        yield fnm.split(os.sep)[-1][:-3]


def parse(txt=None):
    if txt is None:
        txt = " ".join(sys.argv[1:])
    prs = Parsed()
    prs.parse(txt)
    update(Cfg.prs, prs)
    return prs


def scanner(pkg, importer, mods=None):
    path = pkg.__path__[0]
    name = pkg.__name__
    scandir(path, importer, name, mods)


def scandir(path, importer, pname, mods=None):
    for modname in listmod(path):
        if mods and not include(modname, spl(mods)):
            continue
        mname = "%s.%s" % (pname, modname)
        mod = importer(mname, path)
        scan(mod)


def wait():
    while 1:
        time.sleep(1.0)


## runtime


Cfg = Config()
Cfg.prs = Parsed()

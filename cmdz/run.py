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


from .event import Event, Parsed
from .handler import Handler, Command, scan
from .object import Default, Object, last, spl, update
from .thread import launch


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


Cfg = Config()


def boot():
    parse()
    if "c" in Cfg.opts:
        Cfg.console = True
    if "d" in Cfg.opts:
        Cfg.daemon= True
    if "v" in Cfg.opts:
        Cfg.verbose = True
    if "w" in Cfg.opts:
        Cfg.wait = True


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
    if "c" in prs.opts:
        prs.console = True
    if "d" in prs.opts:
        prs.debug = True
    if "v" in prs.opts:
        prs.verbose = True
    if "x" in prs.opts:
        prs.exec = True
    if "w" in prs.opts:
        prs.wait = True
    update(Cfg, prs)
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

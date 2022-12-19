# This file is placed in the Public Domain.
# pylint: disable=C0115,C0116,E1101


"runtime information"


import threading
import time


from cmdz.objects import Object, update
from cmdz.handler import Bus
from cmdz.threads import elapsed, name


def __dir__():
    return (
            'fleet',
            'threads',
            'uptime'
           )


starttime = time.time()


def fleet(event):
    try:
        index = int(event.args[0])
        event.reply(Bus.objs[index])
        return
    except (KeyError, TypeError, IndexError, ValueError):
        pass
    event.reply(" | ".join([name(o) for o in Bus.objs]))


def threads(event):
    result = []
    for thread in sorted(threading.enumerate(), key=lambda x: x.getName()):
        if str(thread).startswith("<_"):
            continue
        obj = Object()
        update(obj, vars(thread))
        if getattr(obj, "sleep", None):
            uptime = obj.sleep - int(time.time() - obj.state["latest"])
        else:
            uptime = int(time.time() - starttime)
        result.append((uptime, thread.name))
    res = []
    for uptime, txt in sorted(result, key=lambda x: x[0]):
        res.append("%s/%s" % (txt, elapsed(uptime)))
    if res:
        event.reply(" ".join(res))
    else:
        event.reply("no threads running")


def uptime(event):
    event.reply(elapsed(time.time()-starttime))

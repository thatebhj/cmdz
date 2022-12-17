# This file is placed in the Public Domain


"config"


from cmdz.objects import last, printable, keys, edit, write
from cmdz.running import Cfg


def __dir__():
    return (
            "config",
           ) 


def config(event):
    last(Cfg)
    if not event.sets:
        event.reply(printable(
                              Cfg,
                              keys(Cfg),
                             )
                   )
    else:
        edit(Cfg, event.sets)
        write(Cfg)
        event.done()

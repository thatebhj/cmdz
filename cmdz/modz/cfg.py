# This file is placed in the Public Domain


"config"


from cmdz.object import last, printable, keys, edit, write
from cmdz.run import Cfg


def cfg(event):
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

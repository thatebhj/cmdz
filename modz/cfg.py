# This file is placed in the Public Domain


from cmdz import Cfg, last, printable, keys, save, edit


def cfg(event):
    last(Cfg)
    if not event.sets:
        event.reply(printable(
                              Cfg,
                              keys(Cfg),
                              skip="control,password,realname,sleep,username")
                             )
    else:
        edit(Cfg, event.sets)
        save(Cfg)
        event.done()

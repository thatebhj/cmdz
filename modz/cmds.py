# This file is placed in the Public Domain.
# pylint: disable=C0115,C0116


"commands"


from cmdz.handler import Command


def __dir__():
    return (
            'cmds',
           )


def cmds(event):
    event.reply(",".join(sorted(Command.cmd)))

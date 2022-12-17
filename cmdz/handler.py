# This file is placed in the Public Domain.
# pylint: disable=C0115,C0116,W0703,W0201,R0902,R0903,W0613,R0201,E0402


"handler"


import inspect
import queue
import sys
import threading
import time


from .bus import Bus
from .object import Object
from .thread import launch


def __dir__():
    return (
            'Callback',
            'Command',
            'Handler',
            'scan',
           )


__all__ = __dir__()


class Callback(Object):

    cbs = Object()
    errors = []

    def register(self, typ, cbs):
        if typ not in self.cbs:
            setattr(self.cbs, typ, cbs)

    def callback(self, event):
        func = getattr(self.cbs, event.type, None)
        if not func:
            event.ready()
            return
        event.__thr__ = launch(func, event)

    def dispatch(self, event):
        self.callback(event)

    def get(self, typ):
        return getattr(self.cbs, typ)


class Command(Object):

    cmd = Object()
    errors = []

    @staticmethod
    def add(cmd):
        setattr(Command.cmd, cmd.__name__, cmd)

    @staticmethod
    def get(cmd):
        return getattr(Command.cmd, cmd, None)

    @staticmethod
    def handle(evt):
        if not evt.isparsed:
            evt.parse()
        func = Command.get(evt.cmd)
        if func:
            try:
                func(evt)
            except Exception as ex:
                tbk = sys.exc_info()[2]
                evt.__exc__ = ex.with_traceback(tbk)
                Command.errors.append(evt)
                evt.ready()
                return None
            evt.show()
        evt.ready()
        return None

    @staticmethod
    def remove(cmd):
        delattr(Command.cmd, cmd)


class Handler(Callback):

    def __init__(self):
        Callback.__init__(self)
        self.queue = queue.Queue()
        self.stopped = threading.Event()
        self.stopped.clear()
        self.register("event", Command.handle)
        Bus.add(self)

    @staticmethod
    def add(cmd):
        Command.add(cmd)

    def announce(self, txt):
        self.raw(txt)

    def handle(self, event):
        self.dispatch(event)

    def loop(self):
        while not self.stopped.set():
            self.handle(self.poll())

    def poll(self):
        return self.queue.get()

    def put(self, event):
        self.queue.put_nowait(event)

    def raw(self, txt):
        raise NotImplementedError("raw")

    def restart(self):
        self.stop()
        self.start()

    def say(self, channel, txt):
        self.raw(txt)

    def stop(self):
        self.stopped.set()

    def start(self):
        self.stopped.clear()
        self.loop()

    def wait(self):
        while 1:
            time.sleep(1.0)


def scan(mod):
    for key, cmd in inspect.getmembers(mod, inspect.isfunction):
        if key.startswith("cb"):
            continue
        names = cmd.__code__.co_varnames
        if "event" in names:
            Command.add(cmd)
# This file is placed in the Public Domain.
# pylint: disable=C0115,C0116,W0703,W0201,R0902,R0903,W0613,R0201,C0103,E0402


"event"


import threading
import time


from .bus import Bus
from .object import Default, register
from .thread import elapsed


def __dir__():
    return  (
             "Parsed",
             "Event",
            )


class Parsed(Default):

    def __init__(self):
        Default.__init__(self)
        self.args = []
        self.gets = Default()
        self.isparsed = False
        self.sets = Default()
        self.toskip = Default()
        self.txt = ""

    def parse(self, txt=None):
        self.isparsed = True
        self.otxt = txt or self.txt
        spl = self.otxt.split()
        args = []
        _nr = -1
        for word in spl:
            if word.startswith("-"):
                try:
                    self.index = int(word[1:])
                except ValueError:
                    self.opts = self.opts + word[1:2]
                continue
            try:
                key, value = word.split("==")
                if value.endswith("-"):
                    value = value[:-1]
                    register(self.toskip, value, "")
                register(self.gets, key, value)
                continue
            except ValueError:
                pass
            try:
                key, value = word.split("=")
                register(self.sets, key, value)
                continue
            except ValueError:
                pass
            _nr += 1
            if _nr == 0:
                self.cmd = word
                continue
            args.append(word)
        if args:
            self.args = args
            self.rest = " ".join(args)
            self.txt = self.cmd + " " + self.rest
        else:
            self.txt = self.cmd


class Event(Parsed):


    def __init__(self):
        Parsed.__init__(self)
        self.__ready__ = threading.Event()
        self.__thr__ = None
        self.control = "!"
        self.createtime = time.time()
        self.result = []
        self.type = "event"

    def bot(self):
        return Bus.byorig(self.orig)

    def error(self):
        pass

    def done(self):
        diff = elapsed(time.time()-self.createtime)
        Bus.say(self.orig, self.channel, f'ok {diff}')

    def ok(self, txt=None):
        text = "ok " + txt or ""
        text = text.rstrip()
        Bus.say(self.orig, self.channel, txt)

    def ready(self):
        self.__ready__.set()

    def reply(self, txt):
        self.result.append(txt)

    def show(self):
        for txt in self.result:
            Bus.say(self.orig, self.channel, txt)

    def wait(self):
        if self.__thr__:
            self.__thr__.join()
        self.__ready__.wait()

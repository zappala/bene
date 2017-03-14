from __future__ import print_function

from . import scheduler


class Sim(object):
    scheduler = scheduler.Scheduler()
    debug = {}
    files = {}

    @staticmethod
    def set_debug(kind):
        Sim.debug[kind] = True

    @staticmethod
    def trace(kind, message):
        if kind in Sim.debug:
            print(Sim.scheduler.current_time(), message)

    @staticmethod
    def plot(filename, message):
        if 'Plot' not in Sim.debug:
            return
        if filename not in Sim.files:
            Sim.files[filename] = open(filename,'wb')
        Sim.files[filename].write(message)

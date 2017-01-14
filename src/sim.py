from __future__ import print_function

from . import scheduler


class Sim(object):
    scheduler = scheduler.Scheduler()
    debug = {}

    @staticmethod
    def set_debug(kind):
        Sim.debug[kind] = True

    @staticmethod
    def trace(kind, message):
        if kind in Sim.debug:
            print(Sim.scheduler.current_time(), message)

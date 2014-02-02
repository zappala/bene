import scheduler

class Sim(object):
    scheduler = scheduler.Scheduler()
    debug = False

    @staticmethod
    def set_debug(value):
        Sim.debug = value

    @staticmethod
    def trace(message):
        if Sim.debug:
            print Sim.scheduler.current_time(),message


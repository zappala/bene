import itertools
import sched


class Scheduler(object):
    def __init__(self):
        self.current = 0
        self.count = itertools.count()
        self.scheduler = sched.scheduler(self.current_time, self.advance_time)

    def reset(self):
        self.current = 0

    def current_time(self):
        return self.current

    def advance_time(self, units):
        self.current += units

    def add(self, delay, event, handler):
        return self.scheduler.enter(delay, next(self.count), handler, [event])

    def cancel(self, event):
        self.scheduler.cancel(event)

    def run(self):
        self.scheduler.run()

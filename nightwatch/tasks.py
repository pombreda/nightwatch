import threading
import functools
from nightwatch.lib import parallelize


class Task(object):
    NOT_RUN = 0
    RUNNING = 1
    SATISFIED = 2
    FAILED = 3

    def __init__(self, func, deps = ()):
        self.func = func
        self.deps = deps
        self.output = None
        self._state = self.NOT_RUN
        self._lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        @functools.wraps(cls)
        def delayed(func):
            inst = cls.__base__.__new__(cls, *args, **kwargs)
            inst.__init__(func, *args, **kwargs)
            return inst
        return delayed

    def __call__(self):
        with self._lock:
            if self._state == self.NOT_RUN:
                self._state = self.RUNNING
            elif self._state == self.RUNNING:
                raise ValueError("Cyclic dependency detected")
            elif self._state == self.SATISFIED:
                return self
            elif self._state == self.FAILED:
                raise ValueError("Task has failed")
            else:
                raise ValueError("Invalid state %r" % (self._state,))
        
        try:
            if self.deps:
                parallelize(self.deps)
            self.output = dict(parallelize(lambda: (job, self.func(job)) 
                for job in self.get_jobs()))
        except Exception:
            with self._lock:
                self._state = self.FAILED
            raise
        else:
            with self._lock:
                self._state = self.SATISFIED

    def get_jobs(self):
        raise NotImplementedError()


class HostBasedTask(Task):
    def __init__(self, func, hosts, deps = ()):
        Task.__init__(self, func, deps = deps)
        self.hosts = hosts
    def get_jobs(self):
        for hostinfo in self.hosts:
            yield hostinfo.connect()


class Builder(HostBasedTask):
    pass


class Executor(HostBasedTask):
    pass











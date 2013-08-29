import rpyc
from plumbum import SshMachine
from rpyc.utils.zerodeploy import DeployedServer
import threading
import sys
import logging


class BaseHost(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
    def connect(self):
        raise NotImplementedError()
    def close(self):
        pass

class SshHost(BaseHost):
    def __init__(self, **kwargs):
        BaseHost.__init__(self, **kwargs)
        self._mach = None
        self.deployment = None
    def connect(self):
        if self.deployment is None:
            self._mach = SshMachine(**self.kwargs)
            self.deployment = DeployedServer(self._mach)
        return self.deployment.classic_connect()
    def close(self):
        if self.deployment is not None:
            self.deployment.close()
            self._mach.close()

class RPyCHost(BaseHost):
    def connect(self, **kwargs):
        return rpyc.classic.connect(**kwargs)

class DepsDict(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._values = kwargs.values()
    def __len__(self):
        return len(self._values)
    def __iter__(self):
        return iter(self._values)
    def __getattr__(self, name):
        return None
    def __getitem__(self, name):
        return getattr(self, name) 


def parallelize(iterable):
    results = {}
    def threadfunc(i, func):
        try:
            res = func()
        except Exception:
            results[i] = (False, sys.exc_info())
        else:
            results[i] = (True, res)
    
    threads = []
    for i, func in enumerate(iterable):
        thd = threading.Thread(target = threadfunc, args = (i, func))
        thd.start()
    for thd in threads:
        thd.join()
    
    output = [None] * len(results)
    for i in range(output):
        succ, obj = results[i]
        if succ:
            output[i] = obj
        else:
            t, v, tb = obj
            raise t, v, tb
    return output


class REQUIRED(object):
    pass

class BaseTask(object):
    NOT_RUN = 0
    RUNNING = 1
    SATISFIED = 2
    FAILED = 3
    
    def __init__(self, deps = (), **attrs):
        self._state = self.NOT_RUN
        self._lock = threading.Lock()
        self.deps = ()
        self.attrs = attrs
    
    def run(self):
        with self._lock:
            if self._state == self.NOT_RUN:
                self._state = self.RUNNING
            elif self._state == self.RUNNING:
                raise ValueError("Cyclic dependency detected")
            elif self._state == self.SATISFIED:
                return
            elif self._state == self.FAILED:
                raise ValueError("Task is failed")
            else:
                raise ValueError("Invalid state: %r" % (self._state,))
        
        try:
            parallelize(dep.run for dep in self.deps)
            self._run()
        except Exception:
            with self._lock:
                self._state = self.FAILED
        else:
            with self._lock:
                self._state = self.SATISFIED

    @property
    def logger(self):
        return logging.getLogger(self.__class__.__name__)

    def _run(self):
        raise NotImplementedError()

class BuildTask(BaseTask):
    ATTRS = dict(hosts = REQUIRED)
    
    def should_rebuild(self):
        return True
    def get_outputs(self):
        raise NotImplementedError()

class ScriptTask(BaseTask):
    ATTRS = dict(hosts = REQUIRED)

class GitBuildTask(BaseTask):
    pass

class PipTask(ScriptTask):
    pass

class NoseTask(ScriptTask):
    pass





















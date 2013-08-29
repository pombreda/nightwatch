import rpyc
from plumbum import SshMachine
from rpyc.utils.zerodeploy import DeployedServer


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



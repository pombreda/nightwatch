import os


def gitrepo(host, url, branch = "master"):
    pass

def run(host, command):
    pass

class VirtualEnv(object):
    def __init__(self, host, path, interpreter = None):
        self.host = host
        self.path = path
        self.interpreter = interpreter
    
    def activate(self):
        self.host.modules.os.environ["VIRTUAL_ENV"] = self.path
        self._prev_pythonhome = self.host.modules.os.environ["PYTHONHOME"]
        self.host.modules.os.environ["PYTHONHOME"] = ""
        self._prev_path = self.host.modules.os.environ["PATH"]
        path = [self.path + "/bin", self.path + "/Scripts"]
        if self._prev_path:
            path.append(self._prev_path)
        self.host.modules.os.environ["PATH"] = os.path.pathsep.join(path)
    
    def deactivate(self):
        self.host.modules.os.environ["VIRTUAL_ENV"] = ""
        self.host.modules.os.environ["PYTHONHOME"] = self._prev_pythonhome
        self.host.modules.os.environ["PATH"] = self._prev_path
    
    def pip(self, *args):
        pass












from nightwatch import SshHost, Builder, Executor


hosts = [SshHost("server1"), SshHost("server2")]

@Builder(hosts = hosts)
def build_A(host):
    with host.gitrepo("url"):
        host.run("python", "setup.py", "sdist")
        return host.glob("dist/*.tar.gz")

@Builder(hosts = hosts)
def build_B(host):
    with host.gitrepo("url"):
        host.run("python", "setup.py", "sdist")
        return host.glob("dist/*.tar.gz")

@Builder(hosts = hosts, deps = [build_A, build_B])
def build_C(host):
    build_A.outputs

@Executor(hosts = hosts)
def run_tests(host):
    with host.virtual_env() as venv:
        venv.pip("install", "foo")
        venv.pip("install", "bar")
        venv.nosetest("-vv")














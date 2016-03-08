import pytest
import socket

DEFAULT_PORT = '11211'

@pytest.fixture(scope='session')
def run_services():
    """Run services for tests."""
    return True


@pytest.fixture(scope='module')
def memcached_address(request, run_services):
    """The memcached socket location."""
    if run_services:
        return getattr(request.module, 'MEMCACHE_CONNECTION', ['127.0.0.1:11211'])


def get_version(host, port):
    port = int(port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.send(b"version\r\n")
        version = s.recv(4096)
    finally:
        s.close()
    vstr = b"VERSION "
    rnstr = b"\r\n"
    if not version.startswith(vstr) or not version.endswith(rnstr):
        raise ValueError("unexpected version return: %r" % (version,))
    else:
        version = version[8:-2]
    return version


def memcached_checker(addresses):
    for addr in [addr.split(':') for addr in addresses]:
        if len(addr) < 2:
            addr.append(DEFAULT_PORT)
        try:
            get_version(*addr)
        except (ValueError, socket.error):
            continue
        return True
    return False


@pytest.fixture(scope='module')
def memcached(run_services, memcached_address, watcher_getter):
    """The memcached instance which is ready to be used by the tests."""
    if run_services:
        return watcher_getter(
            name='memcached',
            arguments=['-l', ",".join(memcached_address)],
            checker=lambda : memcached_checker(memcached_address))
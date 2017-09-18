from fabric.api import env
from getpass import getpass


def ensure_hosts():
    """Ensure there is at least one host stored in the Fabric environment"""
    if len(env.hosts) == 0:
        env.hosts = ["localhost"]

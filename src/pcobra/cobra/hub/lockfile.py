"""API de lockfiles de Hub, separada para consumidores neutrales."""

from pcobra.cobra.hub.resolver import read_lockfile, write_lockfile

__all__ = ["read_lockfile", "write_lockfile"]

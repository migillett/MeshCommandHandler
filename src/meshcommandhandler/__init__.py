from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("MeshCommandHandler")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

from .main import MeshCommandHandler

__all__ = ["MeshCommandHandler", "__version__"]


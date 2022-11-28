try:
    import uvloop

    uvloop.install()
except ImportError:  # pragma: nocover
    pass

from app.app import app  # noqa F401

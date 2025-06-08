import importlib

modules = [
    'main',
    'app.routers.plant',
    'app.routers.sensor',
    'app.routers.diagnostics',
    'app.routers.manual',
    'app.routers.system',
    'app.routers.health',
]


def test_imports():
    for m in modules:
        assert importlib.import_module(m)

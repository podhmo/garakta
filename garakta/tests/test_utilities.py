# -*- coding:utf-8 -*-
import pytest


def _getTarget():
    from garakta import create_registry
    return create_registry


def _makeOne():
    return _getTarget()()


class Storage(object):
    def save(self, data):
        raise Exception


class FileStorage(Storage):
    def __init__(self, name):
        self.name = name

    def save(self, data):
        import json
        with open(self.name, "w") as wf:
            wf.write(json.dumps(data))


class MockStorage(Storage):
    def __init__(self):
        self.data = None

    def save(self, data):
        self.data = data


def test_lookup_component__found__ok():
    reg = _makeOne()

    component = FileStorage("savedata.json")
    reg.utilities.register(Storage, component)

    result = reg[Storage]

    assert result == component


def test_lookup_component__not_found__raise_error():
    from garakta import ComponentNotFound
    reg = _makeOne()

    with pytest.raises(ComponentNotFound):
        reg[Storage]


def test_lookup_component__inherited__found__ok():
    reg = _makeOne()

    # Storage -> {FileStorage,  MockStorage}
    component = MockStorage()
    reg.utilities.register(FileStorage, FileStorage("savedata.json"))
    reg.utilities.register(Storage, component)

    assert reg[MockStorage] == component


def test_lookup_component__inherited__multiple__ok():
    reg = _makeOne()

    component = MockStorage()
    reg.utilities.register(Storage, component)

    assert reg[MockStorage] == component

    # cached?
    def dont_call_this(*args, **kwargs):
        raise Exception
    reg.utilities.walk_for_parent = dont_call_this
    assert reg[MockStorage] == component

    # really cached?
    with pytest.raises(Exception):
        reg[FileStorage]


def test_register__with_validation__ng__raise_error():
    from garakta import InvalidComponent

    def has_name(registry, target):
        return hasattr(target, "name")

    reg = _makeOne()

    reg.utilities.validation[Storage].append(has_name)
    with pytest.raises(InvalidComponent):
        reg.utilities.register(Storage, MockStorage())


def test_register__with_validation__ok():
    from garakta import InvalidComponent

    def has_name(registry, target):
        return hasattr(target, "name")

    reg = _makeOne()

    reg.utilities.validation[Storage].append(has_name)
    reg.utilities.register(Storage, FileStorage("hmm"))


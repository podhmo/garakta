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


def get_storage_name_for_storage(storage):
    return u"保存場所"  # save point


def get_storage_name_for_file_storage(storage):
    return u"保存場所: {}".format(storage.name)


def test__lookup_found__ok():
    reg = _makeOne()

    reg.adapters.register(FileStorage, "display_name", get_storage_name_for_file_storage)

    result = reg(FileStorage("hmm")).display_name()
    assert result == u"保存場所: hmm"


def test__lookup__attributes_is__not_found__raise_attribute_error():
    reg = _makeOne()

    reg.adapters.register(FileStorage, "display_name", get_storage_name_for_file_storage)
    with pytest.raises(AttributeError):
        reg(FileStorage("hmm")).missing()


def test__lookup__adapter_is__not_found__raise_error():
    from garakta import ComponentNotFound
    reg = _makeOne()
    with pytest.raises(ComponentNotFound):
        reg(FileStorage("hmm")).missing()

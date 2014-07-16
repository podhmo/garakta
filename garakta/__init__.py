# -*- coding:utf-8 -*-
class ComponentNotFound(Exception):
    pass


class Registry(object):
    def __init__(self, utilities, adapters):
        self.utilities = utilities
        self.adapters = adapters

    def __getitem__(self, k):
        return self.utilities.lookup(k)


class UtilitiyRegistry(object):
    def __init__(self, sentinel=object):
        self.registry = {}
        self.sentinel = sentinel

    def register(self, k, instance):
        self.registry[k] = instance

    def lookup(self, cls):
        try:
            return self.registry[cls]
        except KeyError:
            v = self.registry[cls] = self.walk_for_parent(cls)
            return v

    def walk_for_parent(self, target_class):
        for cls in target_class.__mro__:
            if self.sentinel == cls:
                raise ComponentNotFound(target_class)
            v = self.registry.get(cls)
            if v is not None:
                return v
        raise ComponentNotFound(target_class)


class Adapters(object):
    pass


def create_registry():
    return Registry(
        UtilitiyRegistry(),
        None
    )

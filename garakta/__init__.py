# -*- coding:utf-8 -*-
from collections import defaultdict


class ComponentError(Exception):
    pass


class ComponentNotFound(ComponentError):
    pass


class InvalidComponent(ComponentError):
    pass


class Registry(object):
    def __init__(self, utilities, adapters):
        self.utilities = utilities
        self.adapters = adapters

    def __getitem__(self, k):
        return self.utilities.lookup(k)

    @property
    def validation(self):
        return self.utilities.validation


class UtilitiyRegistry(object):
    def __init__(self, validation=None, sentinel=object):
        self.registry = {}
        self.validation = validation
        self.sentinel = sentinel

    def register(self, k, instance):
        for v in self.validation.get(k, []):
            status = v(self, instance)
            if status is False:
                raise InvalidComponent(v, instance)
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


class AdapterRegistry(object):
    def __init__(self):
        self.registry = {}


class Validation(object):
    def __init__(self):
        self.registry = defaultdict(list)

    def __getitem__(self, k):
        return self.registry[k]

    def get(self, k, default=None):
        return self.registry.get(k, default)


def create_registry():
    return Registry(
        UtilitiyRegistry(Validation()),
        None
    )

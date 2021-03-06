# -*- coding:utf-8 -*-
from collections import defaultdict
from functools import wraps
from weakref import WeakKeyDictionary


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

    def __call__(self, src):
        return self.adapters.lookup(src)

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


class AdapterFactory(object):
    def init(self, ob):
        self.ob = ob

    def __init__(self, init=init):
        self.attrs = {"__init__": init}

    def __setitem__(self, k, v):
        self.attrs[k] = self.wrap(v)

    def wrap(self_, fn):
        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            return fn(self.ob, *args, **kwargs)
        return wrapped

    def create(self, src):
        return type("{}Adapter".format(src.__name__), (object, ), self.attrs)


class AdapterRegistry(object):
    def __init__(self, sentinel=object):
        self.sentinel = sentinel
        self.adapter_factories = defaultdict(AdapterFactory)
        self.factory_cache = {}
        self.adapter_cache = WeakKeyDictionary()

    def lookup(self, ob):
        try:
            return self.adapter_cache[ob]
        except KeyError:
            v = self.adapter_cache[ob] = self.adapter_from_class(ob.__class__)(ob)
            return v

    def adapter_from_class(self, cls):
        try:
            return self.factory_cache[cls]
        except KeyError:
            v = self.factory_cache[cls] = self.walk_for_parent(cls)
            return v

    def walk_for_parent(self, target_class):
        for cls in target_class.__mro__:
            if self.sentinel == cls:
                raise ComponentNotFound(target_class)
            factory = self.adapter_factories.get(cls)
            if factory is not None:
                return factory.create(cls)
        raise ComponentNotFound(target_class)

    def register(self, src, name, fn):
        self.adapter_factories[src][name] = fn


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
        AdapterRegistry()
    )

# -*- coding:utf-8 -*-
from collections import defaultdict
from functools import wraps


class ComponentError(Exception):
    pass


class ComponentNotFound(ComponentError):
    pass


class ComponentNotPolymorphic(ComponentError):
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


class AdapterProxyFactory(object):
    def proxy_init(self, ob):
        self.ob = ob

    def __init__(self, proxy_init=proxy_init):
        self.attrs = {"__init__": proxy_init}

    def __setitem__(self, k, v):
        self.attrs[k] = self.wrap(v)

    def wrap(self_, fn):
        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            return fn(self.ob, *args, **kwargs)
        return wrapped

    def create(self, src):
        return type("{}AdapterProxy".format(src.__name__), (object, ), self.attrs)


class AdapterRegistry(object):
    def __init__(self, sentinel=object):
        self.sentinel = sentinel
        self.proxy_factories = defaultdict(AdapterProxyFactory)
        self.cache = {}

    def lookup(self, ob):
        return self.proxy_from_class(ob.__class__)(ob)

    def proxy_from_class(self, cls):
        try:
            return self.cache[cls]
        except KeyError:
            v = self.cache[cls] = self.walk_for_parent(cls)
            return v

    def walk_for_parent(self, target_class):
        for cls in target_class.__mro__:
            if self.sentinel == cls:
                raise ComponentNotFound(target_class)
            factory = self.proxy_factories.get(cls)
            if factory is not None:
                return factory.create(cls)
        raise ComponentNotFound(target_class)

    def register(self, src, name, fn, polimorphic=False):
        self.proxy_factories[src][name] = fn

    # def reorder(self, repo, name):
    #     targets = repo[name]
    #     targets = list(sorted(targets, key=lambda xs: len(xs[0].__mro__)))
    #     repo[name] = targets


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

# simple extensions built on classes

class Wrapped:
    def __init__(self, func, load):
        self.func = func
        self._load = load

    def __get__(self, instance, owner):
        return self.func.__get__(instance, owner)
        # binds the method to the instance ensuring that the
        # `self` argument is always passed implicitly


def event(func):
    def load(instance, client):
        bound = func.__get__(instance, instance.__class__)
        client.events(bound)
    return Wrapped(func, load)


def command(func):
    def load(instance, client):
        bound = func.__get__(instance, instance.__class__)
        client.commands(bound)
    return Wrapped(func, load)


class ExtensionMeta(type):
    def __new__(cls, name, bases, dict_):
        klass = super().__new__(cls, name, bases, dict_)
        klass._methods = []
        for value in dict_.values():
            if isinstance(value, Wrapped):
                klass._methods.append(value)
        return klass

    def __call__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._args_ = args
        obj._kwargs_ = kwargs
        return obj


class Extension(metaclass=ExtensionMeta):
    def remove_event(self, func):
        self._methods.remove(func)
        self.client.events.remove(func)

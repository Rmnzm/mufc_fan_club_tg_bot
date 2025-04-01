import threading
from typing import Dict, Any


class SingletonWithParams(type):
    """Singleton Via Metaclass - allows classes to create just one unique instance with their args, kwargs.
    Metaclass that avoids constructing an object of the Target class if it already exists,
    especially needed for connectors as database, pulsar, etc."""

    _instances = {}
    _singleton_locks: Dict[Any, threading.Lock] = {}

    def __call__(cls, *args, **kwargs):
        key = (cls, str(args), str(kwargs))
        if key not in cls._instances:
            if key not in cls._singleton_locks:
                cls._singleton_locks[key] = threading.Lock()
            with cls._singleton_locks[key]:
                if key not in cls._instances:
                    cls._instances[key] = super(SingletonWithParams, cls).__call__(
                        *args, **kwargs
                    )
        return cls._instances[key]


def singleton(the_class):
    """decorator for a class to make a singleton out of it"""
    class_instances = {}
    singleton_locks: Dict[Any, threading.Lock] = {}

    def get_instance(*args, **kwargs):
        """creating or just return the one and only class instance.
        The singleton depends on the parameters used in init"""
        key = (the_class, str(args), str(kwargs))
        if key not in class_instances:
            if key not in singleton_locks:
                singleton_locks[key] = threading.Lock()
            with singleton_locks[key]:
                if key not in class_instances:
                    class_instances[key] = the_class(*args, **kwargs)
        return class_instances[key]

    return get_instance

import math


# Base class of the algorithm and distribution families (SortAlgorithm, PathFinder, WeightDistribution). Every family
# gets its own registry, and every subclass of a family with a display name registers itself there, so the pages can
# list it. params maps the names of the numeric parameters a class takes to their default values.
class Registry:
    kind = "class"
    name = None
    params = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if Registry in cls.__bases__:
            cls.registry = {}
        elif cls.name:
            cls.registry[cls.name] = cls

    @classmethod
    def get(cls, name):
        if name not in cls.registry:
            raise ValueError("Unknown " + cls.kind + ": " + str(name))
        return cls.registry[name]

    # sets an attribute for every parameter from params (name -> value), missing ones take their default
    def setParams(self, params):
        params = params or {}
        if not isinstance(params, dict):
            raise ValueError("'params' must map parameter names to values")
        for param, default in self.params.items():
            value = params.get(param, default)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("'" + param + "' must be a number")
            setattr(self, param, value)

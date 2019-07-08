"""
A tiny base class for fluent builders.
"""


class Builder:
    """
    A base class for builders, supporting the "with" style of chaining methods.
    "With" methods are dynamically generated based on the names defined
    in the 'defaults' attribute (to be overridden by subclasses) according
    to the template ``with_{name}``.

    To subclass Builder:
        1. Define a class attribute (a list of tuples) called ``defaults``.
        2. Override the ``dict`` method if you need to use a custom dict class
        3. Define a ``build`` method which performs the required steps to
           build the object and returns an instance of the object.
    A 'with' method for each entry in ``defaults`` will be generated for you.

    >>> class MyBuilder(Builder):
    ...     # declare the defaults for the builder
    ...     defaults = [
    ...         ("abc", 123),
    ...         ("def", 456),
    ...         ("xyz", 789)
    ...     ]
    ...
    ...     def build(self):
    ...         # convert self.data into the object you're building
    ...         return self.data
    ...
    >>> result = MyBuilder().with_abc(-1).with_def(-2).build()
    >>> result == {'xyz': 789, 'def': -2, 'abc': -1}
    True
    """

    def __init__(self):
        self.data = self.dict(self.defaults)

    def __getattr__(self, name):
        if not name.startswith("with_"):
            raise AttributeError(name)
        if name[5:] not in self.data:
            raise AttributeError(name)

        def _with(value):
            """
            Sets the value of ``"{}"`` in ``self.data``.

            :param value: The value to set.
            """.format(name[5:])
            self.data[name[5:]] = value
            return self

        _with.__name__ = name

        return _with

    def dict(self, pairs):
        """
        Override me if you want to use a custom :class:`dict`
        subclass for ``self.data``.
        """
        return dict(pairs)


def evaluate_callables(data):
    """
    Call any callable values in the input dictionary;
    return a new dictionary containing the evaluated results.
    Useful for lazily evaluating default values in ``build`` methods.

    >>> data = {"spam": "ham", "eggs": (lambda: 123)}
    >>> result = evaluate_callables(data)
    >>> result == {'eggs': 123, 'spam': 'ham'}
    True
    """
    sequence = ((k, v() if callable(v) else v) for k, v in data.items())
    return type(data)(sequence)

"""Refactored 'safe reference from dispatcher.py"""

import collections.abc
import traceback
import weakref
from functools import total_ordering


def safe_ref(target, on_delete=None):
    """Return a *safe* weak reference to a callable target.

    - ``target``: The object to be weakly referenced, if it's a bound
      method reference, will create a BoundMethodWeakref, otherwise
      creates a simple weakref.

    - ``on_delete``: If provided, will have a hard reference stored to
      the callable to be called after the safe reference goes out of
      scope with the reference object, (either a weakref or a
      BoundMethodWeakref) as argument.
    """
    if hasattr(target, "im_self"):
        if target.__self__ is not None:
            # Turn a bound method into a BoundMethodWeakref instance.
            # Keep track of these instances for lookup by disconnect().
            assert hasattr(target, "im_func"), (
                f"safe_ref target {target!r} has im_self, but no im_func, "
                "don't know how to create reference"
            )
            reference = BoundMethodWeakref(target=target, on_delete=on_delete)
            return reference

    if hasattr(target, "__self__"):
        if target.__self__ is not None:
            assert hasattr(target, "__func__"), (
                f"safe_ref target {target!r} has __self__, but no __func__, "
                "don't know how to create reference"
            )
            reference = BoundMethodWeakref(target=target, on_delete=on_delete)
            return reference

    if hasattr(on_delete, "__call__"):
        return weakref.ref(target, on_delete)
    else:
        return weakref.ref(target)


@total_ordering
class BoundMethodWeakref(object):
    """'Safe' and reusable weak references to instance methods.

    BoundMethodWeakref objects provide a mechanism for referencing a
    bound method without requiring that the method object itself
    (which is normally a transient object) is kept alive.  Instead,
    the BoundMethodWeakref object keeps weak references to both the
    object and the function which together define the instance method.

    Attributes:

    - ``key``: The identity key for the reference, calculated by the
      class's calculate_key method applied to the target instance method.

    - ``deletion_methods``: Sequence of callable objects taking single
      argument, a reference to this object which will be called when
      *either* the target object or target function is garbage
      collected (i.e. when this object becomes invalid).  These are
      specified as the on_delete parameters of safe_ref calls.

    - ``weak_self``: Weak reference to the target object.

    - ``weak_func``: Weak reference to the target function.

    Class Attributes:

    - ``_all_instances``: Class attribute pointing to all live
      BoundMethodWeakref objects indexed by the class's
      calculate_key(target) method applied to the target objects.
      This weak value dictionary is used to short-circuit creation so
      that multiple references to the same (object, function) pair
      produce the same BoundMethodWeakref instance.
    """

    _all_instances = weakref.WeakValueDictionary()

    def __new__(cls, target, on_delete=None, *arguments, **named):
        """Create new instance or return current instance.

        Basically this method of construction allows us to
        short-circuit creation of references to already- referenced
        instance methods.  The key corresponding to the target is
        calculated, and if there is already an existing reference,
        that is returned, with its deletion_methods attribute updated.
        Otherwise the new instance is created and registered in the
        table of already-referenced methods.
        """
        key = cls.calculate_key(target)
        current = cls._all_instances.get(key)
        if current is not None:
            current.deletion_methods.append(on_delete)
            return current
        else:
            base = super(BoundMethodWeakref, cls).__new__(cls)
            cls._all_instances[key] = base
            base.__init__(target, on_delete, *arguments, **named)
            return base

    def __init__(self, target, on_delete=None):
        """Return a weak-reference-like instance for a bound method.

        - ``target``: The instance-method target for the weak reference,
          must have im_self and im_func attributes and be
          reconstructable via the following, which is true of built-in
          instance methods::

            target.im_func.__get__( target.im_self )

        - ``on_delete``: Optional callback which will be called when
          this weak reference ceases to be valid (i.e. either the
          object or the function is garbage collected).  Should take a
          single argument, which will be passed a pointer to this
          object.
        """

        def remove(weak, self_=self):
            """Set self.isDead to True when method or instance is destroyed."""
            methods = self_.deletion_methods[:]
            del self_.deletion_methods[:]
            try:
                del self_.__class__._all_instances[self_.key]
            except KeyError:
                pass
            for function in methods:
                try:
                    if isinstance(function, collections.abc.Callable):
                        function(self_)
                except Exception:
                    try:
                        traceback.print_exc()
                    except AttributeError as e:
                        print(
                            f"Exception during saferef {self_} "
                            f"cleanup function {function}: {e}"
                        )

        self.deletion_methods = [on_delete]
        self.key = self.calculate_key(target)
        try:
            self.weak_self = weakref.ref(target.__self__, remove)
            self.weak_func = weakref.ref(target.__func__, remove)
            self.self_name = str(target.__self__)
            self.__name__ = str(target.__func__.__name__)
        except AttributeError:
            self.weak_self = weakref.ref(target.__self__, remove)
            self.weak_func = weakref.ref(target.__func__, remove)
            self.self_name = str(target.__self__)
            self.__name__ = str(target.__func__.__name__)

    @classmethod
    def calculate_key(cls, target):
        """Calculate the reference key for this reference.

        Currently this is a two-tuple of the id()'s of the target
        object and the target function respectively.
        """
        return id(target.__self__), id(target.__func__)

    def __str__(self):
        """Give a friendly representation of the object."""
        return f"{self.__class__.__name__}({self.self_name}.{self.__name__})"

    __repr__ = __str__

    def __bool__(self):
        """Whether we are still a valid reference."""
        return self() is not None

    def __eq__(self, other):
        """Compare with another reference."""
        if not isinstance(other, self.__class__):
            return self.__class__ is type(other)
        else:
            return self.key == other.key

    def __ne__(self, other):
        """Compare with another reference."""
        if not isinstance(other, self.__class__):
            return self.__class__ is not type(other)
        else:
            return self.key != other.key

    def __lt__(self, other):
        """Compare with another reference."""
        if not isinstance(other, self.__class__):
            return self.__class__ < type(other)
        else:
            return self.key < other.key

    def __call__(self):
        """Return a strong reference to the bound method.

        If the target cannot be retrieved, then will return None,
        otherwise returns a bound instance method for our object and
        function.

        Note: You may call this method any number of times, as it does
        not invalidate the reference.
        """
        target = self.weak_self()
        if target is not None:
            function = self.weak_func()
            if function is not None:
                return function.__get__(target)
        return None

    def __hash__(self):
        return hash(self.key)

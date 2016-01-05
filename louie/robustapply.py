"""Robust apply mechanism.

Provides a function 'call', which can sort out what arguments a given
callable object can take, and subset the given arguments to match only
those which are acceptable.
"""

def function(receiver):
    """Get function-like callable object for given receiver.

    returns (function_or_method, codeObject, fromMethod)

    If fromMethod is true, then the callable already has its first
    argument bound.
    """
    if hasattr(receiver, '__call__'):
        # receiver is a class instance; assume it is callable.
        # Reassign receiver to the actual method that will be called.
        c = receiver.__call__
        if hasattr(c, 'im_func') or hasattr(c, 'im_code'):
            receiver = c 
        if hasattr(c, '__func__') or hasattr(c, '__code__'):
            receiver = c
    if hasattr(receiver, 'im_func'):
        # receiver is an instance-method.
        return receiver, receiver.im_func.func_code, 1
    if hasattr(receiver, '__func__'):
        #receiver is an instance method in python3
        return receiver, receiver.__func__.__code__, 1
    if hasattr(receiver, '__code__'):
        #receiver is a function and has code, name changed in python3?
        return receiver, receiver.__code__, 0 

    elif not hasattr(receiver, 'func_code'):
        raise ValueError(
            'unknown reciever type {} {}'.format(receiver, type(receiver)))
    return receiver, receiver.func_code, 0


def robust_apply(receiver, signature, *arguments, **named):
    """Call receiver with arguments and appropriate subset of named.
    ``signature`` is the callable used to determine the call signature
    of the receiver, in case ``receiver`` is a callable wrapper of the
    actual receiver."""
    signature, code_object, startIndex = function(signature)
    acceptable = code_object.co_varnames[
        startIndex + len(arguments):
        code_object.co_argcount
        ]
    for name in code_object.co_varnames[
        startIndex:startIndex + len(arguments)
        ]:
        if name in named:
            raise TypeError(
                'Argument {!r} specified both positionally '
                'and as a keyword for calling {!r}'.format(name, signature))
    if not (code_object.co_flags & 8):
        # fc does not have a **kwds type parameter, therefore 
        # remove unacceptable arguments.
        # have to make this a list type in python3 as dicts cant be
        # modified in place, producing RuntimeError 
        for arg in list(named.keys()):
            if arg not in acceptable:
                del named[arg]
    return receiver(*arguments, **named)

            

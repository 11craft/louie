"""Robust apply mechanism.

Provides a function 'call', which can sort out what arguments a given
callable object can take, and subset the given arguments to match only
those which are acceptable.
"""

import sys
if sys.hexversion >= 0x3000000:
    IM_FUNC = '__func__'
    FUNC_CODE = '__code__'
else:
    IM_FUNC = 'im_func'
    FUNC_CODE = 'func_code'


def function(receiver):
    """Get function-like callable object for given receiver.

    returns (function_or_method, codeObject, fromMethod)

    If fromMethod is true, then the callable already has its first
    argument bound.
    """
    if hasattr(receiver, IM_FUNC):
        # Instance method.
        im_func = getattr(receiver, IM_FUNC)
        func_code = getattr(im_func, FUNC_CODE)
        return receiver, func_code, True
    elif hasattr(receiver, FUNC_CODE):
        func_code = getattr(receiver, FUNC_CODE)
        return receiver, func_code, False
    elif hasattr(receiver, '__call__'):
        return function(receiver.__call__)
    else:
        raise ValueError(
            'unknown reciever type {} {}'.format(receiver, type(receiver)))


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
                'Argument {0!r} specified both positionally '
                'and as a keyword for calling {1!r}'.format(name, signature))
    if not (code_object.co_flags & 8):
        # fc does not have a **kwds type parameter, therefore 
        # remove unacceptable arguments.
        # have to make this a list type in python3 as dicts cant be
        # modified in place, producing RuntimeError 
        for arg in list(named.keys()):
            if arg not in acceptable:
                del named[arg]
    return receiver(*arguments, **named)

            

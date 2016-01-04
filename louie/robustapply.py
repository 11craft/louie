"""Robust apply mechanism.

Provides a function 'call', which can sort out what arguments a given
callable object can take, and subset the given arguments to match only
those which are acceptable.
"""

import sys
if sys.hexversion >= 0x3000000:
    im_func = '__func__'
    im_self = '__self__'
    im_code = '__code__'
    func_code = '__code__'
else:
    im_func = 'im_func'
    im_self = 'im_self'
    im_code = 'im_code'
    func_code = 'func_code'


def function( receiver ):
        """Get function-like callable object for given receiver

        returns (function_or_method, codeObject, fromMethod)

        If fromMethod is true, then the callable already
        has its first argument bound
        """
        if hasattr( receiver, im_func ):
                # an instance-method...
                return receiver, getattr(getattr(receiver, im_func), func_code), 1
        elif hasattr(receiver, 'func_code'):
                return receiver, receiver.func_code, 0
        elif hasattr(receiver, '__call__'):
                return function(receiver.__call__)
        else:
                raise ValueError('unknown reciever type %s %s'%(receiver, type(receiver)))


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
        if named.has_key(name):
            raise TypeError(
                'Argument %r specified both positionally '
                'and as a keyword for calling %r'
                % (name, signature)
                )
    if not (code_object.co_flags & 8):
        # fc does not have a **kwds type parameter, therefore 
        # remove unacceptable arguments.
        for arg in named.keys():
            if arg not in acceptable:
                del named[arg]
    return receiver(*arguments, **named)

            

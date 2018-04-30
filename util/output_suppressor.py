# CC0 - free software.
# To the extent possible under law, all copyright and related or neighboring
# rights to this work are waived.

'''
A context manager for suppression of stdout and stderr. Will suppress all
output, even if the print originates in a native sub-function. Will not
suppress raised exceptions, since exceptions are printed to stderr just before
a script exits, and after the context manager has exited.

>>> import sys
>>> with Suppressor():
...     print('out SHOULD NOT SHOW', file=sys.stdout)
...     print('err SHOULD NOT SHOW', file=sys.stderr)
>>> with ErrorSuppressor():
...     print('err SHOULD NOT SHOW', file=sys.stderr)
>>> with OutputSuppressor():
...     print('out SHOULD NOT SHOW', file=sys.stdout)
>>> with Suppressor(suppress_stdout=False, suppress_stderr=False):
...     print('there should be something after this -> ', end='', flush=True)
...     print('<- there should be something before this', file=sys.stderr)
there should be something after this -> <- there should be something before this

Adapted from
https://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions
'''
import os


class Suppressor(object):
    '''Only show ouput written to specific channels. Suppress all other output.'''
    def __init__(self, suppress_stdout=True, suppress_stderr=True):
        self.suppress = {1: bool(suppress_stdout), 2: bool(suppress_stderr)}
        # Open a pair of null files
        self.null_fds = {k: os.open(os.devnull, os.O_RDWR) for k, s in self.suppress.items() if s}
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = {k: os.dup(k) for k, s in self.suppress.items() if s}
    
    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        [os.dup2(self.null_fds[k], k) for k, s in self.suppress.items() if s]
    
    def __exit__(self, *args):
        # Re-assign the real stdout/stderr back to (1) and (2)
        [os.dup2(self.save_fds[k], k) for k, s in self.suppress.items() if s]
        # Close the null files
        [os.close(fd) for fd in self.null_fds.values()]


class ErrorSuppressor(Suppressor):
    '''Only shows output written to stdout'''
    def __init__(self):
        super(ErrorSuppressor, self).__init__(suppress_stdout=False)


class OutputSuppressor(Suppressor):
    '''Only shows output written to stderr'''
    def __init__(self):
        super(OutputSuppressor, self).__init__(suppress_stderr=False)


if __name__ == '__main__':
    ### This seems to low-level for doctest :(
    # import doctest
    # doctest.testmod()
    
    ### Test directly:
    import sys
    with Suppressor():
        print('out SHOULD NOT SHOW', file=sys.stdout)
        print('err SHOULD NOT SHOW', file=sys.stderr)
    with ErrorSuppressor():
        print('err SHOULD NOT SHOW', file=sys.stderr)
    with OutputSuppressor():
        print('out SHOULD NOT SHOW', file=sys.stdout)
    with Suppressor(suppress_stdout=False, suppress_stderr=False):
        print('there should be something after this -> ', end='', flush=True)
        print('<- there should be something before this', file=sys.stderr)

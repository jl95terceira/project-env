import os.path
import signal
import sys
import typing
#import warnings

def is_module(path:str):

    return path.endswith('.py') or (os.path.isdir(path) and os.path.exists(os.path.join(path,'__init__.py')))

def is_this_windows():

    return sys.platform == 'win32'

TEMP_DIR = 'C:\\Temp' if is_this_windows() else '/tmp'

def get_user_env(name  :str,
                 expand:bool=False):
    
    return (os.popen(f'powershell -NoProfile -Command "(Get-Item -Path HKCU:\\Environment).GetValue(\'{name}\')"') if expand else \
            os.popen(f'powershell -NoProfile -Command "(Get-Item -Path HKCU:\\Environment).GetValue(\'{name}\', $null, \'DoNotExpandEnvironmentNames\')"')).read()

class Enumerator[T]:

    def __init__(self):

        self._managed:list[T] = list()
    
    def __call__(self, x:T):

        self._managed.append(x)
        return x
    
    #@warnings.deprecated
    def E(self, x:T): 
        
        """
        DEPRECATED
        """
        self(x)

    def __iter__(self):

        return self._managed.__iter__()

def or_repr(items:list[str]):

    return repr(items[0]) if len(items) == 1 else f'{', '.join(map(repr,items[:-1]))} or {repr(items[-1])}'

def and_repr(items:list[str]):

    return repr(items[0]) if len(items) == 1 else f'{', '.join(map(repr,items[:-1]))} and {repr(items[-1])}'

_SIGINT_HOOKS:list[typing.Callable[[],None]] = []
def _SIGINT_MASTER_HANDLER(sig, frame):

    for hook in _SIGINT_HOOKS: hook()

signal.signal(signal.SIGINT, _SIGINT_MASTER_HANDLER)
#def add_sigint_hook(hook:typing.Callable[[],None]):
#
#    _SIGINT_HOOKS.append(hook)
#
#add_sigint_hook(lambda: print('--------SIGINT--------'))
def agetter(o:typing.Any):

    def _f(a:str): return getattr(o,a)
    return _f

_SYS_ARGV_ITER = iter(sys.argv[1:])
def a():

    next(_SYS_ARGV_ITER)

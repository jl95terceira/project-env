import builtins
import os
import os.path
import pathlib
import pickle
import typing

from .util  import *
from .state import *
from .vars  import *

_APPDATA_DIR_LASTNAME   = 'PYTOOLS-0732FEBD06784C248FD1AB7E046D92A6'
_VARS_FILENAME          = '__ENV__.py'
_STATE_FILENAME         = 'state.pkl'
_APPDATA_DIR            = os.path.join(os.getenv('APPDATA') if is_this_windows() else \
                                       pathlib.Path.home(), _APPDATA_DIR_LASTNAME)
VARS_FILEPATH          = os.path.join(_APPDATA_DIR, _VARS_FILENAME)
STATE_FILEPATH         = os.path.join(_APPDATA_DIR ,_STATE_FILENAME)

## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 
## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

class _Global:

    loaded                      = False
    state                       = State(fn=STATE_FILEPATH)   
    varmap:dict[str,typing.Any] = dict() 

def print(v:Verbosity,*a,**ka):

    if _Global.state.verbos.level < v.level: return
    builtins.print('[VERBOSE]',*a,**ka)

def reload():

    os.makedirs(os.path.split(STATE_FILEPATH)[0],exist_ok=True)
    if os.path.exists(STATE_FILEPATH):

        load_success = False
        load_ex      = None
        with open(STATE_FILEPATH, 'rb') as cache_file:

            try:
                
                _Global.state = pickle.load(cache_file)
                print(Verbosities.HIGH, f'State loaded from file {repr(STATE_FILEPATH)}')
                _Global.state.save_cb = lambda: print(Verbosities.HIGH, 'State saved')
            
            except Exception as ex:

                print(Verbosities.LOW, f'Error on loading state - {ex}')
                load_ex = ex

            else:

                load_success = True
        
        if not load_success:

            os.remove(STATE_FILEPATH)

    else:

        print(Verbosities.HIGH, f'State file ({repr(STATE_FILEPATH)}) NOT found - to create')
        _Global.state.save()

    if os.path.exists(VARS_FILEPATH): 

        print(Verbosities.HIGH, f'Variables file {VARS_FILEPATH} exists - to load')
        with open(VARS_FILEPATH, mode='r', encoding='utf-8') as f:

            try:
            
                _Global.varmap.update(dict(eval(f.read())))
            
            except Exception as ex:

                builtins.print(f'ERROR on loading variables file ({VARS_FILEPATH}) - {ex}')
                
            if _Global.varmap:

                padl = max(map(len, _Global.varmap))
                print(Verbosities.HIGH, f'Variables set:\n{'\n'.join(f' - {k}{(padl-len(k))*' '} = {repr(v)}' for k,v in sorted(_Global.varmap.items()))}')

    else:

        print(Verbosities.MEDIUM, f'Variables file {repr(VARS_FILEPATH)} does NOT exist - to create')
        with open(VARS_FILEPATH, mode='w', encoding='utf-8') as f: 

            f.write('{}')

    if not _Global.loaded: print(Verbosities.HIGH, 'Environment loaded and ready')
    else                 : print(Verbosities.HIGH, 'Environment reloaded')
    _Global.loaded = True

def load_ensured(f:typing.Callable):

    def g(*a,**ka):

        if not _Global.loaded: reload()
        return f(*a,**ka)
    
    return g

@load_ensured
def reset_state():

    _Global.state = State(STATE_FILEPATH)
    print(Verbosities.LOW, f'state reset')
    if os.path.exists(STATE_FILEPATH):

        os.remove(STATE_FILEPATH)
        print(Verbosities.LOW, f'state file ({repr(STATE_FILEPATH)}) removed')

    else:

        print(Verbosities.LOW, f'state file ({repr(STATE_FILEPATH)}) not found - nothing to remove')

@load_ensured
def var[T](name       :str,
           type       :typing.Callable[[typing.Any],T]=str,
           description:str                            ='',
           default    :T|NoDefaultType                =NO_DEFAULT):

    return Var(varmap =_Global.varmap,
               name       =name,
               type       =type,
               description=description,
               default    =default)

class EditorTypeNotValid(Exception): pass
def _editor(o) -> typing.Callable[[typing.Any],str]:

    if isinstance(o, str): return _editor(lambda file_path: f'{o} {file_path}')
    if callable  (o): 

        try: 
            
            r = o('test/file/path')
            if not isinstance(r, str): raise EditorTypeNotValid(o)

        except: raise EditorTypeNotValid(o)
        return o

EDITOR = var(name   ='editor',
             type   =_editor,
             default=_editor('notepad'))


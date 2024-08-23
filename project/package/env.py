import builtins
import os
import os.path
import pathlib
import pickle
import types
import typing

from env_lib.util  import *
from env_lib.state import *
from env_lib.vars  import *

_APPDATA_DIR_LASTNAME   = 'PYTOOLS-0732FEBD06784C248FD1AB7E046D92A6'
_VARS_FILENAME          = '__ENV__.py'
_STATE_FILENAME         = 'state.pkl'
_APPDATA_DIR            = os.path.join(os.getenv('APPDATA') if is_this_windows() else \
                                       pathlib.Path.home(), _APPDATA_DIR_LASTNAME)
_VARS_FILEPATH          = os.path.join(_APPDATA_DIR, _VARS_FILENAME)
_STATE_FILEPATH         = os.path.join(_APPDATA_DIR ,_STATE_FILENAME)

## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 
## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

class _Global:

    loaded                      = False
    state                       = State(fn=_STATE_FILEPATH)   
    varmap:dict[str,typing.Any] = dict() 

def print(v:Verbosity,*a,**ka):

    if _Global.state.verbos.level < v.level: return
    builtins.print('[VERBOSE]',*a,**ka)

def reload():

    os.makedirs(os.path.split(_STATE_FILEPATH)[0],exist_ok=True)
    if os.path.exists(_STATE_FILEPATH):

        load_success = False
        load_ex      = None
        with open(_STATE_FILEPATH, 'rb') as cache_file:

            try:
                
                _Global.state = pickle.load(cache_file)
                print(Verbosities.HIGH, f'State loaded from file {repr(_STATE_FILEPATH)}')
                _Global.state.save_cb = lambda: print(Verbosities.HIGH, 'State saved')
            
            except Exception as ex:

                print(Verbosities.LOW, f'Error on loading state - {ex}')
                load_ex = ex

            else:

                load_success = True
        
        if not load_success:

            os.remove(_STATE_FILEPATH)

    else:

        print(Verbosities.HIGH, f'State file ({repr(_STATE_FILEPATH)}) NOT found - to create')
        _Global.state.save()

    if os.path.exists(_VARS_FILEPATH): 

        print(Verbosities.MEDIUM, f'Variables file {_VARS_FILEPATH} exists - to load')
        with open(_VARS_FILEPATH, mode='r', encoding='utf-8') as f:

            try:
            
                _Global.varmap.update(dict(eval(f.read())))
            
            except Exception as ex:

                builtins.print(f'ERROR on loading variables file ({_VARS_FILEPATH}) - {ex}')
                
            if _Global.varmap:

                padl = max(map(len, _Global.varmap))
                print(Verbosities.HIGH, f'Variables set:\n{'\n'.join(f' - {k}{(padl-len(k))*' '} = {repr(v)}' for k,v in sorted(_Global.varmap.items()))}')

    else:

        print(Verbosities.MEDIUM, f'Variables file {repr(_VARS_FILEPATH)} does NOT exist - to create')
        with open(_VARS_FILEPATH, mode='w', encoding='utf-8') as f: 

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

    _Global.state = State(_STATE_FILEPATH)
    print(Verbosities.LOW, f'state reset')
    if os.path.exists(_STATE_FILEPATH):

        os.remove(_STATE_FILEPATH)
        print(Verbosities.LOW, f'state file ({repr(_STATE_FILEPATH)}) removed')

    else:

        print(Verbosities.LOW, f'state file ({repr(_STATE_FILEPATH)}) not found - nothing to remove')

@load_ensured
def var[T](name   :str,
           type   :typing.Callable[[typing.Any],T]=str,
           default:T|NoDefaultType                =NO_DEFAULT):

    return Var(varmap =_Global.varmap,
               name   =name,
               type   =type,
               default=default)

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

if __name__ == '__main__':

    import argparse

    class P:

        LIST   = 'list'
        VERBOS = 'verbos'
        RESET  = 'reset'
        OPEN   = 'open'

    DESCRIPTION = '\n'.join((
                                    
        f'',
        f'This is help for setting up your devtools environment, to be more productive.',
        f'',
        f'Edit your variables file with sub-command {repr(P.OPEN)}.', 
        f'Having a variables file helps with not having to pass certain optional arguments to certain devtools - if these arguments are not given, their values will be looked up in the env file.',
        f'Whenever a devtool is called, the variables file is read as a Python **dict** and its entries are assumed to match with the local environment.',
        f'',
        f'This tool has a mutable state. Every time the state changes, it is saved to file {_STATE_FILEPATH}.',
    
    ))
    def default_list(args): builtins.print('\n'.join((lambda l: (f'    {repr(v.key)}{(l-len(v.key))*' '} : {v.descr}' for v in Vars.values()))(max(map(len,(v.key for v in Vars.values()))))))

    def default_verb(args):

        levelrepr = get('v')
        if levelrepr is None:

            builtins.print(f'Verbosity = {_Global.state.verbos.level}')
            return

        level = int(levelrepr)
        if level not in VERBOSITY_BY_LEVEL:

            print(Verbosities.LOW, f'verbosity level {level} not mapped')
            return
        
        _Global.state.verbos = VERBOSITY_BY_LEVEL[int(get('v'))]

    def default_reset(args): reset_state()

    def default_open(args): 
        
        os.system(EDITOR.get()(_VARS_FILEPATH))

    p = argparse.ArgumentParser       (formatter_class=argparse.RawTextHelpFormatter,
                                       description    =DESCRIPTION)
    sp = p.add_subparsers(dest='_SP',help='sub-commands')
    o  = sp.add_parser(P.OPEN,
                       formatter_class=argparse.RawTextHelpFormatter,
                       help   =f'open the variables file - located at {repr(_VARS_FILEPATH)}')
    o.set_defaults    (_F=default_open)
    l  = sp.add_parser(P.LIST,
                       formatter_class=argparse.RawTextHelpFormatter,
                       help=f'list all entries that may be looked up in the variables file and what they should match with')
    l.set_defaults    (_F=default_list)
    v  = sp.add_parser(P.VERBOS,
                       formatter_class=argparse.RawTextHelpFormatter,
                       help=f'set verbosity level')
    v.add_argument    ('v',
                       help=f'verbosity level\nPossible values:\n{'\n'.join(map(lambda v: f'- {v.level} ({v.descr})', Verbosities.values()))}',
                       nargs='?')
    v.set_defaults    (_F=default_verb)
    r  = sp.add_parser(P.RESET,
                       formatter_class=argparse.RawTextHelpFormatter,
                       help   =f'reset the state / remove the state file - located at {repr(_STATE_FILEPATH)}')
    r.set_defaults    (_F=default_reset)
    args = p.parse_args()
    get  = agetter(args)
    if get('_SP') is None:

        builtins.print(f'For help, give option \'-h\'.')
        exit(0)
    
    get('_F')(args)

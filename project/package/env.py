import argparse
import builtins
import os

import envlib
from envlib import (
    _Global,
)
import envlib.vars.builtin

if __name__ == '__main__':

    class P:

        VERBOS = 'verbos'
        RESET  = 'reset'
        OPEN   = 'open'

    DESCRIPTION = '\n'.join((
                                    
        f'',
        f'Edit your variables file with sub-command {repr(P.OPEN)}.', 
        f'Having a variables file helps with not having to pass certain optional arguments to certain devtools - if these arguments are not given, their values will be looked up in the env file.',
        f'Other tools may retrieve variables from this file (through Python methods of this module), to know about the user environment (such as application paths).',
        f'',
        f'This tool manages a state. Every time the state changes, it is saved to file {envlib.STATE_FILEPATH}.',
    
    ))
    def default_verbos(args):

        levelrepr = get('v')
        if levelrepr is None:

            builtins.print(f'Verbosity = {_Global.state.verbos.level}')
            return

        level = int(levelrepr)
        if level not in envlib.state.VERBOSITY_BY_LEVEL:

            print(envlib.state.Verbosities.LOW, f'verbosity level {level} not mapped')
            return
        
        _Global.state.verbos = envlib.state.VERBOSITY_BY_LEVEL[int(get('v'))]

    def default_reset(args): envlib.reset_state()

    def default_open(args): 
        
        os.system(envlib.vars.builtin.EDITOR.get()(envlib.VARS_FILEPATH))

    p = argparse.ArgumentParser       (formatter_class=argparse.RawTextHelpFormatter,
                                       description    =DESCRIPTION)
    sp = p.add_subparsers(dest='_SP',help='sub-commands')
    o  = sp.add_parser(P.OPEN,
                       formatter_class=argparse.RawTextHelpFormatter,
                       help=f'open the variables file - located at {repr(envlib.VARS_FILEPATH)}')
    o.set_defaults    (_F=default_open)
    v  = sp.add_parser(P.VERBOS,
                       formatter_class=argparse.RawTextHelpFormatter,
                       help=f'set verbosity level\nThis may be used not only by this tool but also by other tools to control the level of verbosity in console output\nCurrent value: {_Global.state.verbos.level} ({_Global.state.verbos.descr})')
    v.add_argument    ('v',
                       help=f'verbosity level\nPossible values:\n{'\n'.join(map(lambda v: f'- {v.level} ({v.descr})', envlib.state.Verbosities.values()))}',
                       nargs='?')
    v.set_defaults    (_F=default_verbos)
    r  = sp.add_parser(P.RESET,
                       formatter_class=argparse.RawTextHelpFormatter,
                       help=f'reset the state / remove the state file - located at {repr(envlib.STATE_FILEPATH)}')
    r.set_defaults    (_F=default_reset)
    args = p.parse_args()
    get  = args.__getattribute__
    if get('_SP') is None:

        builtins.print(f'For help, give option \'-h\'.')
        exit(0)
    
    get('_F')(args)

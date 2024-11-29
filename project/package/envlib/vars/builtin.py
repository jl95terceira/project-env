import os.path as path
import typing

from .. import var

from jl95terceira.batteries import os

class EditorTypeNotValid(Exception): pass
def _editor(o) -> typing.Callable[[str],str]:

    if isinstance(o, str): return _editor(lambda file_path: f'{o} {file_path}')
    if callable  (o): 

        try: 
            
            r = o(path.join('test','file','path'))
            if not isinstance(r, str): raise EditorTypeNotValid(o)

        except: raise EditorTypeNotValid(o)
        return o

EDITOR           = var(name       ='editor',
                       description='default text file editor',
                       type       =_editor,
                       default    =_editor('notepad'))
TEMP             = var(name       ='temp', 
                       description='a directory that may be used to hold temporary files',
                       type       =str,
                       default    =os.TEMP_DIR)

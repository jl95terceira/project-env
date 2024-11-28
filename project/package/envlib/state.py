import pickle
import typing

from jl95terceira.batteries import *

# If this class is not separated from env.py, problems arise with pickling.

class Verbosity:

    def __init__(self,level:int,descr:str):

        self.level = level
        self.descr = descr

class Verbosities:

    _e = Enumerator[Verbosity]()

    OFF       = _e(Verbosity(0,'Off'))
    LOW       = _e(Verbosity(1,'Low'))
    MEDIUM    = _e(Verbosity(2,'Medium'))
    HIGH      = _e(Verbosity(3,'High'))

    @staticmethod
    def values(): yield from Verbosities._e

VERBOSITY_BY_LEVEL = {v.level:v for v in Verbosities.values()}

class State:

    def __init__(self,fn:str,save_cb:typing.Callable[[],None]=lambda: None):

        self._fn      = fn
        self._verbos  = Verbosities.MEDIUM
        self._save_cb = save_cb

    def save(self):

        svc = self.save_cb
        self.save_cb = None
        with open(self._fn, 'wb') as cache_file:

            pickle.dump(file=cache_file, obj=self)
        
        self.save_cb = svc
        self.save_cb()

    def autosaved(f):

        def w(self:'State', *a,**ka):

            r = f(self, *a,**ka)
            self.save()
            return r

        return w

    def _get_verbos(self): return self._verbos
    @autosaved
    def _set_verbos(self,v:Verbosity): self._verbos = v
    verbos:Verbosity = property(fget=_get_verbos,fset=_set_verbos)

    def _get_save_cb(self): return self._save_cb
    def _set_save_cb(self,save_cb:typing.Callable[[],None]): self._save_cb = save_cb
    save_cb = property(fget=_get_save_cb,fset=_set_save_cb)


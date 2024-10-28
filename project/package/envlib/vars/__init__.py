import typing

class VarNotDefinedException(Exception):

    def __init__(self, v:'Var'): super().__init__(str(v))

class NoDefaultType: pass
NO_DEFAULT = NoDefaultType()
class Var[T]:

    def __init__(self,
                 varmap      :dict[str,typing.Any], 
                 name        :str, 
                 type        :typing.Callable[[typing.Any],T], 
                 description :str            ='',
                 default     :T|NoDefaultType=NO_DEFAULT):

        self._varmap      = varmap
        self._name        = name
        self._description = description
        self._type        = type
        self._default     = default

    def check(self): return self._name in self._varmap

    def _typed(f):

        def g(self,*a,**ka):

            return self._type(f(self,*a,**ka))
        
        return g

    @_typed
    def get(self) -> T: 
        
        if not self.check(): 

            if self._default is not NO_DEFAULT: return self._default    
            else                              : raise  VarNotDefinedException(self._name)
        
        return self._varmap[self._name]
    
    @_typed
    def get_or(self, default:T) -> T:

        try                          : return self.get()
        except VarNotDefinedException: return default

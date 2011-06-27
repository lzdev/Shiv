#!/usr/bin/env python
#
#       callback.py
#       
#       Copyright 2009 yousuf <yousuf@postocode53.com>
#       

class Callback(object):
    _instance = None
    _registry = {}
    _index = 0
    
    def __new__(cls, *args, **kwargs):
        if cls != type(cls._instance):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def register(self, func):        
        key = str(self._index)+func.func_name
        def wrap(*args, **kwargs):
            return func(*args, **kwargs)
            
        self._registry[key] = wrap
        self._index+=1
        wrap.key=key
        return wrap


#!/usr/bin/env python
#
#       data_methods.py
#       
#       Copyright 2009 yousuf <yousuf@postocode53.com>
#
from django.core.cache import cache
from django.utils.safestring import mark_safe
import re
import time
import cPickle as pickle
    
class Memoize(object):
    def __init__(self, keyfunc,timeout=None):
        self.keyfunc = keyfunc
        self.timeout = timeout

    def __call__(self, fn):
        def wrapped(*args, **kwargs):
            if 'get_key' in kwargs:
                del kwargs['get_key']
                return pickle.dumps((fn.func_name, self.keyfunc(*args, **kwargs)))
                
            if not wrapped.func_dict.get('state', None):
                wrapped.state = {}
            if 'reset' in kwargs:
                del kwargs['reset']
                key = pickle.dumps((fn.func_name, self.keyfunc(*args, **kwargs)))
                wrapped.state[key] = 0
                
            key = pickle.dumps((fn.func_name, self.keyfunc(*args, **kwargs)))
            if wrapped.state.get(key,0) == 0:
                wrapped.state[key] = time.time()
                cache.delete(key)
            for f, state in wrapped.func_dict.get('depends',{}).items():
                    if f.state[state[0]] != state[1]:
                        cache.delete(key)

            value = cache.get(key)
            if not value:
                value = fn(*args, **kwargs)
                if self.timeout:
                   cache.set(key, pickle.dumps(value),self.timeout)
                else:
                    cache.set(key, pickle.dumps(value))
            else:
                value = pickle.loads(value)
            return value
        return wrapped

def merge(init_dict, new_data):
    for module, value in init_dict.items():
        if module in new_data:
            init_dict[module]['value'] = True
        for cls in value['classes'].keys():
            if cls in new_data:
                init_dict[module]['classes'][cls] = True
    return init_dict


def slugify(value,replace_with='_'):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value=unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return mark_safe(re.sub('[-\s]+', replace_with, value))
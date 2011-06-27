#!/usr/bin/env python
#
#       tab.py
#       

from django.conf import settings
from django.template.loader import get_template
from shiv.container import Container
from shiv.nodes import Node



class TabMeta(type):
    def __init__(cls, name, bases, dict):
        for b in bases:
            if hasattr(b, '_registry'):
                b._registry[name] = cls
                cls.tab_id = dict['__module__'].rsplit('.',1)[0] + name
                module = __import__(dict['__module__'].rsplit('.',1)[0]+'.media', fromlist=[dict['__module__'].rsplit('.',1)[0]])
                try:
                    cls._media = getattr(module, name+'Media')()
                except AttributeError:
                    cls._media = getattr(module, 'DefaultMedia')()
                cls._media.css=[e.startswith('http') and e or cls._media.css_prefix+e for e in cls._media.css]
                cls._media.extra_css = dict['_element_class']._media.css
                cls._media.js=[e.startswith('http') and e or cls._media.js_prefix+e for e in cls._media.js]
                cls._media.extra_js = dict['_element_class']._media.js
                if settings.TEMPLATE_CACHING:
                    cls._media.template = get_template(cls._media.template)
                break
        return type.__init__(cls, name, bases, dict)
        
class Tab(Container):
    __metaclass__ = TabMeta
    _registry = {}
    title = "Tab"
    
    def __init__(self,request , is_default, tab_client=None):
        self.is_default = is_default
        self.user = request.user
        self.client = tab_client
        self.context = {'elements': [], 'is_default': is_default,
                            'id': self.tab_id, 'title': Node(self.title),
                            'images': self._media.images}
        self._prepare()        
        self.request=request

    def _prepare(self):
        self.ids = [self.client]
        
    def _get_elements(self, element_class, start, count, data):
        end = ((start+1)*count) < len(data) and ((start+1)*count) or len(data)
        return [ element_class( client = id,request=self.request,
                                ) for id in data[start*count:end] ]
        
    def show(self, template = None, is_json = False, start = 0, count = 10, next_key=None, prev_key=None):
        if self.is_default:
            element_class = self._element_class
            self.context['elements'] = [e.show(is_json = is_json)\
                                    for e in self._get_elements(element_class,
                                    start, count, self.ids)]

            self.context['has_next'] = (start*count+count) < len(self.ids)        

        if self.context.get('has_next', False) and next_key:            
            self.context['Next'] = Node('Next', data_id='%s+%d' % (next_key, start+1))
        if start and prev_key:
            self.context['Prev'] = Node('Prev', data_id='%s+%d' % (prev_key, start-1))
            
        context = {}
        if (not is_json) and self.is_default:
            context['html'] = super(Tab, self).show(template = template,
                                request=self.request,
                                context = self.context,
                                is_json = is_json)
        context.update(self.context)
        if hasattr(self, 'client'):
            context['client'] = str(self.client)
        return context


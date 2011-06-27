#!/usr/bin/env python
#
#       container.py
#       
from django.template.context import RequestContext
from django.template.loader import get_template
       
class Container(object):        
    def show(self,template=None,request=None,  context=None, is_json=False):
        context = context or self.context
        if is_json:
            return context
        template = template or self._media.template        
        return get_template(template).render(RequestContext(request,context)) if isinstance(template, str) else  template.render(RequestContext(request,context))
        



#!/usr/bin/env python
#
#       page.py
#       
#       Copyright 2010 yousuf <yousuf@postocode53.com>
#
import json

from shiv import data_methods as dm
from shiv.auth import login_required as lr
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import inspect
from shiv.container import Container
from shiv.utils.cssmin import cssmin
from shiv.utils.jsmin import jsmin

class PageMeta(type):
    def __init__(cls, name, bases, dict):
        for b in bases:
            if hasattr(b, '_registry'):
                b._registry[name] = cls
                cls.page_id = name                
                #cls._media.template = get_template(cls._media.template)
                break
        return type.__init__(cls, name, bases, dict)
        
class Page(Container):
    __metaclass__ = PageMeta
    _registry = {}
    title = "Page"
    
    def __init__(self, login_required=True, login_url=None, permission=None):
        self.module = self.__module__.split('.')[-2]       
        if permission:
            self.view = permission_required(permission, login_url)(self.view)
        if login_required:
            self.view = lr(self.view, login_url)
        self.context = {}
        self.css, self.js = self.get_css_js()        

    def unique_list(self, l):
        ulist = []
        [ulist.append(x) for x in l if x not in ulist]
        return ulist

    def __call__(self, request, *args,  ** kwargs):        
        meta_log=dict([(e, request.META.get(e,'N/A')) for e in settings.META_LOGGER])        
        log_info={
        'USER':request.user.username or str(request.user),
        'PATH':request.path,
        'PARAMS' :request.REQUEST.items(),
        'META':meta_log,
        }        
        settings.LOGGER.info(json.dumps(log_info))
        user = request.user
        excludes = dm.get_excludes(user)        
        if self.module in excludes:
            return HttpResponseRedirect(reverse('master_prelogin_page'))
        check_loggedin={
                     None:True,
                     False: isinstance(user, AnonymousUser),
                     True:not isinstance(user, AnonymousUser),
                      }        
        self.boxes = filter(lambda x:  x.__module__ + '.' + (x.__name__ if inspect.isclass(x) else x.__class__.__name__) not in excludes and x.__module__ not in excludes, self.boxes)
        self.boxes=filter(lambda x: check_loggedin[getattr(x,'_for_loggedin')] ,self.boxes)
        return self.view(request, *args,  ** kwargs)
        
    def view(self, request, * args,  ** kwargs):        
        if hasattr(self, 'request_validator'):
            if not self.request_validator(request, args, kwargs):
                raise Http404
        return self.show(request, * args,  ** kwargs)

    def show(self, request, * args,  ** kwargs):                
        self.context['boxes'] = [inspect.isclass(e) and e(request, module=self.module, * args,  ** kwargs).show() or e.show() for e in self.boxes]
        self.context['header'] = hasattr(self, 'header') and (inspect.isclass(self.header) and self.header(request, module=self.module).show() or self.header.show())
        self.context['footer'] = hasattr(self, 'footer') and self.footer(request, module=self.module).show() or ''
        self.context['css'] = self.css
        self.context['js'] = self.js        
        x=getattr(self, 'page_title','')
        self.context['title']=x(request,args,kwargs) if x.__class__.__name__=='function' else x
        return HttpResponse(super(Page, self).show(self.template,request, None, None))

    def get_css_js(self):
        css = []
        js = []
        for e in self.__dict__.values():            
            if isinstance(e, list):
                for b in e:
                    if inspect.isclass(b) and (isinstance(b, Container) or issubclass(b, Container)):
                        css.extend(b.get_css())
                        js.extend(b.get_js())
                continue

            if inspect.isclass(e) and (isinstance(e, Container) or issubclass(e, Container)):
                css.extend(e.get_css())
                js.extend(e.get_js())

        #js minification function
        if settings.JS_MINIFY:
            js=minify_js(self.unique_list(js),"%s_%s_"%(self.module,self.page_id))

        #css minification function
        if settings.CSS_MINIFY:
            css= minify_css(self.unique_list(css),"%s_%s_"%(self.module,self.page_id))

        return [x[:-1] if x.endswith('/') else x for x in self.unique_list(css)], [x[:-1] if x.endswith('/') else x for x in self.unique_list(js)]
        
class DefaultPage(Page):
    template = "master/PageHome.html"

    def show(self, request, * args,  ** kwargs):
        self.context = {}
        self.context['menu'] = inspect.isclass(self.menu) and  hasattr(self, 'menu') and self.menu(request, module=self.module).show() or ''
        self.context['subheader'] = inspect.isclass(self.subheader) and  hasattr(self, 'subheader') and self.subheader(request, module=self.module).show() or  ''
        return super(DefaultPage, self).show(request, * args,  ** kwargs)


def minify_js(js,page_id):
        xs = []
        jsdata = ''
        for e in js:
            if e.startswith('http'):
                xs.append(e)
                continue
            try:
                f=open(settings.PROJECT_PATH + e)                                    
                jsdata += '\n//' + e + '\n' + f.read() + '\n'
                f.close()
            except:pass
        of = open(settings.MEDIA_ROOT + '/js/minified/' + page_id + '.js', 'w')
        if settings.DEBUG:
            of.write(jsmin(jsdata))
        else:
            of.write(jsmin(jsdata))
        of.close()
        js=xs + ['/static/js/minified/'+ page_id + '.js']
        return js
    
def minify_css(css,page_id):        
        xs = []
        cssdata = ''
        for e in css:
            if e.startswith('http'):
                xs.append(e)                
                continue
            try:
                f=open(settings.PROJECT_PATH + e)                                
                cssdata+='\n/*' + e + '*/\n' + f.read()
            except:pass
                
        of = open(settings.MEDIA_ROOT + '/css/minified/' + page_id + '.css', 'w')
        of.write(cssmin("".join(cssdata)))
        of.close()
        css=xs + ['/static/css/minified/' + page_id + '.css']
        return css


def redirect_to_internal(url, index=1):
    # NOTE check university name removal part
    url_list = url.split('/')
    url_list.pop(index)
    url_list.pop(index)
    url = "/".join(url_list)
    return HttpResponseRedirect(url)

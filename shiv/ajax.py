# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__ = "naved"
__date__ = "$22 Jun, 2010 1:32:06 PM$"
import json

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from shiv.callback import Callback

cb = Callback()

def unique_list(l):
    ulist = []
    [ulist.append(x) for x in l if x not in ulist]
    return ulist

def get_callback(request):
    meta_log=dict([(e, request.META.get(e,'N/A')) for e in settings.META_LOGGER])

    log_info={
    'USER':request.user.username or str(request.user),
    'PATH':request.path,
    'PARAMS' :request.REQUEST.items(),
    'META':meta_log,
    }
    settings.LOGGER.info(json.dumps(log_info))
    if request.GET:        
        if not len(request.GET) or not request.GET.get('data_id'): return HttpResponse("No Parameters Specified")
        data_id = request.GET['data_id'].split('+')
    else:        
        if not len(request.POST) or not request.POST.get('data_id'): return HttpResponse("No Parameters Specified")
        data_id = request.POST['data_id'].split('+')
    func = cb._registry[data_id[0]]
    
    if func.func_dict.get("allowAnonymous", None) or not isinstance(request.user, AnonymousUser):
        return func(request)
    else:
        return HttpResponse("User Not Authorized")
    

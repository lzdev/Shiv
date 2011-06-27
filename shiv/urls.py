from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="naved"
__date__ ="$22 Jun, 2010 1:42:04 PM$"

urlpatterns = patterns('',
                       url(r'^callback', 'base.ajax.get_callback', name='ajax_url'),
                       )
 
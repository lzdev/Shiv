#!/usr/bin/env python
#
#       extra_tags.py
#       
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def form_as_shiv(form, state):
    return form.as_shiv(state = state)

@register.filter
def render_node(node):
  if node['type'] == 'has_data_id':
    t = "<%(tag_type)s class='has_data_id %(extra_class)s' data-id='%(data_id)s'>%(text)s</%(tag_type)s>" % node
  elif node['type'] == 'has_link':
    t = "<a href='%(link)s' class='has_link %(extra_class)s' target='%(target)s'>%(text)s</a>" % node
  elif node['type'] == 'has_image':
    t = "<a href='%(link)s' class='has_image %(extra_class)s' target='%(target)s'><img class='rollover' data-rollover='%(image_link_over)s' src='%(image_link)s' alt='%(text)s' /></a>"
  else:
    t = "<%(tag_type)s class='plain_text %(extra_class)s'>%(text)s</%(tag_type)s>" % node
  return mark_safe(t)

@register.filter
def truncate_length(string, arg):
    if len(string) > arg:
        return string[:arg-3] + '...'
    return string

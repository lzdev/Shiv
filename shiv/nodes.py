#!/usr/bin/env python
#
#       nodes.py
#       

class Node(dict):
    def __init__(self, text, link = None, data_id = None,target='_self', image_link = None, image_link_over=None, extra_class = '', tag_type=None):
        type = (link and not image_link and 'has_link') or (data_id and 'has_data_id') or (link and image_link and 'has_image') or 'plain_text'
        tag_type = tag_type or 'span'    
        link = link or ''
        text = text
        data_id = data_id or ''
        image_link = image_link or ''
        image_link_over = image_link_over or ''
        target = target
        extra_class = extra_class
        self.update(locals())
        self.__delitem__('self')

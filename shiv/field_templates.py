#!/usr/bin/env python
#
#       field_templates.py
#       

DEFAULT_TEMPLATE = u''' <div class="fieldWrapper">
                            <div class="fieldLabel">%(label)s</div>
                            <div class="fieldInput %(state)s">%(field)s</div>
                            <div class="fieldErrors">%(errors)s</div>
                            <div class="fieldHelp">%(help_text)s</div>
                        </div> 
                    '''
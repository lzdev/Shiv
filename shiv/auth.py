
from django.contrib.auth.decorators import user_passes_test

def login_required(function=None, login_url=None, redirect_field_name='next'):
    actual_decorator = user_passes_test(
                                        lambda u: u.is_authenticated(),
                                        login_url=login_url,
                                        redirect_field_name=redirect_field_name
                                        )
    if function:
        return actual_decorator(function)
    return actual_decorator    

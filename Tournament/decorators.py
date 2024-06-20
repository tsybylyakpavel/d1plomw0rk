# Декораторы для проверки принадлежности пользователя к определенной группе
from django.core.exceptions import PermissionDenied

def group_required(group_name):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.groups.filter(name=group_name).exists():
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def user_is_organizer(function):
    def wrap(request, *args, **kwargs):
        if request.user.groups.filter(name='Organizer').exists():
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap

def user_is_captain_or_organizer(function):
    def wrap(request, *args, **kwargs):
        if request.user.groups.filter(name='Organizer').exists() or request.user.groups.filter(name='Captain').exists():
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap
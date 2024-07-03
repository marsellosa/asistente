from functools import wraps
from django.shortcuts import redirect

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main:inicio')
        return view_func(request, *args, **kwargs)
    return wrapper_func

# def allowed_users(allowed_roles=[]):
#     def decorator(view_func):
#         def wrapper_func(request, *args, **kwargs):
#             if request.user.groups.filter(name__in=allowed_roles).exists():
#                 return view_func(request, *args, **kwargs)
#             else:
#                 return redirect('main:inicio')
#         return wrapper_func
#     return decorator


def allowed_users(allowed_roles=None):
    """
    Decorator to restrict access to views based on user roles.
    
    Args:
    allowed_roles (list): List of allowed role names.
    
    Returns:
    function: Decorator function.
    """
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def wrapper_func(request, *args, **kwargs):
            # Check if the user is in any of the allowed groups
            if request.user.groups.filter(name__in=allowed_roles).exists():
                return view_func(request, *args, **kwargs)
            else:
                # Optionally log unauthorized access attempt
                # print(f"User {request.user.username} tried to access a restricted view.")
                return redirect('main:inicio')
        return wrapper_func
    return decorator

#Проверка ролей пользователя
from django.contrib.auth.models import Group

def user_roles(request):
    if request.user.is_authenticated:
        user = request.user
        is_organizer = user.groups.filter(name='Organizer').exists()
        is_captain = user.groups.filter(name='Captain').exists()
        return {
            'is_organizer': is_organizer,
            'is_captain': is_captain,
        }
    return {}

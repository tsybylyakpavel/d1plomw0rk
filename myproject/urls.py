from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from Tournament import views as tournament_views
from Tournament import forms as tournament_forms
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', tournament_views.home, name="index"),
    path('tourney/<int:tourney_id>/', tournament_views.tourney_main, name="tourney"),
    path('tourney/new/', tournament_views.new_tourney, name="new"),
    path('tourney/tournaments/', tournament_views.tourney_listings, name="listings"),
    path('tourney/edit_match/<int:match_not_unique_id>/<int:tourney_id>/', tournament_views.edit_match, name="edit_match"),
    path('tourney/delete_tourney/<int:tourney_id>/', tournament_views.delete_tourney, name="delete_tourney"),
    path('tourney/generate_schedule/<int:tourney_id>/', tournament_views.generate_schedule, name='generate_schedule'),
    path('accounts/profile/', tournament_views.profile, name="profile"),
    path('profile/edit/', tournament_views.edit_profile, name='edit_profile'),
    path('profile/update/', tournament_views.update_profile, name='update_profile'),
    path('login/', tournament_views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='User/logout.html'), name='logout'),
    path('register/', tournament_views.register, name='register'),
    path('tourney/<int:tourney_id>/edit/', tournament_views.edit_tourney, name='edit'),
    path('tourney/<int:tourney_id>/apply/', tournament_views.apply_for_tourney, name='apply_for_tourney'),
    path('process_application/<int:application_id>/', tournament_views.process_application, name='process_application'),
    path('captain/tourneys/', tournament_views.captain_tourney_listings, name='captain_tourney_listings'),
    path('tourney/<int:tourney_id>/upload_rules/', tournament_views.upload_rules, name='upload_rules'),
    path('generate_round_robin/<int:tourney_id>/', tournament_views.generate_round_robin, name='generate_round_robin'),
    path('verification_pending/', tournament_views.verification_pending, name='verification_pending'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
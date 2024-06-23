# Представления
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.core.paginator import Paginator
from .models import TournamentObject, Team, Match, Profile, Application, TeamMember
from .forms import CustomUserCreationForm, RulesUploadForm, CustomLoginForm
from .utils import Rounds, LosersRounds, single_tourney_update_future_rounds, double_tourney_update_future_rounds, shuffle_teams, generate_round_robin_schedule
from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.utils import timezone


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'User/login.html'

    def form_valid(self, form):
        user = form.get_user()
        if not user.profile.is_verified and user.groups.filter(name='Organizer').exists():
            form.add_error(None, ValidationError(
                "Ваш аккаунт еще не верифицирован. Пожалуйста, свяжитесь с администрацией для прохождения верификации.",
                code='unverified',
            ))
            return self.form_invalid(form)
        auth_login(self.request, form.get_user())
        return redirect(self.get_success_url())


# Главная страница
def home(request):
    return render(request, 'Tournament/home.html', {})

# Страница соревнования
def tourney(request):
    return render(request, 'Tournament/tourney.html', {})

# Создание нового соревнования
def new_tourney(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        name = request.POST.get('name', '')
        tournament_type = request.POST.get('type', '')
        num_teams = int(request.POST.get('teams', ''))
        sport = request.POST.get('sport', '')
        desc = request.POST.get('desc', '')
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')

        selected_location = request.POST.get('selectedLocation', None)
        if selected_location:
            try:
                location_lat, location_lon = map(float, selected_location.split(','))
            except (ValueError, IndexError):
                location_lat, location_lon = None, None
        else:
            location_lat, location_lon = None, None

        address = request.POST.get('address', '')

        map_zoom = request.POST.get('mapZoom', None)
        try:
            map_zoom = int(map_zoom)
        except (ValueError, TypeError):
            map_zoom = None

        map_center = request.POST.get('mapCenter', None)
        if map_center:
            try:
                map_center_lat, map_center_lon = map(float, map_center.split(','))
            except (ValueError, IndexError):
                map_center_lat, map_center_lon = None, None
        else:
            map_center_lat, map_center_lon = None, None

        created_tourney = TournamentObject(
            name=name,
            tournament_type=tournament_type,
            num_teams=num_teams,
            sport=sport,
            description=desc,
            start_date=start_date,
            end_date=end_date,
            user=request.user,
            location_lat=location_lat,
            location_lon=location_lon,
            location_address=address,
            map_zoom=map_zoom,
            map_center_lat=map_center_lat,
            map_center_lon=map_center_lon
        )
        created_tourney.save()

        for i in range(1, num_teams + 1):
            team_name = request.POST.get(f'team_{i}', '')
            if team_name:
                Team.objects.create(
                    name=team_name,
                    tournament=created_tourney
                )

        url = reverse('tourney', kwargs={'tourney_id': created_tourney.id})
        return redirect(url)

    return render(request, 'Tournament/new.html')

# Основная страница соревнования
def tourney_main(request, tourney_id):
    date = None
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        tourney_obj = get_object_or_404(TournamentObject, pk=tourney_id)

        if tourney_obj.user != request.user:
            raise PermissionDenied("Вы не авторизованы для редактирования этого соревнования.")

        team1_name = request.POST.get('edit-names-1', '')
        team1_id = int(request.POST.get('team1_id', ''))
        if team1_id != -1:
            team1_obj = get_object_or_404(Team, pk=team1_id)
            team1_obj.name = team1_name
        else:
            team1_obj = Team(name=team1_name, tournament=tourney_obj)
        team1_obj.save()

        team2_name = request.POST.get('edit-names-2', '')
        team2_id = int(request.POST.get('team2_id', ''))
        if team2_id != -1:
            team2_obj = get_object_or_404(Team, pk=team2_id)
            team2_obj.name = team2_name
        else:
            team2_obj = Team(name=team2_name, tournament=tourney_obj)
        team2_obj.save()

        match_id = int(request.POST.get('match_id', ''))
        try:
            match_obj = Match.objects.get(tournament=tourney_obj, round=match_id)
        except Match.DoesNotExist:
            match_obj = Match(tournament=tourney_obj, round=match_id)

        match_obj.team1 = team1_obj
        match_obj.team2 = team2_obj
        date = request.POST.get('match_date', '')
        if date != '':
            match_obj.date = date

        match_obj.result_team1 = request.POST.get('team1_score', None)
        match_obj.result_team2 = request.POST.get('team2_score', None)
        match_obj.winner = request.POST.get('winner', '')

        match_obj.save()

        winner = request.POST.get('winner', '')
        if tourney_obj.tournament_type == "SE":
            single_tourney_update_future_rounds(match_id, tourney_obj, winner, team1_obj, team2_obj)
        else:
            double_tourney_update_future_rounds(match_id, tourney_obj, winner, team1_obj, team2_obj)

    this_tourney = get_object_or_404(TournamentObject, pk=tourney_id)

    rounds = Rounds(this_tourney)
    applications = Application.objects.filter(tournament=this_tourney)
    approved_applications = applications.filter(status=Application.ACCEPTED)
    approved_teams = Team.objects.filter(tournament=this_tourney, application__status=Application.ACCEPTED).prefetch_related('members')
    pending_applications = applications.filter(status=Application.PENDING)
    num_slots = this_tourney.num_teams - approved_teams.count()
    slots = range(num_slots)

    # Проверка наличия уже поданной заявки
    user = request.user if request.user.is_authenticated else None
    existing_application = False
    application_status = None
    if user:
        existing_application = Application.objects.filter(user=user, tournament=this_tourney).exists()
        if existing_application:
            application_status = Application.objects.filter(user=user, tournament=this_tourney).first().status

    context = {
        'tourney': this_tourney,
        'rounds': rounds,
        'style': 'default_style',
        'location_lat': this_tourney.location_lat,
        'location_lon': this_tourney.location_lon,
        'location_address': this_tourney.location_address,
        'map_zoom': this_tourney.map_zoom,
        'map_center_lat': this_tourney.map_center_lat,
        'map_center_lon': this_tourney.map_center_lon,
        'applications': applications,
        'approved_teams': approved_teams,
        'teams_in_tourney': approved_teams,
        'num_slots': num_slots,
        'slots': slots,
        'pending_applications': pending_applications, 
        'date': date,
        'existing_application': existing_application,
        'application_status': application_status,
    }

    if this_tourney.tournament_type == "DE":
        loser_rounds = LosersRounds(this_tourney)
        context['losers'] = loser_rounds

    return render(request, 'Tournament/tourney.html', context)

# Редактирование соревнования
def edit_tourney(request, tourney_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    tourney_obj = TournamentObject.objects.get(pk=tourney_id)
    
    if request.method == 'POST':
        tourney_obj.name = request.POST.get('tourney_name', '')
        tourney_obj.description = request.POST.get('desc', '')
        tourney_obj.start_date = request.POST.get('start_date', '')
        tourney_obj.end_date = request.POST.get('end_date', '')
        tourney_obj.save()
        url = reverse('tourney', kwargs={'tourney_id': tourney_id})
        return redirect(url)
    
    if tourney_obj.user == request.user:
        return render(request, 'Tournament/edittourney.html', {'tourney': tourney_obj})
    else:
        raise PermissionDenied("Вы не авторизованы для редактирования этого соревнования.")

def tourney_listings(request):
    query = request.GET.get('search')
    sport_filter = request.GET.get('sport')
    navbar_search = request.GET.get('navbar_search', 'false') == 'true'

    if request.user.is_authenticated:
        if request.user.groups.filter(name='Organizer').exists() and not navbar_search:
            tourneys = TournamentObject.objects.filter(user=request.user)
        else:
            tourneys = TournamentObject.objects.filter(Q(archived=False) | Q(user=request.user))
    else:
        tourneys = TournamentObject.objects.filter(archived=False)

    if query:
        tourneys = tourneys.filter(Q(name__icontains=query) | Q(description__icontains=query))
    
    if sport_filter:
        tourneys = tourneys.filter(sport=sport_filter)

    paginator = Paginator(tourneys, 12)
    page = request.GET.get('page')
    tourneys = paginator.get_page(page)

    is_organizer = request.user.groups.filter(name='Organizer').exists() if request.user.is_authenticated else False
    is_captain = request.user.groups.filter(name='Captain').exists() if request.user.is_authenticated else False

    # Проверка заявок для представителей команд
    existing_applications = {}
    if is_captain:
        for tourney in tourneys:
            application_exists = Application.objects.filter(user=request.user, tournament=tourney).exists()
            existing_applications[tourney.id] = application_exists

    context = {
        'tourneys': tourneys,
        'is_organizer': is_organizer,
        'is_captain': is_captain,
        'existing_applications': existing_applications,
    }

    return render(request, 'Tournament/listings.html', context)


# Удаление соревнования
def delete_tourney(request, tourney_id):
    tourney_obj = get_object_or_404(TournamentObject, pk=tourney_id)
    if tourney_obj.user == request.user:
        tourney_obj.delete()
        return redirect('listings')
    else:
        raise PermissionDenied("Вы не авторизованы для удаления этого сое.")

# Редактирование матча
def edit_match(request, match_not_unique_id, tourney_id):
    this_tourney = TournamentObject.objects.get(pk=tourney_id)
    team1_id = "-1"
    team2_id = "-1"

    if match_not_unique_id < (this_tourney.num_teams / 2) + 1:
        team1 = "Команда " + str((match_not_unique_id - 1) * 2 + 1)
        team2 = "Команда " + str(match_not_unique_id * 2)
        can_edit = 2
    else:
        team1 = "Будет определено"
        team2 = "Будет определено"
        can_edit = 0

    date = 0
    result_team1 = None
    result_team2 = None
    winner = None

    try:
        this_match = Match.objects.get(tournament=this_tourney, round=match_not_unique_id)
        if this_match.team1 is not None:
            team1 = this_match.team1.name
            team1_id = this_match.team1.id
            can_edit += 1
        if this_match.team2 is not None:
            team2 = this_match.team2.name
            team2_id = this_match.team2.id
            can_edit += 1
        date = this_match.date
        result_team1 = this_match.result_team1
        result_team2 = this_match.result_team2
        winner = this_match.winner
    except Match.DoesNotExist:
        pass

    context = {
        'tourney_id': tourney_id,
        'tourney_creator': this_tourney.user,
        'match_id': match_not_unique_id,
        'team1': team1,
        'team2': team2,
        'team1_id': team1_id,
        'team2_id': team2_id,
        'date': date,
        'result_team1': result_team1,
        'result_team2': result_team2,
        'winner': winner,
        'can_edit': can_edit,
    }
    return render(request, 'Tournament/editmatch.html', context)


# Профиль пользователя
@login_required
def profile(request):
    user = request.user
    is_organizer = user.groups.filter(name='Organizer').exists()
    is_captain = user.groups.filter(name='Captain').exists()

    context = {
        'is_organizer': is_organizer,
        'is_captain': is_captain,
    }
    return render(request, 'User/profile.html', context)

# Редактирование профиля
def edit_profile(request):
    return render(request, 'User/edit_profile.html')


# Обновление данных профиля
@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.email = request.POST['email']
        user.save()
        
        if hasattr(user, 'profile'):
            user.profile.organization_name = request.POST.get('organization_name', user.profile.organization_name)
            user.profile.phone_number = request.POST.get('phone_number', user.profile.phone_number)
            user.profile.save()
        
        messages.success(request, 'Ваш профиль был успешно обновлен!')
        return redirect('profile')
    return render(request, 'User/edit_profile.html')

# Регистрация
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            account_type = form.cleaned_data.get('account_type')
            if account_type == 'organizer':
                group = Group.objects.get(name='Organizer')
                user.groups.add(group)
                return redirect('verification_pending')
            elif account_type == 'captain':
                group = Group.objects.get(name='Captain')
                user.groups.add(group)
                auth_login(request, user)
                return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'User/register.html', {'form': form})

# Создание расписания и жеребьевки
@login_required
def generate_schedule(request, tourney_id):
    if request.method == 'POST':
        tourney = get_object_or_404(TournamentObject, pk=tourney_id)
        if tourney.user != request.user:
            raise PermissionDenied("Вы не авторизованы для редактирования этого соревнования.")
        
        # Удаляем существующие матчи для турнира
        Match.objects.filter(tournament=tourney).delete()
        
        if tourney.tournament_type == TournamentObject.ROUND_ROBIN:
            teams = list(Team.objects.filter(tournament=tourney))
            matches = generate_round_robin_schedule(tourney, teams)
            Match.objects.bulk_create(matches)
        else:
            shuffled_teams = shuffle_teams(tourney)
            rounds = Rounds(tourney, shuffled_teams)
            if tourney.tournament_type == "DE":
                losers_rounds = LosersRounds(tourney)

            for round in rounds.rounds:
                for match in round.matches:
                    match_obj, created = Match.objects.get_or_create(
                        tournament=tourney, 
                        round=match.match_util_round
                    )
                    team1 = Team.objects.filter(name=match.team_1, tournament=tourney).first()
                    team2 = Team.objects.filter(name=match.team_2, tournament=tourney).first()
                    match_obj.team1 = team1
                    match_obj.team2 = team2
                    match_obj.save()
        
        tourney.schedule_generated = True
        tourney.save()
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


# Подача заявки на участие в соревновании
@login_required
def apply_for_tourney(request, tourney_id):
    if not request.user.groups.filter(name='Captain').exists():
        raise PermissionDenied("Только представители команд могут подавать заявки на участие.")

    tourney = get_object_or_404(TournamentObject, pk=tourney_id)
    
    # Проверка срока приема заявок
    current_date = timezone.now().date()
    if not (tourney.application_start_date <= current_date <= tourney.application_end_date):
        messages.error(request, 'Срок подачи заявок истек или еще не начался.')
        return redirect('tourney', tourney_id=tourney_id)
    
    # Проверка на количество заявок
    if Application.objects.filter(tournament=tourney, status=Application.ACCEPTED).count() >= tourney.num_teams:
        return redirect('tourney', tourney_id=tourney_id)

    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        member_first_names = request.POST.getlist('member_first_name')
        member_middle_names = request.POST.getlist('member_middle_name')
        member_last_names = request.POST.getlist('member_last_name')
        member_birthdates = request.POST.getlist('member_birthdate')

        if team_name and member_first_names and member_last_names:
            application = Application.objects.create(
                user=request.user,
                tournament=tourney,
                team_name=team_name,
                status=Application.PENDING
            )
            
            temp_team = Team.objects.create(
                name=team_name,
                user=request.user,
                tournament=tourney
            )

            for first_name, middle_name, last_name, birthdate in zip(member_first_names, member_middle_names, member_last_names, member_birthdates):
                TeamMember.objects.create(
                    team=temp_team,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    birthdate=birthdate
                )
            
            application.team = temp_team
            application.save()

            return redirect('tourney', tourney_id=tourney_id)

    return render(request, 'Tournament/apply.html', {'tourney': tourney})

# Обработка заявки на участие
@login_required
def process_application(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    tourney = application.tournament

    if tourney.user != request.user:
        raise PermissionDenied("Вы не авторизованы для обработки этой заявки.")

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept' and Application.objects.filter(tournament=tourney, status=Application.ACCEPTED).count() < tourney.num_teams:
            application.status = Application.ACCEPTED
            if not application.team:
                team = Team.objects.create(
                    name=application.team_name,
                    user=application.user,
                    tournament=tourney
                )
                application.team = team
            else:
                team = application.team

            # Обновляем членов команды после создания команды
            for member in TeamMember.objects.filter(team=application.team):
                member.team = team
                member.save()
        elif action == 'reject':
            application.status = Application.REJECTED

        application.save()
        return redirect('tourney', tourney_id=tourney.id)

    return render(request, 'Tournament/process_application.html', {'application': application})

#Списки заявок представителей команд
@login_required
def captain_tourney_listings(request):
    user = request.user
    if not user.groups.filter(name='Captain').exists():
        raise PermissionDenied("Только представителей команд могут просматривать свои соревнования.")

    applications = Application.objects.filter(user=user)
    tourneys_with_status = [
        {
            'tourney': app.tournament,
            'status': app.status
        }
        for app in applications
    ]

    paginator = Paginator(tourneys_with_status, 12)  # 12 соревнований на странице
    page = request.GET.get('page')
    paged_tourneys_with_status = paginator.get_page(page)

    context = {
        'tourneys_with_status': paged_tourneys_with_status,
    }

    return render(request, 'Tournament/captain_listings.html', context)

#Загрузка правил
@login_required
def upload_rules(request, tourney_id):
    tourney = get_object_or_404(TournamentObject, pk=tourney_id)
    if tourney.user != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = RulesUploadForm(request.POST, request.FILES, instance=tourney)
        if form.is_valid():
            form.save()
            return redirect('tourney', tourney_id=tourney_id)

    return redirect('tourney', tourney_id=tourney_id)

# Круговой формат
@login_required
def generate_round_robin(request, tourney_id):
    tourney = get_object_or_404(TournamentObject, pk=tourney_id)

    if tourney.user != request.user:
        raise PermissionDenied

    schedule = generate_round_robin_schedule(tourney)

    for round_num, round_matches in enumerate(schedule, start=1):
        for match in round_matches:
            team1, team2 = match
            Match.objects.create(
                tournament=tourney,
                round=round_num,
                team1=team1,
                team2=team2
            )

    return redirect('tourney', tourney_id=tourney_id)

# Проверка верификации
def verification_pending(request):
    return render(request, 'User/verification_pending.html')

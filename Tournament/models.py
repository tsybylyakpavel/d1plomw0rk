# Модели
from django.db import models
from django.contrib.auth.models import User

# Модель для профиля пользователя
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return self.user.username

# Модель для соревнования
class TournamentObject(models.Model):
    SINGLE_ELIMINATION = 'SE'
    DOUBLE_ELIMINATION = 'DE'
    ROUND_ROBIN = 'RR'
    TOURNAMENT_TYPES = [
        (SINGLE_ELIMINATION, 'Олимпийская система'),
        (DOUBLE_ELIMINATION, 'С двойным выбыванием'),
        (ROUND_ROBIN, 'Круговой турнир'),
    ]

    FOOTBALL = 'football'
    TENNIS = 'tennis'
    BOXING = 'boxing'
    BADMINTON = 'badminton'
    VOLLEYBALL = 'volleyball'
    BASKETBALL = 'basketball'
    HANDBALL = 'handball'
    ESPORTS = 'esports'
    HOCKEY = 'hockey'
    RUGBY = 'rugby'

    SPORTS_TYPES = [
        (FOOTBALL, 'Футбол'),
        (TENNIS, 'Теннис'),
        (BOXING, 'Бокс'),
        (BADMINTON, 'Бадминтон'),
        (VOLLEYBALL, 'Волейбол'),
        (BASKETBALL, 'Баскетбол'),
        (HANDBALL, 'Гандбол'),
        (ESPORTS, 'Киберспорт'),
        (HOCKEY, 'Хоккей'),
        (RUGBY, 'Регби'),
    ]

    name = models.CharField(max_length=100, default="Мой турнир")
    description = models.TextField(blank=True)
    num_teams = models.IntegerField(default=16)
    tournament_type = models.CharField(max_length=2, choices=TOURNAMENT_TYPES, default=SINGLE_ELIMINATION)
    sport = models.CharField(max_length=20, choices=SPORTS_TYPES, default=FOOTBALL)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tourney')
    archived = models.BooleanField(default=False)
    winner = models.CharField(max_length=100, default="none")
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_address = models.CharField(max_length=255, null=True, blank=True)
    map_zoom = models.IntegerField(null=True, blank=True)
    map_center_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    map_center_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    schedule_generated = models.BooleanField(default=False)
    rules_document = models.FileField(upload_to='rules/', null=True, blank=True)

    def __str__(self):
        return self.name if self.name else "Пусто"

# Модель для команды
class Team(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='team')
    tournament = models.ForeignKey(TournamentObject, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return self.name if self.name else "Пусто"

# Модель для участника команды
# Модель для участника команды
class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, null=True, blank=True)  # Добавляем отчество
    last_name = models.CharField(max_length=255)
    birthdate = models.DateField(null=True, blank=True)  # Добавляем дату рождения

    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()


# Модель для матча
class Match(models.Model):
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    date = models.DateTimeField(null=True)
    team1 = models.ForeignKey(Team, related_name='matches_as_team1', on_delete=models.CASCADE, null=True)
    team2 = models.ForeignKey(Team, related_name='matches_as_team2', on_delete=models.CASCADE, null=True)
    tournament = models.ForeignKey(TournamentObject, on_delete=models.CASCADE, related_name='matches')
    round = models.IntegerField()
    result_team1 = models.CharField(max_length=10, null=True, blank=True)
    result_team2 = models.CharField(max_length=10, null=True, blank=True)
    winner = models.CharField(max_length=10, choices=[('team1', 'Team 1'), ('team2', 'Team 2'), ('none', 'None')], default='none')

    class Meta:
        unique_together = (('tournament', 'round'),)

    def __str__(self):
        return self.name if self.name else "Пусто"

# Модель для заявки на участие в соревновании
class Application(models.Model):
    PENDING = 'P'
    ACCEPTED = 'A'
    REJECTED = 'R'
    STATUS_CHOICES = [
        (PENDING, 'В ожидании'),
        (ACCEPTED, 'Принято'),
        (REJECTED, 'Отклонено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(TournamentObject, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=255)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    team = models.OneToOneField('Team', null=True, blank=True, on_delete=models.SET_NULL, related_name='application')

    def __str__(self):
        return f"{self.team_name} - {self.get_status_display()}"

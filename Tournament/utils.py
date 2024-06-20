# Логика матчей и соревнований
import math
from django.core.exceptions import ObjectDoesNotExist
from .models import Match,Team
import random

# Класс для создания раундов соревнования
class Rounds:

    def __init__(self, tourney, shuffled_teams=None):
        self.rounds = []
        global_round_counter = 1
        round_count = tourney.num_teams
        while round_count > 1:
            round_count //= 2
            self.rounds.append(Round(tourney, round_count, global_round_counter, shuffled_teams))
            global_round_counter += round_count


# Класс для создания матчей в одном раунде
class Round:
    def __init__(self, tourney, rounds, count, shuffled_teams=None):
        self.matches = []
        for i in range(1, rounds + 1):
            winner = "none"
            result_team1 = None
            result_team2 = None
            match_date = None

            if count < (tourney.num_teams / 2) + 1:
                # Раунд 1
                if shuffled_teams:
                    arg1 = shuffled_teams[(count - 1) * 2].name
                    arg2 = shuffled_teams[count * 2 - 1].name
                else:
                    arg1 = "Команда " + str((count - 1) * 2 + 1)
                    arg2 = "Команда " + str(count * 2)
            else:
                # После первого раунда команды будут определяться победителями предыдущих раундов
                arg1 = "Будет определено"
                arg2 = "Будет определено"

            try:
                this_match = Match.objects.get(tournament=tourney, round=count)
                if this_match.team1 is not None:
                    arg1 = this_match.team1.name
                if this_match.team2 is not None:
                    arg2 = this_match.team2.name
                result_team1 = this_match.result_team1
                result_team2 = this_match.result_team2
                winner = this_match.winner
                match_date = this_match.date
                if count == tourney.num_teams - 1:
                    winner = tourney.winner
            except Match.DoesNotExist:
                pass

            self.matches.append(TeamNames(arg1, arg2, count, winner, result_team1, result_team2, match_date))
            count += 1


# Класс для создания раундов в сетке проигравших
class LosersRounds:

    def __init__(self, tourney):
        self.rounds = []
        global_round_counter = tourney.num_teams
        round_count = tourney.num_teams // 2
        # В сетке проигравших количество игр уменьшается только через раунд.
        # Например, если всего 16 команд, количество игр на раунд в сетке проигравших будет:
        # 8, 8, 4, 4, 2, 2
        second_round = True
        while round_count > 0:
            if second_round:
                round_count //= 2
                second_round = False
            else:
                second_round = True
            self.rounds.append(Round(tourney, round_count, global_round_counter))
            global_round_counter += round_count
        self.grand_final = GrandFinal(tourney, global_round_counter)

# Класс для создания матчей в одном раунде сетки проигравших
class LoserRound:
    def __init__(self, tourney, rounds, count):
        self.matches = []
        for i in range(1, rounds + 1):
            arg1 = "Будет определено"
            arg2 = "Будет определено"
            result_team1 = None
            result_team2 = None
            winner = None

            try:
                this_match = Match.objects.get(tournament=tourney, round=count)
                if this_match.team1 is not None:
                    arg1 = this_match.team1.name
                if this_match.team2 is not None:
                    arg2 = this_match.team2.name
                result_team1 = this_match.result_team1
                result_team2 = this_match.result_team2
                winner = this_match.winner

            except Match.DoesNotExist:
                pass

            self.matches.append(TeamNames(arg1, arg2, count, winner, result_team1, result_team2))
            count += 1


# Класс для создания финального матча соревнования
class GrandFinal:
    def __init__(self, tourney, count):
        self.team_1 = "Будет определено"
        self.team_2 = "Будет определено"
        self.match_util_round = count
        self.result_team1 = None
        self.result_team2 = None
        self.winner = tourney.winner

        try:
            this_match = Match.objects.get(tournament=tourney, round=count)
            if this_match.team1 is not None:
                self.team_1 = this_match.team1.name
            if this_match.team2 is not None:
                self.team_2 = this_match.team2.name
            self.result_team1 = this_match.result_team1
            self.result_team2 = this_match.result_team2
        except Match.DoesNotExist:
            pass


# Класс для хранения информации о матче
class TeamNames:
    def __init__(self, team_name_1, team_name_2, match_util_round, winner, result_team1, result_team2, match_date):
        self.team_1 = team_name_1
        self.team_2 = team_name_2
        self.match_util_round = match_util_round
        self.winner = winner
        self.result_team1 = result_team1
        self.result_team2 = result_team2
        self.date = match_date 


# Функция для обновления следующего раунда для олимпийской системы
def single_tourney_update_future_rounds(match_id, tourney_obj, winner, team1_obj, team2_obj):
    # Если это последний раунд, ничего не делаем
    if match_id < tourney_obj.num_teams - 1 and winner != "none":
        next_round = calculate_next_round(match_id, tourney_obj.num_teams)
        next_match_obj = get_or_create_match(tourney_obj, next_round)

        if next_round == tourney_obj.num_teams - 1:
            # Очищает победителя соревнования, если участники финала изменились
            tourney_obj.winner = "none"
            tourney_obj.save()

        if match_id % 2 == 0:
            next_match_obj.team2 = team2_obj if winner == "team2" else team1_obj
        else:
            next_match_obj.team1 = team2_obj if winner == "team2" else team1_obj
        next_match_obj.save()
        clear_following_round(next_round, tourney_obj)
    elif match_id == tourney_obj.num_teams - 1 and winner != "none":
        # Устанавливает победителя соревноваия
        if winner == "team1":
            tourney_obj.winner = "top"
        else:
            tourney_obj.winner = "bottom"
        tourney_obj.save()


# Обновляет следующий раунд, в котором появляются победитель и проигравший
def double_tourney_update_future_rounds(match_id, tourney_obj, winner, team1_obj, team2_obj):
    # Если это последний раунд, ничего не делаем
    if match_id < get_double_elim_max(tourney_obj.num_teams) and winner != "none":
        # Вычисляет match_id для следующего раунда, в котором будет участвовать победившая команда
        next_round = calculate_double_next_round(match_id, tourney_obj.num_teams)
        next_match_obj = get_or_create_match(tourney_obj, next_round)

        if next_round == get_double_elim_max(tourney_obj.num_teams):
            tourney_obj.winner = "none"
            tourney_obj.save()

        if is_condense_round(match_id, tourney_obj.num_teams):
            # Обычный раунд в сетке победителей
            # Или сжимающий раунд в сетке проигравших
            if (match_id > tourney_obj.num_teams and match_id % 2 == 1) or (
                    match_id <= tourney_obj.num_teams and match_id % 2 == 0):
                # Четные нижние для следующего раунда
                if winner == "team2":
                    next_match_obj.team2 = team2_obj
                else:
                    next_match_obj.team2 = team1_obj
            else:
                # Нечетные верхние для следующего раунда
                if winner == "team2":
                    next_match_obj.team1 = team2_obj
                else:
                    next_match_obj.team1 = team1_obj
        else:
            # Победитель этого матча выиграл в сетке проигравших
            # Следующий раунд сыграет с недавним проигравшим в сетке победителей
            # Всегда будет нижним
            if winner == "team2":
                next_match_obj.team2 = team2_obj
            else:
                next_match_obj.team2 = team1_obj
        next_match_obj.save()

         # Переход в сетку проигравших?
        loser_next_round = calculate_loser_next_round(match_id, tourney_obj.num_teams)

        if loser_next_round != -1:
            loser_match_obj = get_or_create_match(tourney_obj, loser_next_round)

            # Сетка победителей -> Сетка проигравших всегда верхняя, кроме первого раунда
            if match_id <= tourney_obj.num_teams / 2:
                # Первый раунд
                if match_id % 2 == 0:
                    # Четные нижние для Сетка победителей -> Сетка проигравших в первом раунде
                    if winner == "team2":
                        loser_match_obj.team2 = team1_obj
                    else:
                        loser_match_obj.team2 = team2_obj
                else:
                    # Нечетные верхние для Сетка победителей -> Сетка проигравших в первом раунде
                    if winner == "team2":
                        loser_match_obj.team1 = team1_obj
                    else:
                        loser_match_obj.team1 = team2_obj
            else:
                # Другие раунды, кроме первого
                if winner == "team2":
                    loser_match_obj.team1 = team1_obj
                else:
                    loser_match_obj.team1 = team2_obj
            loser_match_obj.save()
            clear_following_round_winning(next_round, tourney_obj)
            clear_following_round_losing(next_round, tourney_obj)
    elif match_id == get_double_elim_max(tourney_obj.num_teams) and winner != "none":
        # Устанавливает победителя соревнования
        if winner == "team1":
            tourney_obj.winner = "top"
        else:
            tourney_obj.winner = "bottom"
        tourney_obj.save()


# Получает или создает объект матча для данного соревнования и раунда
def get_or_create_match(tournament, round):
    try:
        return Match.objects.get(tournament=tournament, round=round)
    except Match.DoesNotExist:
        return Match(tournament=tournament, round=round)


# Возвращает следующий раунд для одиночного выбывания
def calculate_next_round(match_number, total):
    if match_number >= total - 1:
        raise Exception("ERROR: Trying to find next round for final round")
    half_total = total / 2
    current_total = half_total
    while match_number > current_total:
        half_total /= 2
        current_total += half_total
    match_number -= current_total - half_total
    return current_total + (match_number + 1) // 2


# Возвращает следующий раунд для проигравшего в двойном выбывании
# Возвращает -1, если это был их последний раунд
def calculate_double_next_round(match_number, total):
    if match_number < total - 1:
        # Сетка победителей
        return calculate_next_round(match_number, total)
    if match_number == total - 1:
       # Победитель сетки победителей
        return get_double_elim_max(total)
    if match_number >= get_double_elim_max(total):
        raise Exception("ERROR: Trying to find next round for final round")

      # Сетка проигравших
    half_total = total / 4
    current_total = half_total + total
    past_total = total

     # Это делается потому, что количество матчей в раунде повторяется в сетке проигравших
    odd_round = True

    while match_number > current_total:
        if odd_round:
            odd_round = False
        else:
            half_total /= 2
            odd_round = True
        past_total = current_total
        current_total += half_total

    if odd_round:
        # Если в следующем раунде такое же количество раундов, мы можем просто добавить номер матча к количеству матчей в
        # раунде
        return match_number + half_total
    else:
        # Если в следующем раунде половина количества раундов, мы должны добавить позицию этого матча в раунде // 2
        # к номеру матча первого матча в следующем раунде
        return current_total + ((match_number - past_total) // 2)


# Возвращает следующий раунд для проигравшего в двойном выбывании
# Возвращает -1, если это был их последний раунд
def calculate_loser_next_round(match_number, total):
    if match_number >= get_double_elim_max(total):
        raise Exception("ERROR: Trying to find loser's round for final round")
    if match_number >= total:
        # Сетка проигравших
        return -1
    if match_number == total - 1:
        # Особый случай
        return get_double_elim_max(total) - 1

   # Сетка победителей
    # Первый раунд
    half_total = total / 2
    if match_number - 1 < half_total:
        return (match_number - 1) // 2 + total

    # Поздние раунды
    current_total = half_total
    half_total /= 2
    current_total += half_total
    offset = -1
    while match_number > current_total:
        half_total /= 2
        current_total += half_total
        offset += half_total

    return match_number - total / 4 + offset + total


# Очищает последующие раунды в случае, если победитель был изменен и старый победитель прошел дальше в соревновании
def clear_following_round(match_id, tourney_obj):
    if match_id < tourney_obj.num_teams - 1:
        next_round = calculate_next_round(match_id, tourney_obj.num_teams)
        try:
            next_match_obj = Match.objects.get(tournament=tourney_obj, round=next_round)
        except ObjectDoesNotExist:
            # Объект следующего матча не найден, поэтому мы не можем его обновить
            return
        if match_id % 2 == 0:
            # Четные нижние для следующего раунда
            next_match_obj.team2 = None
        else:
            # Нечетные верхние для следующего раунда
            next_match_obj.team1 = None
        # Если мы нашли матч здесь, то может быть еще один будущий матч, в котором они участвуют
        next_match_obj.save()
        clear_following_round(next_round, tourney_obj)
    elif match_id == tourney_obj.num_teams - 1:
        # Очищает победителя соревнования
        tourney_obj.winner = "none"


def clear_following_round_winning(match_id, tourney_obj):
    #
    #
    #
    #
    if match_id < get_double_elim_max(tourney_obj.num_teams):
        next_round = calculate_double_next_round(match_id, tourney_obj.num_teams)
        try:
            next_match_obj = Match.objects.get(tournament=tourney_obj, round=next_round)
        except ObjectDoesNotExist:
            # Объект следующего матча не найден, поэтому мы не можем его обновить
            return
        if match_id == tourney_obj.num_teams - 1:
            next_match_obj.team1 = None
        elif match_id == get_double_elim_max(tourney_obj.num_teams) - 1:
            next_match_obj.team2 = None
        elif is_condense_round(next_round, tourney_obj.num_teams):
            # Обычный раунд в сетке победителей или сжимающий раунд в сетке проигравших
            if (match_id > tourney_obj.num_teams and match_id % 2 == 1) or (
                    match_id <= tourney_obj.num_teams and match_id % 2 == 0):
                # Четные нижние для следующего раунд
                next_match_obj.team2 = None
            else:
                # Нечетные верхние для следующего раунда
                next_match_obj.team1 = None
        else:
            # Победитель этого матча выиграл в сетке проигравших
            # Следующий раунд сыграет с недавним проигравшим в сетке победителей
            # Всегда будет нижним
            next_match_obj.team2 = None
        next_match_obj.save()
        # Если мы нашли матч здесь, то может быть еще один будущий матч, в котором они участвуют
        clear_following_round_winning(next_round, tourney_obj)
        clear_following_round_losing(next_round, tourney_obj)
    elif match_id == get_double_elim_max(tourney_obj.num_teams):
        # Очищает победителя соревнования
        tourney_obj.winner = "none"


# Очищает последующие раунды в случае, если проигравший был изменен и старый проигравший прошел дальше в соревновании
def clear_following_round_losing(match_id, tourney_obj):
    if match_id < get_double_elim_max(tourney_obj.num_teams):
        next_round = calculate_loser_next_round(match_id, tourney_obj.num_teams)
        try:
            loser_match_obj = Match.objects.get(tournament=tourney_obj, round=next_round)
        except ObjectDoesNotExist:
            # Объект следующего матча не найден, поэтому мы не можем его обновить
            return
        # Сетка победителей -> Сетка проигравших всегда верхняя, кроме первого раунда
        if match_id <= tourney_obj.num_teams / 2:
            # Первый раунд
            if match_id % 2 == 0:
                loser_match_obj.team2 = None
            else:
                # Нечетные верхние для следующего раунда
                loser_match_obj.team1 = None
        else:
            # Другие раунды
            loser_match_obj.team1 = None
        loser_match_obj.save()
        # Нужно очистить выигрыш отсюда, чтобы использовать правильный номер последнего раунда
        try:
            next_match_obj = Match.objects.get(tournament=tourney_obj, round=next_round)
            if match_id == tourney_obj.num_teams - 1:
                next_match_obj.team1 = None
            elif match_id == get_double_elim_max(tourney_obj.num_teams) - 1:
                next_match_obj.team2 = None
            elif not is_condense_round(next_round, tourney_obj.num_teams):
                # Обычный раунд в сетке победителей
                # Или сжимающий раунд в сетке проигравших
                if (match_id > tourney_obj.num_teams and match_id % 2 == 1) or (
                        match_id <= tourney_obj.num_teams and match_id % 2 == 0):
                    # Четные нижние для следующего раунда
                    next_match_obj.team2 = None
                else:
                    # Нечетные верхние для следующего раунда
                    next_match_obj.team1 = None
            else:
                 # Победитель этого матча выиграл в сетке проигравших
                # Следующий раунд сыграет с недавним проигравшим в сетке победителей
                # Всегда будет нижним
                next_match_obj.team2 = None
            next_match_obj.save()
        except ObjectDoesNotExist:
            pass
        # Если мы нашли матч здесь, то может быть еще один будущий матч, в котором они участвуют
        clear_following_round_losing(next_round, tourney_obj)
        clear_following_round_winning(next_round, tourney_obj)


def get_double_elim_max(size):
    n = math.log2(size)
    return double_elim_max_sequence(n) + 1


def double_elim_max_sequence(n):
    if n == 1:
        return 2
    elif n == 2:
        return 5
    else:
        return 2*double_elim_max_sequence(n-1) + 3


def is_condense_round(match_number, total):
    if match_number <= total:
        # Сетка победителей
        return True
    if match_number >= get_double_elim_max(total):
        raise Exception("ERROR: Invalid match number. The input was too high.")
    # Сетка проигравших
    quarter_total = total / 4
    current_total = quarter_total + total
    even_round = False
    while match_number >= current_total:
        if not even_round:
            even_round = True
        else:
            quarter_total /= 2
            even_round = False
        current_total += quarter_total

    return even_round

def shuffle_teams(tourney):
    teams = list(Team.objects.filter(tournament=tourney))
    random.shuffle(teams)
    return teams

def generate_round_robin_schedule(tourney, teams):
    num_teams = len(teams)
    if num_teams % 2:
        teams.append(None)  # Добавить фиктивную команду, если количество команд нечетное

    schedule = []
    num_days = num_teams - 1
    half_size = num_teams // 2

    for day in range(num_days):
        matches = []
        for i in range(half_size):
            team1 = teams[i]
            team2 = teams[num_teams - 1 - i]
            if team1 and team2:
                match = Match(
                    tournament=tourney,
                    team1=team1,
                    team2=team2,
                    round=day + 1
                )
                matches.append(match)
        teams.insert(1, teams.pop())
        schedule.extend(matches)  # Используйте extend вместо append для добавления списка

    return schedule

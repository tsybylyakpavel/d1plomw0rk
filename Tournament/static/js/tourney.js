document.addEventListener("DOMContentLoaded", function() {
    // Обработчик клика по строкам матчей
    document.querySelectorAll(".match-row").forEach(function(row) {
        row.addEventListener("click", function() {
            matchInfo({ currentTarget: row });
        });
    });

    // Обработчик клика по кнопке генерации расписания
    const generateScheduleBtn = document.getElementById('generate-schedule-btn');
    if (generateScheduleBtn) {
        generateScheduleBtn.addEventListener('click', generateSchedule);
    }

    // Инициализация кликов по кнопкам матчей
    let match_buttons = document.querySelectorAll('.matchup_click');
    for (let match_button of match_buttons) {
        match_button.addEventListener('click', matchInfo);
    }

    // Показ нужного таба, если есть хэш в URL
    if (window.location.hash) {
        let hash = window.location.hash;
        let tabLink = document.querySelector('.nav-tabs a[href="' + hash + '"]');
        if (tabLink) {
            new bootstrap.Tab(tabLink).show();
        }
    }
});

function generateSchedule() {
    fetch(generateScheduleUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ generate: true })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('schedule-content').innerHTML = '<p class="text-center">Расписание сгенерировано</p>';
            setTimeout(function() {
                location.reload();
            }, 2000); // Перезагрузить через 2 секунды
        } else {
            alert('Произошла ошибка при генерации расписания');
        }
    });
}

function matchInfo(event) {
    // Создаем модальное окно Bootstrap с кастомным классом
    var modal = $('<div class="modal fade custom-modal" tabindex="-1" role="dialog">');
    var modalDialog = $('<div class="modal-dialog" role="document">');
    var modalContent = $('<div class="modal-content">');
    modal.append(modalDialog);
    modalDialog.append(modalContent);

    const matchId = parseInt(event.currentTarget.getAttribute('data-matchid'));
    const tourneyId = parseInt(event.currentTarget.getAttribute('data-tourney_id'));

    // Проверьте, что matchId и tourneyId корректно извлечены
    if (isNaN(matchId) || isNaN(tourneyId)) {
        console.error('Invalid matchId or tourneyId:', matchId, tourneyId);
        return;
    }

    // Загружаем форму редактирования внутрь модального окна
    $.ajax({
        url: '/tourney/edit_match/' + matchId + '/' + tourneyId,
        success: function(data) {
            modalContent.html(data);
            // Показываем модальное окно
            modal.modal('show');
        }
    });

    // Отправляем форму и закрываем модальное окно, когда процесс завершен
    modalContent.on('submit', 'form', function(e) {
        e.preventDefault();
        $.ajax({
            url: $(this).attr('action'),
            method: $(this).attr('method'),
            data: $(this).serialize(),
            success: function() {
                modal.modal('hide');
                // Добавляем хеш к URL перед перезагрузкой
                window.location.hash = 'games';
                location.reload(); // Перезагружаем страницу, чтобы показать обновленную информацию
            }
        });
    });
}

$(document).ready(function() {
    let match_buttons = document.querySelectorAll('.matchup_click');

    for (let match_button of match_buttons) {
        match_button.addEventListener('click', matchInfo);
    }

    // Автоматическое переключение на вкладку, если в URL есть хеш
    if (window.location.hash) {
        let hash = window.location.hash;
        $('.nav-tabs a[href="' + hash + '"]').tab('show');
    }
});
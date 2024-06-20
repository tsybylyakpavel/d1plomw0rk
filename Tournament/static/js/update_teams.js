function updateTeams() {
    const teamCount = document.getElementById('teams').value;
    const teamNamesDiv = document.getElementById('team-names');
    teamNamesDiv.innerHTML = '';  // Очистка текущих полей ввода

    for (let i = 0; i < teamCount; i++) {
        const input = document.createElement('input');
        input.type = 'text';
        input.name = 'team_' + (i + 1);
        input.className = 'form-control my-2';
        input.placeholder = 'Название команды ' + (i + 1);
        input.required = true;
        teamNamesDiv.appendChild(input);
    }
}

// Вызов функции при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    updateTeams();
});

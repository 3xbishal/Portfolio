document.addEventListener('DOMContentLoaded', function () {
    var treasureMap = document.getElementById('treasureMap'); var treasureStatus = document.getElementById('treasureStatus'); var treasureIndex; var searches;
    function newTreasureMap() { treasureIndex = Math.floor(Math.random() * 9); searches = 3; treasureStatus.textContent = 'Three searches remain.'; treasureMap.innerHTML = ''; for (var i = 0; i < 9; i++) { var tile = document.createElement('button'); tile.type = 'button'; tile.dataset.tile = i; tile.setAttribute('aria-label', 'Search location ' + (i + 1)); tile.innerHTML = '<i class="fas fa-question"></i>'; tile.addEventListener('click', searchTile); treasureMap.appendChild(tile); } }
    function searchTile(event) { var tile = event.currentTarget; if (tile.disabled || searches <= 0) return; var index = Number(tile.dataset.tile); tile.disabled = true; if (index === treasureIndex) { tile.classList.add('found'); tile.innerHTML = '<i class="fas fa-gem"></i>'; searches = 0; treasureStatus.textContent = 'Treasure found! The expedition is a success.'; return; } tile.classList.add('empty'); tile.innerHTML = '<i class="fas fa-xmark"></i>'; searches--; if (searches === 0) { treasureMap.children[treasureIndex].classList.add('found'); treasureMap.children[treasureIndex].innerHTML = '<i class="fas fa-gem"></i>'; Array.from(treasureMap.children).forEach(function (item) { item.disabled = true; }); treasureStatus.textContent = 'The treasure stayed hidden. New map?'; } else { treasureStatus.textContent = searches + ' search' + (searches === 1 ? '' : 'es') + ' remaining.'; } }
    document.getElementById('treasureReset').addEventListener('click', newTreasureMap); newTreasureMap();

    var runner = document.getElementById('runnerPlayer'); var obstacle = document.getElementById('runnerObstacle'); var runnerStart = document.getElementById('runnerStart'); var runnerStatus = document.getElementById('runnerStatus'); var running = false; var jumping = false; var score = 0; var runnerTimer; var runnerBest = Number(localStorage.getItem('gaming_zone_runner_best')) || 0;
    document.getElementById('runnerBest').textContent = runnerBest + ' m';
    function stopRunner(message) { running = false; clearInterval(runnerTimer); obstacle.classList.remove('running'); runnerStart.textContent = 'Start expedition'; runnerStatus.textContent = message; if (score > runnerBest) { runnerBest = score; localStorage.setItem('gaming_zone_runner_best', score); document.getElementById('runnerBest').textContent = score + ' m'; } }
    function jump() { if (!running || jumping) return; jumping = true; runner.classList.add('jump'); setTimeout(function () { runner.classList.remove('jump'); jumping = false; }, 440); }
    function startRunner() { if (running) { jump(); return; } running = true; score = 0; document.getElementById('runnerScore').textContent = '0 m'; runnerStart.textContent = 'Jump'; runnerStatus.textContent = 'Run! Press Space to jump.'; obstacle.classList.add('running'); runnerTimer = setInterval(function () { score += 10; document.getElementById('runnerScore').textContent = score + ' m'; if (!jumping && score > 20 && score % 70 === 0) stopRunner('Expedition over at ' + score + ' m. Try again.'); }, 350); }
    runnerStart.addEventListener('click', function () { if (running) jump(); else startRunner(); });
    document.addEventListener('keydown', function (event) { if (event.code === 'Space') { event.preventDefault(); if (running) jump(); else startRunner(); } });

    var board = Array(9).fill(''); var active = true; var aiThinking = false; var cells = document.querySelectorAll('#ticTacToeBoard button'); var status = document.getElementById('tttStatus');
    var wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
    function winner(mark) { return wins.some(function (line) { return line.every(function (index) { return board[index] === mark; }); }); }
    function finish(message) { active = false; status.textContent = message; }
    function aiTurn() {
        aiThinking = false;
        var choices = board.map(function (value, index) { return value ? null : index; }).filter(function (value) { return value !== null; });
        if (!choices.length) { finish('Draw. Perfectly matched!'); return; }
        var index = choices[Math.floor(Math.random() * choices.length)]; board[index] = 'O'; cells[index].textContent = 'O'; cells[index].classList.add('o-mark');
        if (winner('O')) finish('The challenger takes this round.'); else if (!board.includes('')) finish('Draw. Perfectly matched!'); else status.textContent = 'Your move, commander.';
    }
    cells.forEach(function (cell) { cell.addEventListener('click', function () { var index = Number(cell.dataset.cell); if (!active || aiThinking || board[index]) return; board[index] = 'X'; cell.textContent = 'X'; if (winner('X')) { finish('Victory! You own the grid.'); return; } if (!board.includes('')) { finish('Draw. Perfectly matched!'); return; } aiThinking = true; status.textContent = 'Challenger thinking...'; setTimeout(aiTurn, 350); }); });
    document.getElementById('tttReset').addEventListener('click', function () { board = Array(9).fill(''); active = true; aiThinking = false; status.textContent = 'Your move, commander.'; cells.forEach(function (cell) { cell.textContent = ''; cell.classList.remove('o-mark'); }); });
});

document.addEventListener('DOMContentLoaded', function () {
    // Snake Game
    var snakeCanvas = document.getElementById('snakeGame'); var snakeCtx = snakeCanvas.getContext('2d');
    var snakeScoreEl = document.getElementById('snakeScore'); var snakeBestEl = document.getElementById('snakeBest');
    var snakeStartBtn = document.getElementById('snakeStart'); var snakeStatusEl = document.getElementById('snakeStatus');
    var snakeGridSize = 14; var snakeCellSize = snakeCanvas.width / snakeGridSize;
    var snake = []; var snakeFood = { x: 0, y: 0 }; var snakeDir = { x: 1, y: 0 }; var snakeNextDir = { x: 1, y: 0 };
    var snakeScore = 0; var snakeBest = Number(localStorage.getItem('gaming_zone_snake_best')) || 0;
    var snakeRunning = false; var snakeLoop = null; var snakeSpeed = 120;
    snakeBestEl.textContent = snakeBest;

    function initSnake() {
        snake = [{ x: 7, y: 7 }, { x: 6, y: 7 }, { x: 5, y: 7 }];
        snakeDir = { x: 1, y: 0 }; snakeNextDir = { x: 1, y: 0 };
        snakeScore = 0; snakeScoreEl.textContent = '0';
        placeSnakeFood(); drawSnake();
    }

    function placeSnakeFood() {
        var valid = false;
        while (!valid) {
            snakeFood.x = Math.floor(Math.random() * snakeGridSize);
            snakeFood.y = Math.floor(Math.random() * snakeGridSize);
            valid = !snake.some(function (s) { return s.x === snakeFood.x && s.y === snakeFood.y; });
        }
    }

    function drawSnake() {
        snakeCtx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--bg').trim() || '#0d1117';
        snakeCtx.fillRect(0, 0, snakeCanvas.width, snakeCanvas.height);
        // Draw food
        snakeCtx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#ff6b35';
        snakeCtx.beginPath();
        snakeCtx.arc(snakeFood.x * snakeCellSize + snakeCellSize / 2, snakeFood.y * snakeCellSize + snakeCellSize / 2, snakeCellSize / 2 - 1, 0, Math.PI * 2);
        snakeCtx.fill();
        // Draw snake
        snake.forEach(function (segment, i) {
            var alpha = 1 - (i / snake.length) * 0.4;
            snakeCtx.fillStyle = i === 0 ? (getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#ff6b35') : 'rgba(255, 107, 53, ' + alpha + ')';
            snakeCtx.fillRect(segment.x * snakeCellSize + 1, segment.y * snakeCellSize + 1, snakeCellSize - 2, snakeCellSize - 2);
        });
    }

    function updateSnake() {
        snakeDir = snakeNextDir;
        var head = { x: snake[0].x + snakeDir.x, y: snake[0].y + snakeDir.y };
        // Check wall collision
        if (head.x < 0 || head.x >= snakeGridSize || head.y < 0 || head.y >= snakeGridSize) { stopSnake('Game Over! You hit the wall.'); return; }
        // Check self collision
        if (snake.some(function (s) { return s.x === head.x && s.y === head.y; })) { stopSnake('Game Over! You bit yourself.'); return; }
        snake.unshift(head);
        // Check food
        if (head.x === snakeFood.x && head.y === snakeFood.y) {
            snakeScore += 10; snakeScoreEl.textContent = snakeScore;
            if (snakeScore > snakeBest) { snakeBest = snakeScore; localStorage.setItem('gaming_zone_snake_best', snakeBest); snakeBestEl.textContent = snakeBest; }
            placeSnakeFood();
            // Speed up slightly
            if (snakeSpeed > 60) { snakeSpeed -= 2; clearInterval(snakeLoop); snakeLoop = setInterval(updateSnake, snakeSpeed); }
        } else { snake.pop(); }
        drawSnake();
    }

    function startSnake() {
        if (snakeRunning) return;
        snakeRunning = true; snakeSpeed = 120;
        initSnake();
        snakeStartBtn.textContent = 'Playing...';
        snakeStatusEl.textContent = 'Use arrow keys to move!';
        snakeLoop = setInterval(updateSnake, snakeSpeed);
    }

    function stopSnake(message) {
        snakeRunning = false; clearInterval(snakeLoop);
        snakeStartBtn.textContent = 'Start Game';
        snakeStatusEl.textContent = message + ' Score: ' + snakeScore;
    }

    snakeStartBtn.addEventListener('click', function () { if (!snakeRunning) startSnake(); });
    document.addEventListener('keydown', function (e) {
        if (e.code === 'Space' && !snakeRunning && document.activeElement !== snakeStartBtn) {
            // Only start snake if breakout isn't active either
        }
        if (!snakeRunning) return;
        switch (e.code) {
            case 'ArrowUp': if (snakeDir.y !== 1) snakeNextDir = { x: 0, y: -1 }; e.preventDefault(); break;
            case 'ArrowDown': if (snakeDir.y !== -1) snakeNextDir = { x: 0, y: 1 }; e.preventDefault(); break;
            case 'ArrowLeft': if (snakeDir.x !== 1) snakeNextDir = { x: -1, y: 0 }; e.preventDefault(); break;
            case 'ArrowRight': if (snakeDir.x !== -1) snakeNextDir = { x: 1, y: 0 }; e.preventDefault(); break;
        }
    });
    initSnake();

    // Breakout Game
    var bkCanvas = document.getElementById('breakoutGame'); var bkCtx = bkCanvas.getContext('2d');
    var bkScoreEl = document.getElementById('breakoutScore'); var bkLivesEl = document.getElementById('breakoutLives');
    var bkStartBtn = document.getElementById('breakoutStart'); var bkStatusEl = document.getElementById('breakoutStatus');
    var bkRunning = false; var bkLoop = null; var bkScore = 0; var bkLives = 3;
    var bkPaddle = { x: 100, y: 260, w: 70, h: 8 }; var bkBall = { x: 140, y: 230, dx: 3, dy: -3, r: 5 };
    var bkBricks = []; var bkRows = 4; var bkCols = 7; var bkBrickW = 34; var bkBrickH = 12; var bkBrickPad = 4; var bkBrickOffsetTop = 20; var bkBrickOffsetLeft = 12;
    var bkMouseX = null; var bkKeyLeft = false; var bkKeyRight = false;

    function initBreakout() {
        bkScore = 0; bkLives = 3; bkScoreEl.textContent = '0'; bkLivesEl.textContent = '3';
        bkPaddle.x = (bkCanvas.width - bkPaddle.w) / 2;
        bkBall.x = bkCanvas.width / 2; bkBall.y = bkPaddle.y - 10; bkBall.dx = 3; bkBall.dy = -3;
        bkBricks = [];
        for (var r = 0; r < bkRows; r++) {
            for (var c = 0; c < bkCols; c++) {
                bkBricks.push({ x: bkBrickOffsetLeft + c * (bkBrickW + bkBrickPad), y: bkBrickOffsetTop + r * (bkBrickH + bkBrickPad), w: bkBrickW, h: bkBrickH, alive: true, row: r });
            }
        }
        drawBreakout();
    }

    function drawBreakout() {
        var bgColor = getComputedStyle(document.documentElement).getPropertyValue('--bg').trim() || '#0d1117';
        var accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#ff6b35';
        bkCtx.fillStyle = bgColor; bkCtx.fillRect(0, 0, bkCanvas.width, bkCanvas.height);
        // Draw bricks
        var rowColors = ['#ff6b35', '#f7931e', '#ffc857', '#4ecdc4'];
        bkBricks.forEach(function (b) {
            if (!b.alive) return;
            bkCtx.fillStyle = rowColors[b.row] || accentColor;
            bkCtx.fillRect(b.x, b.y, b.w, b.h);
        });
        // Draw paddle
        bkCtx.fillStyle = accentColor;
        bkCtx.fillRect(bkPaddle.x, bkPaddle.y, bkPaddle.w, bkPaddle.h);
        // Draw ball
        bkCtx.beginPath();
        bkCtx.arc(bkBall.x, bkBall.y, bkBall.r, 0, Math.PI * 2);
        bkCtx.fillStyle = accentColor; bkCtx.fill();
    }

    function updateBreakout() {
        // Move paddle
        if (bkMouseX !== null) { bkPaddle.x = bkMouseX - bkPaddle.w / 2; }
        if (bkKeyLeft) bkPaddle.x -= 6;
        if (bkKeyRight) bkPaddle.x += 6;
        bkPaddle.x = Math.max(0, Math.min(bkCanvas.width - bkPaddle.w, bkPaddle.x));
        // Move ball
        bkBall.x += bkBall.dx; bkBall.y += bkBall.dy;
        // Wall collision
        if (bkBall.x + bkBall.r > bkCanvas.width || bkBall.x - bkBall.r < 0) bkBall.dx = -bkBall.dx;
        if (bkBall.y - bkBall.r < 0) bkBall.dy = -bkBall.dy;
        // Paddle collision
        if (bkBall.y + bkBall.r >= bkPaddle.y && bkBall.y + bkBall.r <= bkPaddle.y + bkPaddle.h && bkBall.x >= bkPaddle.x && bkBall.x <= bkPaddle.x + bkPaddle.w) {
            bkBall.dy = -Math.abs(bkBall.dy);
            var hitPos = (bkBall.x - bkPaddle.x) / bkPaddle.w - 0.5;
            bkBall.dx = hitPos * 6;
        }
        // Bottom - lose life
        if (bkBall.y - bkBall.r > bkCanvas.height) {
            bkLives--; bkLivesEl.textContent = bkLives;
            if (bkLives <= 0) { stopBreakout('Game Over! Final score: ' + bkScore); return; }
            bkBall.x = bkCanvas.width / 2; bkBall.y = bkPaddle.y - 10; bkBall.dx = 3; bkBall.dy = -3;
            bkStatusEl.textContent = 'Life lost! ' + bkLives + ' lives remaining.';
        }
        // Brick collision
        for (var i = 0; i < bkBricks.length; i++) {
            var b = bkBricks[i];
            if (!b.alive) continue;
            if (bkBall.x + bkBall.r > b.x && bkBall.x - bkBall.r < b.x + b.w && bkBall.y + bkBall.r > b.y && bkBall.y - bkBall.r < b.y + b.h) {
                bkBall.dy = -bkBall.dy; b.alive = false;
                bkScore += 10; bkScoreEl.textContent = bkScore;
                if (bkBricks.every(function (br) { return !br.alive; })) { stopBreakout('You win! All bricks cleared! Score: ' + bkScore); return; }
            }
        }
        drawBreakout();
    }

    function startBreakout() {
        if (bkRunning) return;
        bkRunning = true; initBreakout();
        bkStartBtn.textContent = 'Playing...';
        bkStatusEl.textContent = 'Move mouse or use arrow keys!';
        bkLoop = setInterval(updateBreakout, 1000 / 50);
    }

    function stopBreakout(message) {
        bkRunning = false; clearInterval(bkLoop);
        bkStartBtn.textContent = 'Start Game';
        bkStatusEl.textContent = message;
    }

    bkStartBtn.addEventListener('click', function () { if (!bkRunning) startBreakout(); });
    bkCanvas.addEventListener('mousemove', function (e) {
        var rect = bkCanvas.getBoundingClientRect(); var scaleX = bkCanvas.width / rect.width;
        bkMouseX = (e.clientX - rect.left) * scaleX;
    });
    bkCanvas.addEventListener('mouseleave', function () { bkMouseX = null; });
    bkCanvas.addEventListener('touchmove', function (e) {
        e.preventDefault(); var rect = bkCanvas.getBoundingClientRect(); var scaleX = bkCanvas.width / rect.width;
        bkMouseX = (e.touches[0].clientX - rect.left) * scaleX;
    }, { passive: false });
    document.addEventListener('keydown', function (e) {
        if (e.code === 'ArrowLeft') { bkKeyLeft = true; if (bkRunning) e.preventDefault(); }
        if (e.code === 'ArrowRight') { bkKeyRight = true; if (bkRunning) e.preventDefault(); }
    });
    document.addEventListener('keyup', function (e) {
        if (e.code === 'ArrowLeft') bkKeyLeft = false;
        if (e.code === 'ArrowRight') bkKeyRight = false;
    });
    initBreakout();

    // Tic Tac Toe (Grid Clash)
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
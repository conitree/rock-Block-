import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Rock Block",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 Rock Block")
st.caption("← → 키 또는 아래 버튼으로 패들을 움직이세요.")

game = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
body {
    margin: 0;
    background: #111;
    color: white;
    font-family: Arial, sans-serif;
    text-align: center;
}

canvas {
    background: #181818;
    border: 2px solid #555;
    border-radius: 8px;
    max-width: 100%;
}

.info {
    font-size: 18px;
    margin-bottom: 8px;
}

.controls {
    margin-top: 10px;
}

.controls button {
    width: 100px;
    height: 45px;
    margin: 5px;
    font-size: 20px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
}

#restart {
    width: 150px;
    font-size: 16px;
}
</style>
</head>

<body>

<div class="info">
    점수: <span id="score">0</span>
    &nbsp;&nbsp;
    목숨: <span id="lives">3</span>
</div>

<canvas id="gameCanvas" width="640" height="480"></canvas>

<div class="controls">
    <button id="left">◀</button>
    <button id="right">▶</button>
</div>

<br>

<button id="restart">다시 시작</button>

<script>

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const scoreElement = document.getElementById("score");
const livesElement = document.getElementById("lives");

const WIDTH = canvas.width;
const HEIGHT = canvas.height;

let score = 0;
let lives = 3;
let running = true;

let left = false;
let right = false;

const ball = {
    x: WIDTH / 2,
    y: HEIGHT - 60,
    radius: 8,
    dx: 4,
    dy: -4
};

const paddle = {
    width: 100,
    height: 12,
    x: WIDTH / 2 - 50,
    speed: 7
};

const rows = 5;
const columns = 8;

const brickWidth = 68;
const brickHeight = 22;
const brickPadding = 8;
const brickTop = 40;
const brickLeft = 20;

let bricks = [];

function createBricks() {

    bricks = [];

    for (let r = 0; r < rows; r++) {

        bricks[r] = [];

        for (let c = 0; c < columns; c++) {

            bricks[r][c] = {
                x: 0,
                y: 0,
                alive: true
            };

        }
    }
}

function drawBall() {

    ctx.beginPath();

    ctx.arc(
        ball.x,
        ball.y,
        ball.radius,
        0,
        Math.PI * 2
    );

    ctx.fillStyle = "white";
    ctx.fill();

    ctx.closePath();
}

function drawPaddle() {

    ctx.fillStyle = "#4CAF50";

    ctx.fillRect(
        paddle.x,
        HEIGHT - 30,
        paddle.width,
        paddle.height
    );
}

function drawBricks() {

    for (let r = 0; r < rows; r++) {

        for (let c = 0; c < columns; c++) {

            const brick = bricks[r][c];

            if (!brick.alive) {
                continue;
            }

            brick.x =
                brickLeft +
                c * (brickWidth + brickPadding);

            brick.y =
                brickTop +
                r * (brickHeight + brickPadding);

            ctx.fillStyle = "#e74c3c";

            ctx.fillRect(
                brick.x,
                brick.y,
                brickWidth,
                brickHeight
            );
        }
    }
}

function resetBall() {

    ball.x = WIDTH / 2;
    ball.y = HEIGHT - 60;

    ball.dx =
        Math.random() > 0.5
        ? 4
        : -4;

    ball.dy = -4;

    paddle.x =
        WIDTH / 2 - paddle.width / 2;
}

function update() {

    ball.x += ball.dx;
    ball.y += ball.dy;

    // 좌우 벽
    if (
        ball.x + ball.radius >= WIDTH ||
        ball.x - ball.radius <= 0
    ) {
        ball.dx *= -1;
    }

    // 위쪽 벽
    if (ball.y - ball.radius <= 0) {
        ball.dy *= -1;
    }

    // 패들 이동
    if (left) {
        paddle.x -= paddle.speed;
    }

    if (right) {
        paddle.x += paddle.speed;
    }

    // 패들 화면 밖 방지
    if (paddle.x < 0) {
        paddle.x = 0;
    }

    if (paddle.x + paddle.width > WIDTH) {
        paddle.x = WIDTH - paddle.width;
    }

    // 패들 충돌
    const paddleY = HEIGHT - 30;

    if (
        ball.x >= paddle.x &&
        ball.x <= paddle.x + paddle.width &&
        ball.y + ball.radius >= paddleY &&
        ball.y - ball.radius <= paddleY + paddle.height &&
        ball.dy > 0
    ) {

        ball.dy = -Math.abs(ball.dy);

        const position =
            (ball.x - paddle.x) / paddle.width;

        ball.dx =
            (position - 0.5) * 10;
    }

    // 벽돌 충돌
    for (let r = 0; r < rows; r++) {

        for (let c = 0; c < columns; c++) {

            const brick = bricks[r][c];

            if (!brick.alive) {
                continue;
            }

            if (
                ball.x > brick.x &&
                ball.x < brick.x + brickWidth &&
                ball.y > brick.y &&
                ball.y < brick.y + brickHeight
            ) {

                brick.alive = false;

                ball.dy *= -1;

                score += 10;

                scoreElement.textContent = score;

                if (score >= rows * columns * 10) {
                    running = false;
                }
            }
        }
    }

    // 바닥
    if (ball.y - ball.radius > HEIGHT) {

        lives--;

        livesElement.textContent = lives;

        if (lives <= 0) {

            running = false;

        } else {

            resetBall();
        }
    }
}

function drawGame() {

    ctx.clearRect(
        0,
        0,
        WIDTH,
        HEIGHT
    );

    drawBricks();
    drawBall();
    drawPaddle();

    if (!running) {

        ctx.fillStyle = "rgba(0,0,0,0.7)";

        ctx.fillRect(
            0,
            0,
            WIDTH,
            HEIGHT
        );

        ctx.fillStyle = "white";
        ctx.textAlign = "center";
        ctx.font = "32px Arial";

        if (score >= rows * columns * 10) {

            ctx.fillText(
                "YOU WIN!",
                WIDTH / 2,
                HEIGHT / 2
            );

        } else {

            ctx.fillText(
                "GAME OVER",
                WIDTH / 2,
                HEIGHT / 2
            );
        }

        return;
    }

    update();

    requestAnimationFrame(drawGame);
}

// 키보드
document.addEventListener("keydown", function(event) {

    if (event.key === "ArrowLeft") {
        left = true;
    }

    if (event.key === "ArrowRight") {
        right = true;
    }

});

document.addEventListener("keyup", function(event) {

    if (event.key === "ArrowLeft") {
        left = false;
    }

    if (event.key === "ArrowRight") {
        right = false;
    }

});

// 모바일/화면 버튼
const leftButton = document.getElementById("left");
const rightButton = document.getElementById("right");

leftButton.addEventListener("mousedown", function() {
    left = true;
});

leftButton.addEventListener("mouseup", function() {
    left = false;
});

leftButton.addEventListener("touchstart", function(event) {
    event.preventDefault();
    left = true;
});

leftButton.addEventListener("touchend", function(event) {
    event.preventDefault();
    left = false;
});

rightButton.addEventListener("mousedown", function() {
    right = true;
});

rightButton.addEventListener("mouseup", function() {
    right = false;
});

rightButton.addEventListener("touchstart", function(event) {
    event.preventDefault();
    right = true;
});

rightButton.addEventListener("touchend", function(event) {
    event.preventDefault();
    right = false;
});

// 다시 시작
document.getElementById("restart").addEventListener(
    "click",
    function() {

        score = 0;
        lives = 3;
        running = true;

        scoreElement.textContent = score;
        livesElement.textContent = lives;

        createBricks();
        resetBall();

        requestAnimationFrame(drawGame);
    }
);

createBricks();
drawGame();

</script>

</body>
</html>
"""

components.html(
    game,
    height=620,
    scrolling=False
)

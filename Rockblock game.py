import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Brick Breaker",
    page_icon="🧱",
    layout="centered",
)

st.title("🧱 Brick Breaker")
st.caption("키보드 ← → 로 패들을 움직이세요.")

game_html = r"""
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
        overflow: hidden;
    }

    canvas {
        display: block;
        margin: 10px auto;
        background: #181818;
        border: 2px solid #444;
        border-radius: 8px;
        max-width: 100%;
    }

    #info {
        font-size: 16px;
        margin: 5px;
    }

    button {
        padding: 8px 18px;
        border: 0;
        border-radius: 6px;
        cursor: pointer;
        font-size: 15px;
    }
</style>
</head>

<body>

<div id="info">
    점수: <span id="score">0</span>
    &nbsp;&nbsp;
    목숨: <span id="lives">3</span>
</div>

<canvas id="game" width="640" height="480"></canvas>

<button onclick="restartGame()">다시 시작</button>

<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const scoreEl = document.getElementById("score");
const livesEl = document.getElementById("lives");

const WIDTH = canvas.width;
const HEIGHT = canvas.height;

// 공
let ball = {
    x: WIDTH / 2,
    y: HEIGHT - 50,
    radius: 8,
    dx: 4,
    dy: -4
};

// 패들
const paddle = {
    width: 100,
    height: 12,
    x: WIDTH / 2 - 50,
    speed: 8
};

// 벽돌
const brick = {
    rowCount: 5,
    columnCount: 8,
    width: 68,
    height: 22,
    padding: 8,
    offsetTop: 40,
    offsetLeft: 20
};

let bricks = [];
let score = 0;
let lives = 3;

let leftPressed = false;
let rightPressed = false;
let gameRunning = true;

function createBricks() {
    bricks = [];

    for (let r = 0; r < brick.rowCount; r++) {
        bricks[r] = [];

        for (let c = 0; c < brick.columnCount; c++) {
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
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fillStyle = "#fff";
    ctx.fill();
    ctx.closePath();
}

function drawPaddle() {
    ctx.fillStyle = "#4CAF50";

    ctx.fillRect(
        paddle.x,
        HEIGHT - paddle.height - 10,
        paddle.width,
        paddle.height
    );
}

function drawBricks() {
    for (let r = 0; r < brick.rowCount; r++) {
        for (let c = 0; c < brick.columnCount; c++) {
            if (!bricks[r][c].alive) continue;

            const x =
                c * (brick.width + brick.padding) +
                brick.offsetLeft;

            const y =
                r * (brick.height + brick.padding) +
                brick.offsetTop;

            bricks[r][c].x = x;
            bricks[r][c].y = y;

            ctx.fillStyle = "#e74c3c";
            ctx.fillRect(
                x,
                y,
                brick.width,
                brick.height
            );
        }
    }
}

function draw() {
    ctx.clearRect(0, 0, WIDTH, HEIGHT);

    drawBricks();
    drawBall();
    drawPaddle();

    if (!gameRunning) {
        ctx.fillStyle = "rgba(0,0,0,0.65)";
        ctx.fillRect(0, 0, WIDTH, HEIGHT);

        ctx.fillStyle = "#fff";
        ctx.font = "32px Arial";
        ctx.textAlign = "center";

        ctx.fillText(
            score >= brick.rowCount * brick.columnCount
                ? "YOU WIN!"
                : "GAME OVER",
            WIDTH / 2,
            HEIGHT / 2
        );

        ctx.font = "18px Arial";
        ctx.fillText(
            "다시 시작 버튼을 눌러주세요",
            WIDTH / 2,
            HEIGHT / 2 + 40
        );

        return;
    }

    update();
    requestAnimationFrame(draw);
}

function update() {

    // 공 이동
    ball.x += ball.dx;
    ball.y += ball.dy;

    // 좌우 벽 충돌
    if (
        ball.x + ball.radius > WIDTH ||
        ball.x - ball.radius < 0
    ) {
        ball.dx *= -1;
    }

    // 위쪽 벽 충돌
    if (ball.y - ball.radius < 0) {
        ball.dy *= -1;
    }

    // 패들 이동
    if (leftPressed) {
        paddle.x -= paddle.speed;
    }

    if (rightPressed) {
        paddle.x += paddle.speed;
    }

    paddle.x = Math.max(
        0,
        Math.min(WIDTH - paddle.width, paddle.x)
    );

    // 패들 충돌
    const paddleY = HEIGHT - paddle.height - 10;

    if (
        ball.y + ball.radius >= paddleY &&
        ball.y - ball.radius <= paddleY + paddle.height &&
        ball.x >= paddle.x &&
        ball.x <= paddle.x + paddle.width &&
        ball.dy > 0
    ) {
        ball.dy *= -1;

        // 패들 어느 위치에 맞았는지에 따라 방향 변경
        const hit =
            (ball.x - (paddle.x + paddle.width / 2))
            / (paddle.width / 2);

        ball.dx = hit * 6;
    }

    // 벽돌 충돌
    for (let r = 0; r < brick.rowCount; r++) {
        for (let c = 0; c < brick.columnCount; c++) {

            const b = bricks[r][c];

            if (!b.al

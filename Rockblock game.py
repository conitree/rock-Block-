import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Rock Block",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 Rock Block")
st.caption("← → 키 또는 아래 버튼으로 패들을 움직이세요")


GAME_HTML = r'''
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">

<style>
html, body {
    margin: 0;
    padding: 0;
    background: #111;
    color: white;
    font-family: Arial, sans-serif;
}

body {
    text-align: center;
    overflow: hidden;
}

#info {
    margin: 8px 0;
    font-size: 15px;
    line-height: 1.8;
}

canvas {
    display: block;
    width: 640px;
    max-width: 100%;
    height: auto;
    margin: 0 auto;
    background: #181818;
    border: 2px solid #555;
    border-radius: 8px;
    touch-action: none;
}

#legend {
    margin-top: 7px;
    font-size: 13px;
}

.controls {
    margin-top: 8px;
}

.control-button {
    width: 120px;
    height: 50px;
    margin: 3px;
    border: none;
    border-radius: 9px;
    background: #333;
    color: white;
    font-size: 25px;
    cursor: pointer;
    touch-action: none;
}

.control-button:active {
    background: #555;
}

#restart {
    width: 160px;
    height: 40px;
    margin-top: 8px;
    border: none;
    border-radius: 8px;
    background: #444;
    color: white;
    cursor: pointer;
}

#message {
    height: 25px;
    margin-top: 5px;
    font-size: 14px;
}
</style>
</head>

<body>

<div id="info">
    라운드 <span id="round">1</span>
    &nbsp;|&nbsp;
    점수 <span id="score">0</span>
    &nbsp;|&nbsp;
    최고점수 <span id="highScore">0</span>
    &nbsp;|&nbsp;
    ❤️ <span id="lives">3</span>
</div>

<canvas id="gameCanvas" width="640" height="500"></canvas>

<div id="legend">
    ★ 파란색 블록 = 멀티볼 블록
</div>

<div id="message"></div>

<div class="controls">
    <button class="control-button" id="leftButton">◀</button>
    <button class="control-button" id="rightButton">▶</button>
</div>

<button id="restart">다시 시작</button>


<script>

/* =========================================================
   기본 설정
========================================================= */

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const WIDTH = canvas.width;
const HEIGHT = canvas.height;


/* =========================================================
   UI
========================================================= */

const roundElement =
    document.getElementById("round");

const scoreElement =
    document.getElementById("score");

const highScoreElement =
    document.getElementById("highScore");

const livesElement =
    document.getElementById("lives");

const messageElement =
    document.getElementById("message");


/* =========================================================
   게임 상태
========================================================= */

let score = 0;
let lives = 3;
let round = 1;

let gameRunning = true;
let animationStarted = false;

let leftPressed = false;
let rightPressed = false;


/* =========================================================
   최고 기록
========================================================= */

let highScore =
    Number(localStorage.getItem("rockBlockHighScore")) || 0;

let highRound =
    Number(localStorage.getItem("rockBlockHighRound")) || 1;

highScoreElement.textContent = highScore;


/* =========================================================
   패들
========================================================= */

const paddle = {
    width: 105,
    height: 12,
    x: WIDTH / 2 - 52,
    y: HEIGHT - 30
};


/* =========================================================
   라운드별 패들 속도
========================================================= */

function getPaddleSpeed() {

    return Math.min(
        12 + (round - 1) * 2,
        30
    );
}


/* =========================================================
   메인볼
========================================================= */

const mainBall = {
    x: WIDTH / 2,
    y: HEIGHT - 55,
    radius: 9,
    dx: 4.5,
    dy: -4.5,
    active: true
};


/* =========================================================
   라운드별 공 속도
========================================================= */

function getBallSpeed() {

    return Math.min(
        4.5 + (round - 1) * 0.7,
        11
    );
}


/* =========================================================
   멀티볼
========================================================= */

let multiBalls = [];


function getMultiBallSpeed() {

    return Math.min(
        5.2 + (round - 1) * 0.5,
        10
    );
}


/* =========================================================
   블록 설정
========================================================= */

const ROWS = 6;
const COLS = 9;

const BRICK_WIDTH = 62;
const BRICK_HEIGHT = 24;
const BRICK_GAP = 7;

/*
   맨 위쪽에 공간을 만들기 위해
   블록 시작 위치를 아래로 배치
*/

const BRICK_TOP = 78;
const BRICK_LEFT = 20;

let bricks = [];


/* =========================================================
   강화 블록 HP
========================================================= */

function generateHP() {

    const random = Math.random();

    /*
       초반에는 1~3 위주
    */

    if (round === 1) {

        if (random < 0.70) {
            return 1;
        }

        if (random < 0.95) {
            return 2;
        }

        return 3;
    }


    if (round === 2) {

        if (random < 0.55) {
            return 1;
        }

        if (random < 0.90) {
            return 2;
        }

        return 3;
    }


    if (round === 3) {

        if (random < 0.40) {
            return 1;
        }

        if (random < 0.82) {
            return 2;
        }

        if (random < 0.97) {
            return 3;
        }

        return 4;
    }


    /*
       후반 라운드
    */

    if (random < 0.25) {
        return 1;
    }

    if (random < 0.60) {
        return 2;
    }

    if (random < 0.85) {
        return 3;
    }

    if (random < 0.96) {
        return 4;
    }

    return Math.min(
        6,
        5 + Math.floor((round - 4) / 3)
    );
}


/* =========================================================
   멀티볼 블록 확률
========================================================= */

function isMultiBlock() {

    const chance =
        Math.min(
            0.08 + round * 0.015,
            0.20
        );

    return Math.random() < chance;
}


/* =========================================================
   블록 생성
========================================================= */

function createBricks() {

    bricks = [];

    for (let row = 0; row < ROWS; row++) {

        bricks[row] = [];

        for (let col = 0; col < COLS; col++) {

            bricks[row][col] = {

                x:
                    BRICK_LEFT +
                    col * (BRICK_WIDTH + BRICK_GAP),

                y:
                    BRICK_TOP +
                    row * (BRICK_HEIGHT + BRICK_GAP),

                hp: generateHP(),

                alive: true,

                multi: isMultiBlock()
            };
        }
    }
}


/* =========================================================
   메인볼 리셋
========================================================= */

function resetMainBall() {

    const speed = getBallSpeed();

    mainBall.x = WIDTH / 2;
    mainBall.y = HEIGHT - 55;

    mainBall.dx =
        Math.random() < 0.5
        ? speed
        : -speed;

    mainBall.dy = -speed;

    mainBall.active = true;

    paddle.x =
        WIDTH / 2 -
        paddle.width / 2;
}


/* =========================================================
   멀티볼 생성
========================================================= */

function createMultiBalls() {

    const speed = getMultiBallSpeed();

    multiBalls.push({

        x: mainBall.x,
        y: mainBall.y,

        radius: 8,

        dx: -speed,
        dy: -speed * 0.82,

        active: true
    });


    multiBalls.push({

        x: mainBall.x,
        y: mainBall.y,

        radius: 8,

        dx: speed,
        dy: -speed * 0.72,

        active: true
    });


    messageElement.textContent =
        "MULTI BALL!";
}


/* =========================================================
   점수
========================================================= */

function addScore(points) {

    score += points;

    scoreElement.textContent = score;


    if (score > highScore) {

        highScore = score;

        highScoreElement.textContent =
            highScore;

        localStorage.setItem(
            "rockBlockHighScore",
            String(highScore)
        );
    }
}


/* =========================================================
   최고 라운드
========================================================= */

function updateHighRound() {

    if (round > highRound) {

        highRound = round;

        localStorage.setItem(
            "rockBlockHighRound",
            String(highRound)
        );
    }
}


/* =========================================================
   블록 색상
========================================================= */

function brickColor(hp, multi) {

    if (multi) {
        return "#087EFF";
    }

    if (hp >= 6) {
        return "#8E44AD";
    }

    if (hp >= 5) {
        return "#9B59B6";
    }

    if (hp >= 4) {
        return "#3498DB";
    }

    if (hp === 3) {
        return "#2980B9";
    }

    if (hp === 2) {
        return "#F39C12";
    }

    return "#E74C3C";
}


/* =========================================================
   블록 그리기
========================================================= */

function drawBricks() {

    for (let row = 0; row < ROWS; row++) {

        for (let col = 0; col < COLS; col++) {

            const brick =
                bricks[row][col];

            if (!brick.alive) {
                continue;
            }


            ctx.fillStyle =
                brickColor(
                    brick.hp,
                    brick.multi
                );


            ctx.fillRect(
                brick.x,
                brick.y,
                BRICK_WIDTH,
                BRICK_HEIGHT
            );


            /*
               HP 숫자
            */

            ctx.fillStyle = "#FFFFFF";

            ctx.font =
                "bold 15px Arial";

            ctx.textAlign = "center";
            ctx.textBaseline = "middle";

            ctx.fillText(
                String(brick.hp),
                brick.x + BRICK_WIDTH / 2,
                brick.y + BRICK_HEIGHT / 2
            );


            /*
               멀티볼 표시
            */

            if (brick.multi) {

                ctx.fillStyle = "#FFFF00";

                ctx.font =
                    "bold 13px Arial";

                ctx.fillText(
                    "★",
                    brick.x + BRICK_WIDTH - 9,
                    brick.y + 8
                );
            }
        }
    }
}


/* =========================================================
   패들 그리기
========================================================= */

function drawPaddle() {

    ctx.fillStyle = "#45D66A";

    ctx.fillRect(
        paddle.x,
        paddle.y,
        paddle.width,
        paddle.height
    );
}


/* =========================================================
   메인볼 그리기
========================================================= */

function drawMainBall() {

    if (!mainBall.active) {
        return;
    }

    ctx.beginPath();

    ctx.arc(
        mainBall.x,
        mainBall.y,
        mainBall.radius,
        0,
        Math.PI * 2
    );

    /*
       메인볼은 높은 가시성의 노란색
    */

    ctx.fillStyle = "#FFFF00";

    ctx.shadowColor = "#FFFF00";
    ctx.shadowBlur = 15;

    ctx.fill();

    ctx.shadowBlur = 0;

    ctx.closePath();
}


/* =========================================================
   멀티볼 그리기
========================================================= */

function drawMultiBalls() {

    for (const ball of multiBalls) {

        if (!ball.active) {
            continue;
        }

        ctx.beginPath();

        ctx.arc(
            ball.x,
            ball.y,
            ball.radius,
            0,
            Math.PI * 2
        );

        /*
           메인볼과 확실히 다른 색
        */

        ctx.fillStyle = "#00BFFF";

        ctx.shadowColor = "#00BFFF";
        ctx.shadowBlur = 10;

        ctx.fill();

        ctx.shadowBlur = 0;

        ctx.closePath();
    }
}


/* =========================================================
   블록 충돌
========================================================= */

function checkBrickCollision(
    ball,
    isMainBall
) {

    for (let row = 0; row < ROWS; row++) {

        for (let col = 0; col < COLS; col++) {

            const brick =
                bricks[row][col];

            if (!brick.alive) {
                continue;
            }


            const collision =
                ball.x + ball.radius > brick.x &&
                ball.x - ball.radius <
                    brick.x + BRICK_WIDTH &&
                ball.y + ball.radius > brick.y &&
                ball.y - ball.radius <
                    brick.y + BRICK_HEIGHT;


            if (!collision) {
                continue;
            }


            /*
               한 번 부딪힐 때 HP 1 감소
            */

            brick.hp--;

            ball.dy *= -1;

            addScore(2);


            /*
               블록 파괴
            */

            if (brick.hp <= 0) {

                brick.alive = false;

                addScore(8);


                /*
                   멀티볼 블록을
                   메인볼이 파괴했을 때만
                   멀티볼 생성
                */

                if (
                    brick.multi &&
                    isMainBall
                ) {

                    createMultiBalls();
                }
            }

            return;
        }
    }
}


/* =========================================================
   패들 충돌
========================================================= */

function checkPaddleCollision(ball) {

    if (ball.dy <= 0) {
        return;
    }


    const hit =
        ball.x + ball.radius >= paddle.x &&
        ball.x - ball.radius <=
            paddle.x + paddle.width &&
        ball.y + ball.radius >= paddle.y &&
        ball.y - ball.radius <=
            paddle.y + paddle.height;


    if (!hit) {
        return;
    }


    ball.dy =
        -Math.abs(ball.dy);


    /*
       패들 어느 위치에 맞았는지에 따라
       공의 방향을 바꿈
    */

    const offset =
        (
            ball.x -
            (paddle.x + paddle.width / 2)
        ) /
        (paddle.width / 2);


    const maximumHorizontal =
        Math.min(
            7 + (round - 1) * 0.2,
            9
        );


    ball.dx =
        offset * maximumHorizontal;
}


/* =========================================================
   메인볼 업데이트
========================================================= */

function updateMainBall() {

    if (!mainBall.active) {
        return;
    }


    mainBall.x += mainBall.dx;
    mainBall.y += mainBall.dy;


    /*
       좌우 벽
    */

    if (
        mainBall.x + mainBall.radius >= WIDTH ||
        mainBall.x - mainBall.radius <= 0
    ) {

        mainBall.dx *= -1;
    }


    /*
       위쪽 벽
    */

    if (
        mainBall.y - mainBall.radius <= 0
    ) {

        mainBall.dy *= -1;
    }


    checkPaddleCollision(mainBall);

    checkBrickCollision(
        mainBall,
        true
    );


    /*
       메인볼이 떨어지면 목숨 감소
    */

    if (
        mainBall.y - mainBall.radius > HEIGHT
    ) {

        lives--;

        livesElement.textContent =
            lives;


        /*
           멀티볼은 같이 제거
        */

        multiBalls = [];


        if (lives <= 0) {

            mainBall.active = false;

            gameRunning = false;

            messageElement.textContent =
                "게임 오버";

        }
        else {

            resetMainBall();
        }
    }
}


/* =========================================================
   멀티볼 업데이트
========================================================= */

function updateMultiBalls() {

    for (const ball of multiBalls) {

        if (!ball.active) {
            continue;
        }


        ball.x += ball.dx;
        ball.y += ball.dy;


        /*
           좌우 벽
        */

        if (
            ball.x + ball.radius >= WIDTH ||
            ball.x - ball.radius <= 0
        ) {

            ball.dx *= -1;
        }


        /*
           위쪽 벽
        */

        if (
            ball.y - ball.radius <= 0
        ) {

            ball.dy *= -1;
        }


        checkPaddleCollision(ball);

        checkBrickCollision(
            ball,
            false
        );


        /*
           멀티볼이 떨어져도
           목숨 감소 없음
        */

        if (
            ball.y - ball.radius > HEIGHT
        ) {

            ball.active = false;
        }
    }


    multiBalls =
        multiBalls.filter(
            function(ball) {
                return ball.active;
            }
        );
}


/* =========================================================
   남은 블록 수
========================================================= */

function countAliveBricks() {

    let count = 0;

    for (let row = 0; row < ROWS; row++) {

        for (let col = 0; col < COLS; col++) {

            if (bricks[row][col].alive) {
                count++;
            }
        }
    }

    return count;
}


/* =========================================================
   다음 라운드
========================================================= */

function nextRound() {

    round++;

    roundElement.textContent =
        round;


    updateHighRound();


    /*
       다음 라운드에서는
       멀티볼을 정리하고
       새 블록 생성
    */

    multiBalls = [];

    createBricks();

    resetMainBall();


    messageElement.textContent =
        "ROUND " + round + "!";
}


/* =========================================================
   패들 업데이트
========================================================= */

function updatePaddle() {

    const speed =
        getPaddleSpeed();


    if (leftPressed) {

        paddle.x -= speed;
    }


    if (rightPressed) {

        paddle.x += speed;
    }


    if (paddle.x < 0) {

        paddle.x = 0;
    }


    if (
        paddle.x + paddle.width > WIDTH
    ) {

        paddle.x =
            WIDTH - paddle.width;
    }
}


/* =========================================================
   전체 업데이트
========================================================= */

function update() {

    if (!gameRunning) {
        return;
    }


    updatePaddle();

    updateMainBall();

    updateMultiBalls();


    /*
       모든 블록을 깨면
       다음 라운드
    */

    if (
        countAliveBricks() === 0
    ) {

        nextRound();
    }
}


/* =========================================================
   게임오버 화면
========================================================= */

function drawGameOver() {

    ctx.fillStyle =
        "rgba(0, 0, 0, 0.78)";

    ctx.fillRect(
        0,
        0,
        WIDTH,
        HEIGHT
    );


    ctx.fillStyle = "#FFFFFF";

    ctx.textAlign = "center";

    ctx.font =
        "bold 34px Arial";

    ctx.fillText(
        "GAME OVER",
        WIDTH / 2,
        HEIGHT / 2 - 40
    );


    ctx.font =
        "18px Arial";

    ctx.fillText(
        "점수: " + score,
        WIDTH / 2,
        HEIGHT / 2
    );


    ctx.fillText(
        "도달 라운드: " + round,
        WIDTH / 2,
        HEIGHT / 2 + 32
    );


    ctx.fillText(
        "최고점수: " + highScore,
        WIDTH / 2,
        HEIGHT / 2 + 64
    );
}


/* =========================================================
   화면 그리기
========================================================= */

function draw() {

    ctx.clearRect(
        0,
        0,
        WIDTH,
        HEIGHT
    );


    drawBricks();

    drawMainBall();

    drawMultiBalls();

    drawPaddle();


    if (!gameRunning) {

        drawGameOver();

        return;
    }


    update();

    requestAnimationFrame(draw);
}


/* =========================================================
   키보드 입력
========================================================= */

document.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "ArrowLeft") {

            event.preventDefault();

            leftPressed = true;
        }


        if (event.key === "ArrowRight") {

            event.preventDefault();

            rightPressed = true;
        }
    }
);


document.addEventListener(
    "keyup",
    function(event) {

        if (event.key === "ArrowLeft") {

            leftPressed = false;
        }


        if (event.key === "ArrowRight") {

            rightPressed = false;
        }
    }
);


/* =========================================================
   버튼 입력
========================================================= */

const leftButton =
    document.getElementById("leftButton");

const rightButton =
    document.getElementById("rightButton");


function startLeft(event) {

    event.preventDefault();

    leftPressed = true;
}


function stopLeft(event) {

    event.preventDefault();

    leftPressed = false;
}


function startRight(event) {

    event.preventDefault();

    rightPressed = true;
}


function stopRight(event) {

    event.preventDefault();

    rightPressed = false;
}


/* 마우스 */

leftButton.addEventListener(
    "mousedown",
    startLeft
);

leftButton.addEventListener(
    "mouseup",
    stopLeft
);

leftButton.addEventListener(
    "mouseleave",
    stopLeft
);


rightButton.addEventListener(
    "mousedown",
    startRight
);

rightButton.addEventListener(
    "mouseup",
    stopRight
);

rightButton.addEventListener(
    "mouseleave",
    stopRight
);


/* 터치 */

leftButton.addEventListener(
    "touchstart",
    startLeft,
    { passive: false }
);

leftButton.addEventListener(
    "touchend",
    stopLeft,
    { passive: false }
);

leftButton.addEventListener(
    "touchcancel",
    stopLeft,
    { passive: false }
);


rightButton.addEventListener(
    "touchstart",
    startRight,
    { passive: false }
);

rightButton.addEventListener(
    "touchend",
    stopRight,
    { passive: false }
);

rightButton.addEventListener(
    "touchcancel",
    stopRight,
    { passive: false }
);


/* =========================================================
   다시 시작
========================================================= */

document
    .getElementById("restart")
    .addEventListener(
        "click",
        function() {

            score = 0;

            lives = 3;

            round = 1;

            gameRunning = true;

            leftPressed = false;

            rightPressed = false;

            multiBalls = [];


            scoreElement.textContent = "0";

            livesElement.textContent = "3";

            roundElement.textContent = "1";

            messageElement.textContent = "";


            createBricks();

            resetMainBall();


            /*
               이미 게임 루프가 살아있다면
               새 루프를 만들지 않음
            */

            if (!animationStarted) {

                animationStarted = true;

                requestAnimationFrame(draw);
            }
        }
    );


/* =========================================================
   게임 시작
========================================================= */

createBricks();

resetMainBall();

animationStarted = true;

requestAnimationFrame(draw);

</script>

</body>
</html>
'''


components.html(
    GAME_HTML,
    height=680,
    scrolling=False
)

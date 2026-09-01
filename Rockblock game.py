import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Rock Block",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 Rock Block")

html = r'''
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

#info {
    font-size: 16px;
    margin: 8px;
}

canvas {
    display: block;
    margin: auto;
    background: #181818;
    border: 2px solid #555;
    border-radius: 8px;
    max-width: 100%;
    touch-action: none;
}

button {
    width: 120px;
    height: 50px;
    margin: 8px 4px;
    font-size: 24px;
    border: 0;
    border-radius: 8px;
    cursor: pointer;
}

#restart {
    width: 160px;
    height: 40px;
    font-size: 16px;
}
</style>
</head>

<body>

<div id="info">
    라운드 <span id="round">1</span>
    &nbsp; | &nbsp;
    점수 <span id="score">0</span>
    &nbsp; | &nbsp;
    최고점수 <span id="best">0</span>
    &nbsp; | &nbsp;
    ❤️ <span id="lives">3</span>
</div>

<canvas id="game" width="640" height="500"></canvas>

<div>
    ★ 파란색 블록 = 멀티볼
</div>

<div>
    <button id="left">◀</button>
    <button id="right">▶</button>
</div>

<button id="restart">다시 시작</button>


<script>

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const W = canvas.width;
const H = canvas.height;


/* ==========================
   UI
========================== */

const roundText = document.getElementById("round");
const scoreText = document.getElementById("score");
const bestText = document.getElementById("best");
const livesText = document.getElementById("lives");


/* ==========================
   기록
========================== */

let score = 0;
let lives = 3;
let round = 1;

let best =
    Number(localStorage.getItem("rock_block_best")) || 0;

bestText.textContent = best;


/* ==========================
   입력
========================== */

let left = false;
let right = false;


/* ==========================
   패들
========================== */

const paddle = {
    x: W / 2 - 52,
    y: H - 30,
    width: 105,
    height: 12
};


/* ==========================
   공
========================== */

const mainBall = {
    x: W / 2,
    y: H - 55,
    radius: 9,
    dx: 4,
    dy: -4,
    active: true
};

let extraBalls = [];


/* ==========================
   블록
========================== */

const ROWS = 6;
const COLS = 9;

const BRICK_W = 62;
const BRICK_H = 24;
const GAP = 7;

const TOP = 70;
const LEFT = 20;

let bricks = [];


/* ==========================
   라운드별 속도
========================== */

function ballSpeed() {

    return Math.min(
        4.5 + (round - 1) * 0.7,
        10
    );
}


function paddleSpeed() {

    return Math.min(
        14 + (round - 1) * 2,
        30
    );
}


function multiSpeed() {

    return Math.min(
        5.5 + (round - 1) * 0.5,
        9
    );
}


/* ==========================
   블록 HP
========================== */

function randomHP() {

    const r = Math.random();

    if (round === 1) {

        if (r < 0.65) return 1;
        if (r < 0.95) return 2;

        return 3;
    }

    if (round <= 3) {

        if (r < 0.45) return 1;
        if (r < 0.85) return 2;

        return 3;
    }

    if (r < 0.25) return 1;
    if (r < 0.65) return 2;
    if (r < 0.90) return 3;

    return Math.min(
        5,
        4 + Math.floor((round - 4) / 3)
    );
}


/* ==========================
   블록 생성
========================== */

function makeBricks() {

    bricks = [];

    for (let r = 0; r < ROWS; r++) {

        bricks[r] = [];

        for (let c = 0; c < COLS; c++) {

            let hp = randomHP();

            let chance =
                Math.min(
                    0.08 + round * 0.015,
                    0.18
                );

            bricks[r][c] = {

                x: LEFT +
                   c * (BRICK_W + GAP),

                y: TOP +
                   r * (BRICK_H + GAP),

                hp: hp,

                alive: true,

                multi:
                    Math.random() < chance
            };
        }
    }
}


/* ==========================
   공 리셋
========================== */

function resetBall() {

    const speed = ballSpeed();

    mainBall.x = W / 2;
    mainBall.y = H - 55;

    mainBall.dx =
        Math.random() < 0.5
        ? speed
        : -speed;

    mainBall.dy = -speed;

    mainBall.active = true;

    paddle.x =
        W / 2 - paddle.width / 2;
}


/* ==========================
   멀티볼 생성
========================== */

function spawnMultiBalls() {

    const speed = multiSpeed();

    extraBalls.push({
        x: mainBall.x,
        y: mainBall.y,
        radius: 8,
        dx: -speed,
        dy: -speed * 0.8,
        active: true
    });

    extraBalls.push({
        x: mainBall.x,
        y: mainBall.y,
        radius: 8,
        dx: speed,
        dy: -speed * 0.7,
        active: true
    });
}


/* ==========================
   점수
========================== */

function addScore(value) {

    score += value;

    scoreText.textContent = score;

    if (score > best) {

        best = score;

        bestText.textContent = best;

        localStorage.setItem(
            "rock_block_best",
            best
        );
    }
}


/* ==========================
   블록 그리기
========================== */

function drawBricks() {

    for (let r = 0; r < ROWS; r++) {

        for (let c = 0; c < COLS; c++) {

            const b = bricks[r][c];

            if (!b.alive) continue;


            if (b.multi) {
                ctx.fillStyle = "#087eff";
            }
            else if (b.hp >= 4) {
                ctx.fillStyle = "#9b59b6";
            }
            else if (b.hp === 3) {
                ctx.fillStyle = "#3498db";
            }
            else if (b.hp === 2) {
                ctx.fillStyle = "#f39c12";
            }
            else {
                ctx.fillStyle = "#e74c3c";
            }


            ctx.fillRect(
                b.x,
                b.y,
                BRICK_W,
                BRICK_H
            );


            ctx.fillStyle = "white";
            ctx.font = "bold 15px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";

            ctx.fillText(
                b.hp,
                b.x + BRICK_W / 2,
                b.y + BRICK_H / 2
            );


            if (b.multi) {

                ctx.fillStyle = "#ffff00";
                ctx.font = "bold 14px Arial";

                ctx.fillText(
                    "★",
                    b.x + BRICK_W - 9,
                    b.y + 9
                );
            }
        }
    }
}


/* ==========================
   패들 그리기
========================== */

function drawPaddle() {

    ctx.fillStyle = "#4CAF50";

    ctx.fillRect(
        paddle.x,
        paddle.y,
        paddle.width,
        paddle.height
    );
}


/* ==========================
   메인볼 그리기
========================== */

function drawMainBall() {

    if (!mainBall.active) return;

    ctx.beginPath();

    ctx.arc(
        mainBall.x,
        mainBall.y,
        mainBall.radius,
        0,
        Math.PI * 2
    );

    ctx.fillStyle = "#FFFF00";

    ctx.shadowColor = "#FFFF00";
    ctx.shadowBlur = 12;

    ctx.fill();

    ctx.shadowBlur = 0;

    ctx.closePath();
}


/* ==========================
   멀티볼 그리기
========================== */

function drawExtraBalls() {

    for (const b of extraBalls) {

        if (!b.active) continue;

        ctx.beginPath();

        ctx.arc(
            b.x,
            b.y,
            b.radius,
            0,
            Math.PI * 2
        );

        ctx.fillStyle = "#00BFFF";

        ctx.shadowColor = "#00BFFF";
        ctx.shadowBlur = 8;

        ctx.fill();

        ctx.shadowBlur = 0;

        ctx.closePath();
    }
}


/* ==========================
   블록 충돌
========================== */

function hitBricks(ball, isMain) {

    for (let r = 0; r < ROWS; r++) {

        for (let c = 0; c < COLS; c++) {

            const b = bricks[r][c];

            if (!b.alive) continue;

            if (
                ball.x + ball.radius > b.x &&
                ball.x - ball.radius < b.x + BRICK_W &&
                ball.y + ball.radius > b.y &&
                ball.y - ball.radius < b.y + BRICK_H
            ) {

                b.hp--;

                ball.dy *= -1;

                if (b.hp <= 0) {

                    b.alive = false;

                    addScore(10);


                    if (
                        b.multi &&
                        isMain
                    ) {

                        spawnMultiBalls();

                        addScore(20);
                    }
                }

                return;
            }
        }
    }
}


/* ==========================
   패들 충돌
========================== */

function hitPaddle(ball) {

    if (
        ball.dy > 0 &&
        ball.x >= paddle.x &&
        ball.x <= paddle.x + paddle.width &&
        ball.y + ball.radius >= paddle.y &&
        ball.y - ball.radius <= paddle.y + paddle.height
    ) {

        ball.dy =
            -Math.abs(ball.dy);

        const offset =
            (
                ball.x -
                (paddle.x + paddle.width / 2)
            ) /
            (paddle.width / 2);

        ball.dx =
            offset * Math.min(
                7 + (round - 1) * 0.2,
                9
            );
    }
}


/* ==========================
   메인볼 업데이트
========================== */

function updateMainBall() {

    if (!mainBall.active) return;

    mainBall.x += mainBall.dx;
    mainBall.y += mainBall.dy;


    if (
        mainBall.x + mainBall.radius >= W ||
        mainBall.x - mainBall.radius <= 0
    ) {
        mainBall.dx *= -1;
    }


    if (
        mainBall.y - mainBall.radius <= 0
    ) {
        mainBall.dy *= -1;
    }


    hitPaddle(mainBall);

    hitBricks(mainBall, true);


    /*
    메인볼이 떨어질 때만
    목숨 감소
    */

    if (
        mainBall.y - mainBall.radius > H
    ) {

        lives--;

        livesText.textContent = lives;

        extraBalls = [];

        if (lives <= 0) {

            mainBall.active = false;

            running = false;

        }
        else {

            resetBall();
        }
    }
}


/* ==========================
   멀티볼 업데이트
========================== */

function updateExtraBalls() {

    for (const ball of extraBalls) {

        if (!ball.active) continue;

        ball.x += ball.dx;
        ball.y += ball.dy;


        if (
            ball.x + ball.radius >= W ||
            ball.x - ball.radius <= 0
        ) {

            ball.dx *= -1;
        }


        if (
            ball.y - ball.radius <= 0
        ) {

            ball.dy *= -1;
        }


        hitPaddle(ball);

        hitBricks(ball, false);


        /*
        멀티볼은 떨어져도
        목숨을 깎지 않는다.
        */

        if (
            ball.y - ball.radius > H
        ) {

            ball.active = false;
        }
    }


    extraBalls =
        extraBalls.filter(
            b => b.active
        );
}


/* ==========================
   남은 블록
========================== */

function remainingBricks() {

    let count = 0;

    for (let r = 0; r < ROWS; r++) {

        for (let c = 0; c < COLS; c++) {

            if (bricks[r][c].alive) {
                count++;
            }
        }
    }

    return count;
}


/* ==========================
   다음 라운드
========================== */

function nextRound() {

    round++;

    roundText.textContent = round;

    extraBalls = [];

    makeBricks();

    resetBall();
}


/* ==========================
   게임 상태
========================== */

let running = true;


/* ==========================
   업데이트
========================== */

function update() {

    if (!running) return;


    const speed = paddleSpeed();


    if (left) {
        paddle.x -= speed;
    }

    if (right) {
        paddle.x += speed;
    }


    if (paddle.x < 0) {
        paddle.x = 0;
    }

    if (
        paddle.x + paddle.width > W
    ) {

        paddle.x =
            W - paddle.width;
    }


    updateMainBall();

    updateExtraBalls();


    if (remainingBricks() === 0) {

        nextRound();
    }
}


/* ==========================
   화면
========================== */

function draw() {

    ctx.clearRect(
        0,
        0,
        W,
        H
    );

    drawBricks();

    drawMainBall();

    drawExtraBalls();

    drawPaddle();


    if (!running) {

        ctx.fillStyle =
            "rgba(0,0,0,0.78)";

        ctx.fillRect(
            0,
            0,
            W,
            H
        );

        ctx.fillStyle = "white";

        ctx.textAlign = "center";

        ctx.font =
            "bold 32px Arial";

        ctx.fillText(
            "GAME OVER",
            W / 2,
            H / 2
        );

        ctx.font =
            "18px Arial";

        ctx.fillText(
            "점수: " + score,
            W / 2,
            H / 2 + 40
        );

        ctx.fillText(
            "라운드: " + round,
            W / 2,
            H / 2 + 70
        );

        return;
    }


    update();

    requestAnimationFrame(draw);
}


/* ==========================
   키보드
========================== */

document.addEventListener(
    "keydown",
    function(e) {

        if (e.key === "ArrowLeft") {
            left = true;
        }

        if (e.key === "ArrowRight") {
            right = true;
        }
    }
);


document.addEventListener(
    "keyup",
    function(e) {

        if (e.key === "ArrowLeft") {
            left = false;
        }

        if (e.key === "ArrowRight") {
            right = false;
        }
    }
);


/* ==========================
   버튼
========================== */

const leftButton =
    document.getElementById("left");

const rightButton =
    document.getElementById("right");


leftButton.addEventListener(
    "mousedown",
    function() {
        left = true;
    }
);

leftButton.addEventListener(
    "mouseup",
    function() {
        left = false;
    }
);

leftButton.addEventListener(
    "mouseleave",
    function() {
        left = false;
    }
);


rightButton.addEventListener(
    "mousedown",
    function() {
        right = true;
    }
);

rightButton.addEventListener(
    "mouseup",
    function() {
        right = false;
    }
);

rightButton.addEventListener(
    "mouseleave",
    function() {
        right = false;
    }
);


leftButton.addEventListener(
    "touchstart",
    function(e) {
        e.preventDefault();
        left = true;
    },
    { passive: false }
);

leftButton.addEventListener(
    "touchend",
    function(e) {
        e.preventDefault();
        left = false;
    },
    { passive: false }
);


rightButton.addEventListener(
    "touchstart",
    function(e) {
        e.preventDefault();
        right = true;
    },
    { passive: false }
);

rightButton.addEventListener(
    "touchend",
    function(e) {
        e.preventDefault();
        right = false;
    },
    { passive: false }
);


/* ==========================
   다시 시작
========================== */

document
.getElementById("restart")
.addEventListener(
    "click",
    function() {

        score = 0;
        lives = 3;
        round = 1;

        running = true;

        extraBalls = [];

        scoreText.textContent = 0;
        livesText.textContent = 3;
        roundText.textContent = 1;

        makeBricks();
        resetBall();

        requestAnimationFrame(draw);
    }
);


/* ==========================
   시작
========================== */

makeBricks();

resetBall();

draw();

</script>

</body>
</html>
'''

components.html(
    html,
    height=650,
    scrolling=False
)    margin: auto;
    background: #181818;
    border: 2px solid #555;
    border-radius: 8px;
    max-width: 100%;
    touch-action: none;
}

.controls {
    margin-top: 10px;
}

.controls button {
    width: 125px;
    height: 52px;
    margin: 5px;
    font-size: 25px;
    border: none;
    border-radius: 9px;
    cursor: pointer;
    user-select: none;
    -webkit-user-select: none;
    touch-action: none;
}

#restart {
    width: 170px;
    height: 42px;
    font-size: 16px;
}

.legend {
    margin-top: 5px;
    font-size: 14px;
}

</style>
</head>

<body>

<div class="info">

라운드:
<span id="round">1</span>

&nbsp;&nbsp;

점수:
<span id="score">0</span>

&nbsp;&nbsp;

최고점수:
<span id="highScore">0</span>

<br>

최고라운드:
<span id="highRound">1</span>

&nbsp;&nbsp;

❤️
<span id="lives">3</span>

</div>

<canvas
    id="gameCanvas"
    width="640"
    height="500">
</canvas>

<div class="legend">
    ★ = 멀티볼 블록
</div>

<div class="controls">

    <button id="left">◀</button>
    <button id="right">▶</button>

</div>

<button id="restart">
    다시 시작
</button>


<script>

const canvas =
    document.getElementById("gameCanvas");

const ctx =
    canvas.getContext("2d");

const scoreElement =
    document.getElementById("score");

const highScoreElement =
    document.getElementById("highScore");

const highRoundElement =
    document.getElementById("highRound");

const roundElement =
    document.getElementById("round");

const livesElement =
    document.getElementById("lives");

const WIDTH = canvas.width;
const HEIGHT = canvas.height;


/* =====================================
   게임 상태
===================================== */

let score = 0;

let lives = 3;

let round = 1;

let running = true;

let leftPressed = false;

let rightPressed = false;


/* =====================================
   최고 기록
===================================== */

let highScore =
    Number(
        localStorage.getItem(
            "rockBlockHighScore"
        )
    ) || 0;

let highRound =
    Number(
        localStorage.getItem(
            "rockBlockHighRound"
        )
    ) || 1;


highScoreElement.textContent =
    highScore;

highRoundElement.textContent =
    highRound;


/* =====================================
   패들
===================================== */

const paddle = {

    width: 105,

    height: 12,

    x: WIDTH / 2 - 52

};


/*
라운드별 패들 속도

1라운드 = 14
2라운드 = 16
3라운드 = 18
...
최대 = 30
*/

function getPaddleSpeed() {

    return Math.min(
        14 + (round - 1) * 2,
        30
    );

}


/* =====================================
   메인볼
===================================== */

const mainBall = {

    x: WIDTH / 2,

    y: HEIGHT - 65,

    radius: 9,

    dx: 4.5,

    dy: -4.5,

    active: true

};


/*
라운드별 공 속도

1 = 4.5
2 = 5.2
3 = 5.9
...
최대 = 10
*/

function getBallSpeed() {

    return Math.min(
        4.5 + (round - 1) * 0.7,
        10
    );

}


/* =====================================
   멀티볼
===================================== */

let multiBalls = [];


/*
멀티볼 속도도 라운드에 따라 증가
*/

function getMultiBallSpeed() {

    return Math.min(
        5.5 + (round - 1) * 0.5,
        9
    );

}


/* =====================================
   블록 설정
===================================== */

const rows = 6;

const columns = 9;

const brickWidth = 62;

const brickHeight = 24;

const brickPadding = 7;


/*
맨 위에 공간을 둠
*/

const brickTop = 70;

const brickLeft = 20;

let bricks = [];


/* =====================================
   블록 HP 생성
===================================== */

function getBrickHP() {

    const random =
        Math.random();


    /*
    1라운드

    낮은 숫자 위주
    */

    if (round === 1) {

        if (random < 0.65) {
            return 1;
        }

        if (random < 0.95) {
            return 2;
        }

        return 3;
    }


    /*
    2~3라운드
    */

    if (round <= 3) {

        if (random < 0.45) {
            return 1;
        }

        if (random < 0.85) {
            return 2;
        }

        return 3;
    }


    /*
    4라운드 이후

    점점 강해짐
    */

    if (random < 0.25) {
        return 1;
    }

    if (random < 0.65) {
        return 2;
    }

    if (random < 0.90) {
        return 3;
    }


    return Math.min(
        5,
        4 + Math.floor(
            (round - 4) / 3
        )
    );

}


/* =====================================
   블록 생성
===================================== */

function createBricks() {

    bricks = [];


    for (
        let r = 0;
        r < rows;
        r++
    ) {

        bricks[r] = [];


        for (
            let c = 0;
            c < columns;
            c++
        ) {

            const hp =
                getBrickHP();


            /*
            라운드가 높아질수록
            멀티볼 블록 증가
            */

            const multiChance =
                Math.min(
                    0.08 +
                    round * 0.015,
                    0.18
                );


            const multi =
                Math.random() <
                multiChance;


            bricks[r][c] = {

                x: 0,

                y: 0,

                hp: hp,

                alive: true,

                multi: multi

            };

        }

    }

}


/* =====================================
   메인볼 리셋
===================================== */

function resetMainBall() {

    const speed =
        getBallSpeed();


    mainBall.x =
        WIDTH / 2;

    mainBall.y =
        HEIGHT - 65;


    mainBall.dx =
        Math.random() > 0.5
        ? speed
        : -speed;


    mainBall.dy =
        -speed;


    mainBall.active =
        true;


    paddle.x =
        WIDTH / 2 -
        paddle.width / 2;

}


/* =====================================
   멀티볼 생성
===================================== */

function createMultiBall() {

    const speed =
        getMultiBallSpeed();


    /*
    첫 번째 멀티볼
    */

    multiBalls.push({

        x: mainBall.x,

        y: mainBall.y,

        radius: 8,

        dx: -speed,

        dy: -speed * 0.82,

        active: true

    });


    /*
    두 번째 멀티볼
    */

    multiBalls.push({

        x: mainBall.x,

        y: mainBall.y,

        radius: 8,

        dx: speed,

        dy: -speed * 0.72,

        active: true

    });

}


/* =====================================
   점수
===================================== */

function addScore(amount) {

    score += amount;


    scoreElement.textContent =
        score;


    /*
    최고점수
    */

    if (score > highScore) {

        highScore =
            score;


        highScoreElement.textContent =
            highScore;


        localStorage.setItem(
            "rockBlockHighScore",
            highScore
        );

    }


    /*
    최고라운드
    */

    if (round > highRound) {

        highRound =
            round;


        highRoundElement.textContent =
            highRound;


        localStorage.setItem(
            "rockBlockHighRound",
            highRound
        );

    }

}


/* =====================================
   블록 그리기
===================================== */

function drawBricks() {

    for (
        let r = 0;
        r < rows;
        r++
    ) {

        for (
            let c = 0;
            c < columns;
            c++
        ) {

            const brick =
                bricks[r][c];


            if (!brick.alive) {
                continue;
            }


            brick.x =
                brickLeft +
                c *
                (
                    brickWidth +
                    brickPadding
                );


            brick.y =
                brickTop +
                r *
                (
                    brickHeight +
                    brickPadding
                );


            /*
            멀티볼 블록
            */

            if (brick.multi) {

                ctx.fillStyle =
                    "#008cff";

            }

            else if (brick.hp >= 4) {

                ctx.fillStyle =
                    "#9b59b6";

            }

            else if (brick.hp === 3) {

                ctx.fillStyle =
                    "#3498db";

            }

            else if (brick.hp === 2) {

                ctx.fillStyle =
                    "#f39c12";

            }

            else {

                ctx.fillStyle =
                    "#e74c3c";

            }


            ctx.fillRect(

                brick.x,

                brick.y,

                brickWidth,

                brickHeight

            );


            /*
            HP 숫자
            */

            ctx.fillStyle =
                "white";


            ctx.font =
                "bold 15px Arial";


            ctx.textAlign =
                "center";


            ctx.textBaseline =
                "middle";


            ctx.fillText(

                brick.hp,

                brick.x +
                brickWidth / 2,

                brick.y +
                brickHeight / 2

            );


            /*
            멀티볼 표시
            */

            if (brick.multi) {

                ctx.fillStyle =
                    "#ffff00";


                ctx.font =
                    "bold 14px Arial";


                ctx.fillText(

                    "★",

                    brick.x +
                    brickWidth -
                    9,

                    brick.y + 9

                );

            }

        }

    }

}


/* =====================================
   메인볼 그리기
===================================== */

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
    메인볼 = 매우 밝은 노란색
    */

    ctx.fillStyle =
        "#FFFF00";


    ctx.shadowColor =
        "#FFFF00";


    ctx.shadowBlur =
        14;


    ctx.fill();


    ctx.shadowBlur =
        0;


    ctx.closePath();

}


/* =====================================
   멀티볼 그리기
===================================== */

function drawMultiBalls() {

    for (
        const ball of multiBalls
    ) {

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
        멀티볼 = 파란색
        */

        ctx.fillStyle =
            "#00BFFF";


        ctx.shadowColor =
            "#00BFFF";


        ctx.shadowBlur =
            8;


        ctx.fill();


        ctx.shadowBlur =
            0;


        ctx.closePath();

    }

}


/* =====================================
   패들
===================================== */

function drawPaddle() {

    ctx.fillStyle =
        "#4CAF50";


    ctx.fillRect(

        paddle.x,

        HEIGHT - 30,

        paddle.width,

        paddle.height

    );

}


/* =====================================
   블록 충돌
===================================== */

function hitBrick(ball) {

    for (
        let r = 0;
        r < rows;
        r++
    ) {

        for (
            let c = 0;
            c < columns;
            c++
        ) {

            const brick =
                bricks[r][c];


            if (!brick.alive) {
                continue;
            }


            if (

                ball.x >
                brick.x &&

                ball.x <
                brick.x +
                brickWidth &&

                ball.y >
                brick.y &&

                ball.y <
                brick.y +
                brickHeight

            ) {


                /*
                HP 감소
                */

                brick.hp--;


                /*
                공 반사
                */

                ball.dy *= -1;


                /*
                완전히 파괴
                */

                if (
                    brick.hp <= 0
                ) {

                    brick.alive =
                        false;


                    /*
                    기본 점수
                    */

                    addScore(10);


                    /*
                    멀티볼 블록
                    */

                    if (
                        brick.multi &&
                        ball === mainBall
                    ) {

                        createMultiBall();


                        /*
                        보너스 점수
                        */

                        addScore(20);

                    }

                }


                return;

            }

        }

    }

}


/* =====================================
   패들 충돌
===================================== */

function checkPaddleCollision(
    ball
) {

    const paddleY =
        HEIGHT - 30;


    if (

        ball.x >= paddle.x &&

        ball.x <=
        paddle.x +
        paddle.width &&

        ball.y +
        ball.radius >=
        paddleY &&

        ball.y -
        ball.radius <=
        paddleY +
        paddle.height &&

        ball.dy > 0

    ) {


        /*
        공을 위로 튕김
        */

        ball.dy =
            -Math.abs(
                ball.dy
            );


        /*
        패들 맞은 위치에 따라
        공의 방향 변화
        */

        const position =
            (
                ball.x -
                (
                    paddle.x +
                    paddle.width / 2
                )
            )
            /
            (
                paddle.width / 2
            );


        /*
        라운드가 높을수록
        최대 방향 변화도 조금 증가
        */

        const directionPower =
            Math.min(
                7 +
                (round - 1) * 0.2,
                9
            );


        ball.dx =
            position *
            directionPower;

    }

}


/* =====================================
   메인볼 업데이트
===================================== */

function updateMainBall() {

    if (!mainBall.active) {
        return;
    }


    mainBall.x +=
        mainBall.dx;


    mainBall.y +=
        mainBall.dy;


    /*
    좌우 벽
    */

    if (

        mainBall.x +
        mainBall.radius >=
        WIDTH ||

        mainBall.x -
        mainBall.radius <=
        0

    ) {

        mainBall.dx *= -1;

    }


    /*
    위쪽 벽
    */

    if (
        mainBall.y -
        mainBall.radius <=
        0
    ) {

        mainBall.dy *= -1;

    }


    checkPaddleCollision(
        mainBall
    );


    hitBrick(
        mainBall
    );


    /*
    메인볼이 바닥으로 떨어짐

    ★ 여기서만 목숨 감소
    */

    if (
        mainBall.y -
        mainBall.radius >
        HEIGHT
    ) {

        lives--;


        livesElement.textContent =
            lives;


        if (lives <= 0) {

            mainBall.active =
                false;


            running =
                false;

        }

        else {

            resetMainBall();

        }

    }

}


/* =====================================
   멀티볼 업데이트
===================================== */

function updateMultiBalls() {

    for (
        const ball of multiBalls
    ) {

        if (!ball.active) {
            continue;
        }


        ball.x +=
            ball.dx;


        ball.y +=
            ball.dy;


        /*
        좌우 벽
        */

        if (

            ball.x +
            ball.radius >=
            WIDTH ||

            ball.x -
            ball.radius <=
            0

        ) {

            ball.dx *= -1;

        }


        /*
        위쪽 벽
        */

        if (
            ball.y -
            ball.radius <=
            0
        ) {

            ball.dy *= -1;

        }


        checkPaddleCollision(
            ball
        );


        hitBrick(
            ball
        );


        /*
        멀티볼이 떨어져도
        목숨 감소 X
        */

        if (
            ball.y -
            ball.radius >
            HEIGHT
        ) {

            ball.active =
                false;

        }

    }


    /*
    사라진 멀티볼 제거
    */

    multiBalls =
        multiBalls.filter(
            ball =>
                ball.active
        );

}


/* =====================================
   남은 블록 확인
===================================== */

function getRemainingBricks() {

    let remaining = 0;


    for (
        let r = 0;
        r < rows;
        r++
    ) {

        for (
            let c = 0;
            c < columns;
            c++
        ) {

            if (
                bricks[r][c].alive
            ) {

                remaining++;

            }

        }

    }


    return remaining;

}


/* =====================================
   다음 라운드
===================================== */

function nextRound() {

    /*
    라운드 증가
    */

    round++;


    roundElement.textContent =
        round;


    /*
    최고 라운드 기록
    */

    if (
        round > highRound
    ) {

        highRound =
            round;


        highRoundElement.textContent =
            highRound;


        localStorage.setItem(
            "rockBlockHighRound",
            highRound
        );

    }


    /*
    기존 멀티볼 제거
    */

    multiBalls = [];


    /*
    새로운 블록
    */

    createBricks();


    /*
    공을 새로운 속도로
    다시 시작
    */

    resetMainBall();

}


/* =====================================
   게임 업데이트
===================================== */

function update() {

    if (!running) {
        return;
    }


    /*
    ★ 라운드별 패들 속도
    */

    const currentPaddleSpeed =
        getPaddleSpeed();


    /*
    키보드 / 버튼
    */

    if (leftPressed) {

        paddle.x -=
            currentPaddleSpeed;

    }


    if (rightPressed) {

        paddle.x +=
            currentPaddleSpeed;

    }


    /*
    패들 범위 제한
    */

    if (paddle.x < 0) {

        paddle.x = 0;

    }


    if (
        paddle.x +
        paddle.width >
        WIDTH
    ) {

        paddle.x =
            WIDTH -
            paddle.width;

    }


    updateMainBall();

    updateMultiBalls();


    /*
    모든 블록 파괴
    */

    if (
        getRemainingBricks() === 0
    ) {

        nextRound();

    }

}


/* =====================================
   화면 그리기
===================================== */

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


    /*
    게임 종료 화면
    */

    if (!running) {

        ctx.fillStyle =
            "rgba(0,0,0,0.78)";


        ctx.fillRect(

            0,

            0,

            WIDTH,

            HEIGHT

        );


        ctx.fillStyle =
            "white";


        ctx.textAlign =
            "center";


        ctx.font =
            "bold 32px Arial";


        ctx.fillText(

            "GAME OVER",

            WIDTH / 2,

            HEIGHT / 2

        );


        ctx.font =
            "18px Arial";


        ctx.fillText(

            "점수: " +
            score,

            WIDTH / 2,

            HEIGHT / 2 + 40

        );


        ctx.fillText(

            "도달 라운드: " +
            round,

            WIDTH / 2,

            HEIGHT / 2 + 70

        );


        ctx.fillText(

            "최고점수: " +
            highScore,

            WIDTH / 2,

            HEIGHT / 2 + 100

        );


        return;

    }


    update();


    requestAnimationFrame(
        draw
    );

}


/* =====================================
   키보드
===================================== */

document.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key ===
            "ArrowLeft"
        ) {

            leftPressed =
                true;

        }


        if (
            event.key ===
            "ArrowRight"
        ) {

            rightPressed =
                true;

        }

    }
);


document.addEventListener(
    "keyup",
    function(event) {

        if (
            event.key ===
            "ArrowLeft"
        ) {

            leftPressed =
                false;

        }


        if (
            event.key ===
            "ArrowRight"
        ) {

            rightPressed =
                false;

        }

    }
);


/* =====================================
   모바일 / 마우스 버튼
===================================== */

const leftButton =
    document.getElementById(
        "left"
    );

const rightButton =
    document.getElementById(
        "right"
    );


/*
왼쪽 버튼
*/

leftButton.addEventListener(
    "mousedown",
    function() {

        leftPressed =
            true;

    }
);


leftButton.addEventListener(
    "mouseup",
    function() {

        leftPressed =
            false;

    }
);


leftButton.addEventListener(
    "mouseleave",
    function() {

        leftPressed =
            false;

    }
);


leftButton.addEventListener(
    "touchstart",
    function(event) {

        event.preventDefault();

        leftPressed =
            true;

    }
);


leftButton.addEventListener(
    "touchend",
    function(event) {

        event.preventDefault();

        leftPressed =
            false;

    }
);


/*
오른쪽 버튼
*/

rightButton.addEventListener(
    "mousedown",
    function() {

        rightPressed =
            true;

    }
);


rightButton.addEventListener(
    "mouseup",
    function() {

        rightPressed =
            false;

    }
);


rightButton.addEventListener(
    "mouseleave",
    function() {

        rightPressed =
            false;

    }
);


rightButton.addEventListener(
    "touchstart",
    function(event) {

        event.preventDefault();

        rightPressed =
            true;

    }
);


rightButton.addEventListener(
    "touchend",
    function(event) {

        event.preventDefault();

        rightPressed =
            false;

    }
);


/* =====================================
   다시 시작
===================================== */

document
.getElementById("restart")
.addEventListener(
    "click",
    function() {

        score = 0;

        lives = 3;

        round = 1;

        running = true;

        multiBalls = [];


        scoreElement.textContent =
            score;


        livesElement.textContent =
            lives;


        roundElement.textContent =
            round;


        createBricks();

        resetMainBall();


        requestAnimationFrame(
            draw
        );

    }
);


/* =====================================
   게임 시작
===================================== */

createBricks();

resetMainBall();

draw();

</script>

</body>
</html>
"""

components.html(
    game,
    height=700,
    scrolling=False
)    background: #181818;
    border: 2px solid #555;
    border-radius: 8px;
    max-width: 100%;
    touch-action: none;
}

.controls {
    margin-top: 10px;
}



.controls button {
    width: 120px;
    height: 50px;
    margin: 5px;
    font-size: 24px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    user-select: none;
    -webkit-user-select: none;
}

#restart {
    width: 160px;
    font-size: 16px;
}

.legend {
    margin-top: 8px;
    font-size: 14px;
}

</style>
</head>

<body>

<div class="info">

점수:
<span id="score">0</span>

&nbsp;&nbsp;

최고기록:
<span id="highScore">0</span>

&nbsp;&nbsp;

❤️
<span id="lives">3</span>

</div>

<canvas
    id="gameCanvas"
    width="640"
    height="500">
</canvas>

<div class="legend">
    ★ = 멀티볼 블록
</div>

<div class="controls">

    <button id="left">◀</button>
    <button id="right">▶</button>

</div>

<br>

<button id="restart">
    다시 시작
</button>

<script>

const canvas =
    document.getElementById("gameCanvas");

const ctx =
    canvas.getContext("2d");

const scoreElement =
    document.getElementById("score");

const highScoreElement =
    document.getElementById("highScore");

const livesElement =
    document.getElementById("lives");

const WIDTH = canvas.width;
const HEIGHT = canvas.height;


/* =========================
   게임 상태
========================= */

let score = 0;
let lives = 3;
let running = true;

let leftPressed = false;
let rightPressed = false;


/* =========================
   최고 기록
========================= */

let highScore =
    Number(
        localStorage.getItem(
            "rockBlockHighScore"
        )
    ) || 0;

highScoreElement.textContent =
    highScore;


/* =========================
   패들
========================= */

const paddle = {

    width: 105,
    height: 12,

    x: WIDTH / 2 - 52,

    /*
    버튼을 누르고 있을 때
    이전보다 훨씬 빠르게 이동
    */

    speed: 14
};


/* =========================
   메인 볼
========================= */

const mainBall = {

    x: WIDTH / 2,

    y: HEIGHT - 65,

    radius: 9,

    dx: 4.5,
    dy: -4.5,

    active: true
};


/* =========================
   멀티볼
========================= */

let multiBalls = [];


/* =========================
   블록 설정
========================= */

const rows = 6;
const columns = 9;

const brickWidth = 62;
const brickHeight = 24;

const brickPadding = 7;

const brickTop = 70;
const brickLeft = 20;

let bricks = [];


/* =========================
   블록 생성
========================= */

function createBricks() {

    bricks = [];

    for (
        let row = 0;
        row < rows;
        row++
    ) {

        bricks[row] = [];

        for (
            let col = 0;
            col < columns;
            col++
        ) {

            /*
            초반에는 낮은 HP 위주

            1 : 매우 많음
            2 : 많음
            3 : 가끔
            4~5 : 없음
            */

            let random =
                Math.random();

            let hp;

            if (random < 0.60) {

                hp = 1;

            } else if (random < 0.90) {

                hp = 2;

            } else {

                hp = 3;
            }


            /*
            멀티볼 블록은 약 10%
            */

            let multi =
                Math.random() < 0.10;


            bricks[row][col] = {

                x: 0,
                y: 0,

                hp: hp,

                alive: true,

                multi: multi
            };
        }
    }
}


/* =========================
   메인볼 초기화
========================= */

function resetMainBall() {

    mainBall.x =
        WIDTH / 2;

    mainBall.y =
        HEIGHT - 65;

    mainBall.dx =
        Math.random() > 0.5
        ? 4.5
        : -4.5;

    mainBall.dy =
        -4.5;

    mainBall.active =
        true;

    paddle.x =
        WIDTH / 2 -
        paddle.width / 2;
}


/* =========================
   멀티볼 생성
========================= */

function createMultiBall() {

    /*
    2개의 멀티볼 생성
    */

    multiBalls.push({

        x: mainBall.x,
        y: mainBall.y,

        radius: 8,

        dx: -5.5,
        dy: -4.5,

        active: true
    });


    multiBalls.push({

        x: mainBall.x,
        y: mainBall.y,

        radius: 8,

        dx: 5.5,
        dy: -4,

        active: true
    });
}


/* =========================
   점수
========================= */

function addScore(amount) {

    score += amount;

    scoreElement.textContent =
        score;


    if (score > highScore) {

        highScore =
            score;

        highScoreElement.textContent =
            highScore;

        localStorage.setItem(
            "rockBlockHighScore",
            highScore
        );
    }
}


/* =========================
   블록 그리기
========================= */

function drawBricks() {

    for (
        let row = 0;
        row < rows;
        row++
    ) {

        for (
            let col = 0;
            col < columns;
            col++
        ) {

            const brick =
                bricks[row][col];

            if (!brick.alive) {
                continue;
            }


            brick.x =
                brickLeft +
                col *
                (brickWidth + brickPadding);

            /*
            맨 위 공간을 크게 확보
            */

            brick.y =
                brickTop +
                row *
                (brickHeight + brickPadding);


            /*
            HP별 블록 색
            */

            if (brick.hp === 3) {

                ctx.fillStyle =
                    "#9b59b6";

            } else if (brick.hp === 2) {

                ctx.fillStyle =
                    "#f39c12";

            } else {

                ctx.fillStyle =
                    "#e74c3c";
            }


            /*
            멀티볼 블록은
            별도 색으로 강조
            */

            if (brick.multi) {

                ctx.fillStyle =
                    "#00a8ff";

            }


            ctx.fillRect(
                brick.x,
                brick.y,
                brickWidth,
                brickHeight
            );


            /*
            숫자
            */

            ctx.fillStyle =
                "white";

            ctx.font =
                "bold 15px Arial";

            ctx.textAlign =
                "center";

            ctx.textBaseline =
                "middle";


            ctx.fillText(

                brick.hp,

                brick.x +
                brickWidth / 2,

                brick.y +
                brickHeight / 2
            );


            /*
            멀티볼 블록 ★
            */

            if (brick.multi) {

                ctx.fillStyle =
                    "#ffff00";

                ctx.font =
                    "bold 14px Arial";

                ctx.fillText(

                    "★",

                    brick.x +
                    brickWidth -
                    9,

                    brick.y + 9
                );
            }
        }
    }
}


/* =========================
   메인볼
========================= */

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
    메인볼 = 밝은 노란색
    */

    ctx.fillStyle =
        "#FFFF00";

    ctx.shadowColor =
        "#FFFF00";

    ctx.shadowBlur =
        14;

    ctx.fill();

    ctx.shadowBlur =
        0;

    ctx.closePath();
}


/* =========================
   멀티볼
========================= */

function drawMultiBalls() {

    for (
        const ball of multiBalls
    ) {

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
        멀티볼 = 하늘색
        */

        ctx.fillStyle =
            "#00BFFF";

        ctx.shadowColor =
            "#00BFFF";

        ctx.shadowBlur =
            8;

        ctx.fill();

        ctx.shadowBlur =
            0;

        ctx.closePath();
    }
}


/* =========================
   패들
========================= */

function drawPaddle() {

    ctx.fillStyle =
        "#4CAF50";

    ctx.fillRect(

        paddle.x,

        HEIGHT - 30,

        paddle.width,

        paddle.height
    );
}


/* =========================
   블록 충돌
========================= */

function hitBrick(ball) {

    for (
        let row = 0;
        row < rows;
        row++
    ) {

        for (
            let col = 0;
            col < columns;
            col++
        ) {

            const brick =
                bricks[row][col];

            if (!brick.alive) {
                continue;
            }


            if (

                ball.x >
                brick.x &&

                ball.x <
                brick.x +
                brickWidth &&

                ball.y >
                brick.y &&

                ball.y <
                brick.y +
                brickHeight

            ) {

                /*
                공이 맞을 때마다
                HP 1 감소
                */

                brick.hp--;

                ball.dy *= -1;


                /*
                블록이 파괴됨
                */

                if (brick.hp <= 0) {

                    brick.alive =
                        false;


                    /*
                    기본 점수
                    */

                    addScore(10);


                    /*
                    멀티볼 블록이었다면
                    멀티볼 생성
                    */

                    if (
                        brick.multi &&
                        ball === mainBall
                    ) {

                        createMultiBall();

                        addScore(20);
                    }
                }

                return;
            }
        }
    }
}


/* =========================
   패들 충돌
========================= */

function checkPaddleCollision(ball) {

    const paddleY =
        HEIGHT - 30;

    if (

        ball.x >= paddle.x &&

        ball.x <=
        paddle.x +
        paddle.width &&

        ball.y +
        ball.radius >=
        paddleY &&

        ball.y -
        ball.radius <=
        paddleY +
        paddle.height &&

        ball.dy > 0

    ) {

        ball.dy =
            -Math.abs(
                ball.dy
            );


        const position =
            (
                ball.x -
                (
                    paddle.x +
                    paddle.width / 2
                )
            )
            /
            (
                paddle.width / 2
            );


        ball.dx =
            position * 7;
    }
}


/* =========================
   메인볼 업데이트
========================= */

function updateMainBall() {

    if (!mainBall.active) {
        return;
    }


    mainBall.x +=
        mainBall.dx;

    mainBall.y +=
        mainBall.dy;


    /*
    좌우 벽
    */

    if (

        mainBall.x +
        mainBall.radius >= WIDTH ||

        mainBall.x -
        mainBall.radius <= 0

    ) {

        mainBall.dx *= -1;
    }


    /*
    위쪽 벽
    */

    if (
        mainBall.y -
        mainBall.radius <= 0
    ) {

        mainBall.dy *= -1;
    }


    checkPaddleCollision(
        mainBall
    );

    hitBrick(
        mainBall
    );


    /*
    ★ 메인볼이 떨어질 때만
    목숨 감소
    */

    if (
        mainBall.y -
        mainBall.radius >
        HEIGHT
    ) {

        lives--;

        livesElement.textContent =
            lives;


        if (lives <= 0) {

            mainBall.active =
                false;

            running = false;

        } else {

            resetMainBall();
        }
    }
}


/* =========================
   멀티볼 업데이트
========================= */

function updateMultiBalls() {

    for (
        const ball of multiBalls
    ) {

        if (!ball.active) {
            continue;
        }


        ball.x +=
            ball.dx;

        ball.y +=
            ball.dy;


        /*
        좌우 벽
        */

        if (

            ball.x +
            ball.radius >= WIDTH ||

            ball.x -
            ball.radius <= 0

        ) {

            ball.dx *= -1;
        }


        /*
        위쪽 벽
        */

        if (
            ball.y -
            ball.radius <= 0
        ) {

            ball.dy *= -1;
        }


        checkPaddleCollision(
            ball
        );

        hitBrick(
            ball
        );


        /*
        멀티볼은 떨어져도
        목숨 감소 없음
        */

        if (
            ball.y -
            ball.radius >
            HEIGHT
        ) {

            ball.active =
                false;
        }
    }


    multiBalls =
        multiBalls.filter(
            ball =>
                ball.active
        );
}


/* =========================
   게임 업데이트
========================= */

function update() {

    if (!running) {
        return;
    }


    /*
    패들 이동

    speed = 14라서
    버튼을 누르면 빠르게 이동
    */

    if (leftPressed) {

        paddle.x -=
            paddle.speed;
    }

    if (rightPressed) {

        paddle.x +=
            paddle.speed;
    }


    if (paddle.x < 0) {

        paddle.x = 0;
    }


    if (
        paddle.x +
        paddle.width >
        WIDTH
    ) {

        paddle.x =
            WIDTH -
            paddle.width;
    }


    updateMainBall();

    updateMultiBalls();


    /*
    모든 블록 파괴
    */

    let remaining = 0;

    for (
        let row = 0;
        row < rows;
        row++
    ) {

        for (
            let col = 0;
            col < columns;
            col++
        ) {

            if (
                bricks[row][col].alive
            ) {

                remaining++;
            }
        }
    }


    if (remaining === 0) {

        running = false;
    }
}


/* =========================
   그리기
========================= */

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


    if (!running) {

        ctx.fillStyle =
            "rgba(0,0,0,0.75)";

        ctx.fillRect(
            0,
            0,
            WIDTH,
            HEIGHT
        );


        ctx.fillStyle =
            "white";

        ctx.textAlign =
            "center";

        ctx.font =
            "bold 32px Arial";


        if (lives <= 0) {

            ctx.fillText(
                "GAME OVER",
                WIDTH / 2,
                HEIGHT / 2
            );

        } else {

            ctx.fillText(
                "YOU WIN!",
                WIDTH / 2,
                HEIGHT / 2
            );
        }


        ctx.font =
            "18px Arial";


        ctx.fillText(

            "점수: " + score,

            WIDTH / 2,

            HEIGHT / 2 + 40
        );


        return;
    }


    update();

    requestAnimationFrame(
        draw
    );
}


/* =========================
   키보드
========================= */

document.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key ===
            "ArrowLeft"
        ) {

            leftPressed = true;
        }


        if (
            event.key ===
            "ArrowRight"
        ) {

            rightPressed = true;
        }
    }
);


document.addEventListener(
    "keyup",
    function(event) {

        if (
            event.key ===
            "ArrowLeft"
        ) {

            leftPressed = false;
        }


        if (
            event.key ===
            "ArrowRight"
        ) {

            rightPressed = false;
        }
    }
);


/* =========================
   버튼 조작
========================= */

const leftButton =
    document.getElementById("left");

const rightButton =
    document.getElementById("right");


/*
마우스
*/

leftButton.addEventListener(
    "mousedown",
    function() {

        leftPressed = true;
    }
);

leftButton.addEventListener(
    "mouseup",
    function() {

        leftPressed = false;
    }
);


rightButton.addEventListener(
    "mousedown",
    function() {

        rightPressed = true;
    }
);

rightButton.addEventListener(
    "mouseup",
    function() {

        rightPressed = false;
    }
);


/*
터치
*/

leftButton.addEventListener(
    "touchstart",
    function(event) {

        event.preventDefault();

        leftPressed = true;
    }
);


leftButton.addEventListener(
    "touchend",
    function(event) {

        event.preventDefault();

        leftPressed = false;
    }
);


rightButton.addEventListener(
    "touchstart",
    function(event) {

        event.preventDefault();

        rightPressed = true;
    }
);


rightButton.addEventListener(
    "touchend",
    function(event) {

        event.preventDefault();

        rightPressed = false;
    }
);


/* =========================
   다시 시작
========================= */

document
    .getElementById("restart")
    .addEventListener(
        "click",
        function() {

            score = 0;

            lives = 3;

            running = true;

            multiBalls = [];


            scoreElement.textContent =
                score;

            livesElement.textContent =
                lives;


            createBricks();

            resetMainBall();


            requestAnimationFrame(
                draw
            );
        }
    );


/* =========================
   시작
========================= */

createBricks();

resetMainBall();

draw();

</script>

</body>
</html>
"""

components.html(
    game,
    height=690,
    scrolling=False
)

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Rock Block",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 Rock Block")
st.caption("← → 키 또는 버튼으로 패들을 움직이세요. ★ 블록은 멀티볼 블록입니다.")

game = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>

body {
    margin: 0;
    background: #101010;
    color: white;
    font-family: Arial, sans-serif;
    text-align: center;
}

.info {
    font-size: 18px;
    margin-bottom: 8px;
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

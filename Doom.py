import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="DOOM Mobile",
    page_icon="👾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    header, footer, #MainMenu {
        display: none !important;
    }

    iframe {
        border: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

game_html = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width,
             initial-scale=1,
             maximum-scale=1,
             user-scalable=no"
>

<style>
* {
    box-sizing: border-box;
    -webkit-tap-highlight-color: transparent;
}

html, body {
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: #050505;
    color: white;
    font-family: Arial, sans-serif;
    touch-action: none;
    user-select: none;
}

#game {
    position: relative;
    width: 100%;
    height: 92vh;
    min-height: 520px;
    overflow: hidden;
    background: black;
}

canvas {
    display: block;
    width: 100%;
    height: 100%;
    image-rendering: pixelated;
    touch-action: none;
}

/* 시작 화면 */

#startScreen {
    position: absolute;
    inset: 0;
    z-index: 30;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    background:
        radial-gradient(
            circle,
            #641d10 0%,
            #190705 48%,
            #020202 85%
        );
}

#startScreen h1 {
    margin: 0 0 12px;
    color: #ef4428;
    font-family: Impact, sans-serif;
    font-size: clamp(46px, 12vw, 84px);
    letter-spacing: 4px;
    text-shadow: 0 5px 0 #690e08;
}

#startButton {
    padding: 15px 36px;
    color: white;
    font-size: 20px;
    font-weight: bold;
    background: #b72c19;
    border: 2px solid #ff8468;
    border-radius: 10px;
}

.guide {
    margin: 14px 15px;
    color: #e1d0bc;
    font-size: 14px;
    line-height: 1.65;
}

/* 모바일 조작 버튼 */

#mobileControls {
    position: absolute;
    inset: 0;
    z-index: 20;
    pointer-events: none;
}

.movePad,
.actionPad {
    position: absolute;
    bottom: 72px;
    pointer-events: auto;
}

.movePad {
    left: 12px;
    width: 156px;
    height: 156px;
}

.actionPad {
    right: 12px;
    width: 215px;
    height: 156px;
}

.controlButton {
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;

    width: 55px;
    height: 55px;

    color: white;
    font-size: 24px;
    font-weight: bold;

    background: rgba(25, 20, 18, 0.72);
    border: 2px solid rgba(255, 255, 255, 0.48);
    border-radius: 50%;

    touch-action: none;
}

.controlButton.active {
    background: rgba(220, 55, 28, 0.95);
    transform: scale(0.94);
}

#forward {
    top: 0;
    left: 51px;
}

#backward {
    bottom: 0;
    left: 51px;
}

#strafeLeft {
    top: 51px;
    left: 0;
}

#strafeRight {
    top: 51px;
    right: 0;
}

#turnLeft {
    bottom: 10px;
    left: 0;
}

#turnRight {
    bottom: 10px;
    left: 62px;
}

#fire {
    top: 0;
    right: 0;
    width: 84px;
    height: 84px;
    font-size: 16px;
    background: rgba(186, 39, 23, 0.84);
}

#reload {
    right: 5px;
    bottom: 0;
    width: 68px;
    height: 44px;
    font-size: 12px;
    border-radius: 18px;
}

/* 세로 화면 */

@media (orientation: portrait) {
    #game {
        height: 74vh;
        min-height: 540px;
    }

    .movePad,
    .actionPad {
        bottom: 66px;
        transform: scale(0.88);
    }

    .movePad {
        transform-origin: left bottom;
    }

    .actionPad {
        transform-origin: right bottom;
    }
}
</style>
</head>

<body>

<div id="game">

    <canvas id="canvas" width="960" height="600"></canvas>

    <div id="startScreen">
        <div>
            <h1>DOOM-LITE</h1>

            <div class="guide">
                왼쪽 패드: 이동<br>
                오른쪽 화살표: 회전<br>
                FIRE: 발사 / RELOAD: 재장전<br>
                화면 좌우 드래그: 시점 조준<br>
                가로 화면 권장
            </div>

            <button id="startButton">임무 시작</button>
        </div>
    </div>

    <div id="mobileControls">

        <div class="movePad">
            <div class="controlButton" id="forward">▲</div>
            <div class="controlButton" id="backward">▼</div>
            <div class="controlButton" id="strafeLeft">◀</div>
            <div class="controlButton" id="strafeRight">▶</div>
        </div>

        <div class="actionPad">
            <div class="controlButton" id="turnLeft">↶</div>
            <div class="controlButton" id="turnRight">↷</div>
            <div class="controlButton" id="fire">FIRE</div>
            <div class="controlButton" id="reload">RELOAD</div>
        </div>

    </div>

</div>

<script>
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const WIDTH = canvas.width;
const HEIGHT = canvas.height;

/*
0 = 빈 공간
1 = 갈색 벽
2 = 녹색 벽
3 = 보라색 벽
*/

const gameMap = [
    "1111111111111111",
    "1000000000000001",
    "1000000100003001",
    "1000000100000001",
    "1000111101110001",
    "1000000001000001",
    "1030000001000201",
    "1000110001000001",
    "1000010000000001",
    "1000010111100001",
    "1000000100000001",
    "1020000000000001",
    "1000001110000001",
    "1000000000000001",
    "1000300000000001",
    "1111111111111111"
];

const wallColors = [
    "",
    "#7e3024",
    "#4b6451",
    "#68517e"
];

let player;
let enemies;
let controls = {};

let muzzleFlash = 0;
let playing = false;
let lastFrame = 0;

/* 게임 초기화 */

function resetGame() {
    /*
    기존 오류 수정:
    플레이어를 벽이 없는 2.5, 1.5 위치에 배치
    */

    player = {
        x: 2.5,
        y: 1.5,
        angle: 0,
        health: 100,
        ammo: 12,
        score: 0
    };

    /*
    첫 번째 적은 시작 직후 정면에서 보임
    */

    enemies = [
        {
            x: 7.5,
            y: 1.5,
            health: 2
        },
        {
            x: 12.5,
            y: 3.5,
            health: 2
        },
        {
            x: 3.5,
            y: 6.5,
            health: 2
        },
        {
            x: 10.5,
            y: 8.5,
            health: 2
        },
        {
            x: 13.5,
            y: 13.5,
            health: 2
        }
    ];

    controls = {};
    playing = true;
}

/* 벽 판정 */

function isWall(x, y) {
    const mapX = Math.floor(x);
    const mapY = Math.floor(y);

    if (
        mapY < 0 ||
        mapY >= gameMap.length ||
        mapX < 0 ||
        mapX >= gameMap[0].length
    ) {
        return true;
    }

    return Number(gameMap[mapY][mapX]) > 0;
}

/* 광선 추적 */

function castRay(angle) {
    const rayCos = Math.cos(angle);
    const raySin = Math.sin(angle);

    let distance = 0;

    while (distance < 20) {
        distance += 0.025;

        const rayX =
            player.x + rayCos * distance;

        const rayY =
            player.y + raySin * distance;

        if (isWall(rayX, rayY)) {
            return {
                distance: distance,
                type: Number(
                    gameMap[Math.floor(rayY)][Math.floor(rayX)]
                )
            };
        }
    }

    return {
        distance: 20,
        type: 1
    };
}

/* 총 발사 */

function shoot() {
    if (
        !playing ||
        player.ammo <= 0
    ) {
        return;
    }

    player.ammo -= 1;
    muzzleFlash = 5;

    let selectedEnemy = null;
    let smallestAngle = 0.15;

    for (const enemy of enemies) {
        const dx = enemy.x - player.x;
        const dy = enemy.y - player.y;

        const distance =
            Math.hypot(dx, dy);

        let angleDifference =
            Math.atan2(dy, dx) - player.angle;

        angleDifference = Math.atan2(
            Math.sin(angleDifference),
            Math.cos(angleDifference)
        );

        const wallDistance =
            castRay(
                player.angle + angleDifference
            ).distance;

        if (
            Math.abs(angleDifference) < smallestAngle &&
            distance < wallDistance
        ) {
            selectedEnemy = enemy;
            smallestAngle =
                Math.abs(angleDifference);
        }
    }

    if (selectedEnemy !== null) {
        selectedEnemy.health -= 1;
        player.score += 50;

        if (selectedEnemy.health <= 0) {
            const index =
                enemies.indexOf(selectedEnemy);

            enemies.splice(index, 1);
            player.score += 150;
        }
    }
}

/* 게임 상태 갱신 */

function update(deltaTime) {
    if (!playing) {
        return;
    }

    const moveSpeed =
        2.25 * deltaTime;

    const turnSpeed =
        2.15 * deltaTime;

    if (controls.turnLeft) {
        player.angle -= turnSpeed;
    }

    if (controls.turnRight) {
        player.angle += turnSpeed;
    }

    let moveX = 0;
    let moveY = 0;

    if (controls.forward) {
        moveX +=
            Math.cos(player.angle) *
            moveSpeed;

        moveY +=
            Math.sin(player.angle) *
            moveSpeed;
    }

    if (controls.backward) {
        moveX -=
            Math.cos(player.angle) *
            moveSpeed;

        moveY -=
            Math.sin(player.angle) *
            moveSpeed;
    }

    if (controls.strafeLeft) {
        moveX +=
            Math.cos(
                player.angle -
                Math.PI / 2
            ) * moveSpeed;

        moveY +=
            Math.sin(
                player.angle -
                Math.PI / 2
            ) * moveSpeed;
    }

    if (controls.strafeRight) {
        moveX +=
            Math.cos(
                player.angle +
                Math.PI / 2
            ) * moveSpeed;

        moveY +=
            Math.sin(
                player.angle +
                Math.PI / 2
            ) * moveSpeed;
    }

    const playerRadius = 0.18;

    if (
        !isWall(
            player.x + moveX +
            Math.sign(moveX) * playerRadius,
            player.y
        )
    ) {
        player.x += moveX;
    }

    if (
        !isWall(
            player.x,
            player.y + moveY +
            Math.sign(moveY) * playerRadius
        )
    ) {
        player.y += moveY;
    }

    /* 적 이동 및 공격 */

    for (const enemy of enemies) {
        const dx =
            player.x - enemy.x;

        const dy =
            player.y - enemy.y;

        const distance =
            Math.hypot(dx, dy);

        if (distance < 0.68) {
            player.health -=
                17 * deltaTime;
        } else if (distance < 7) {
            const enemySpeed =
                0.43 * deltaTime;

            const nextX =
                enemy.x +
                dx / distance *
                enemySpeed;

            const nextY =
                enemy.y +
                dy / distance *
                enemySpeed;

            if (!isWall(nextX, enemy.y)) {
                enemy.x = nextX;
            }

            if (!isWall(enemy.x, nextY)) {
                enemy.y = nextY;
            }
        }
    }

    if (player.health <= 0) {
        player.health = 0;
        playing = false;
    }

    if (enemies.length === 0) {
        playing = false;
    }
}

/* 배경과 벽 렌더링 */

function drawWorld() {
    const skyGradient =
        ctx.createLinearGradient(
            0,
            0,
            0,
            HEIGHT / 2
        );

    skyGradient.addColorStop(
        0,
        "#210b0a"
    );

    skyGradient.addColorStop(
        1,
        "#6b251a"
    );

    ctx.fillStyle = skyGradient;
    ctx.fillRect(
        0,
        0,
        WIDTH,
        HEIGHT / 2
    );

    const floorGradient =
        ctx.createLinearGradient(
            0,
            HEIGHT / 2,
            0,
            HEIGHT
        );

    floorGradient.addColorStop(
        0,
        "#332a23"
    );

    floorGradient.addColorStop(
        1,
        "#080706"
    );

    ctx.fillStyle = floorGradient;
    ctx.fillRect(
        0,
        HEIGHT / 2,
        WIDTH,
        HEIGHT / 2
    );

    const fieldOfView =
        Math.PI / 3;

    const depthBuffer = [];

    for (
        let column = 0;
        column < WIDTH;
        column += 2
    ) {
        const rayAngle =
            player.angle -
            fieldOfView / 2 +
            fieldOfView *
            column / WIDTH;

        const ray =
            castRay(rayAngle);

        const correctedDistance =
            ray.distance *
            Math.cos(
                rayAngle -
                player.angle
            );

        depthBuffer[column / 2] =
            correctedDistance;

        const wallHeight =
            Math.min(
                HEIGHT,
                HEIGHT /
                Math.max(
                    correctedDistance,
                    0.001
                )
            );

        const brightness =
            Math.max(
                0.22,
                1 -
                correctedDistance / 14
            );

        ctx.fillStyle =
            wallColors[ray.type] ||
            wallColors[1];

        ctx.globalAlpha =
            brightness;

        ctx.fillRect(
            column,
            HEIGHT / 2 -
            wallHeight / 2,
            2,
            wallHeight
        );

        ctx.globalAlpha = 1;
    }

    drawEnemies(
        depthBuffer,
        fieldOfView
    );
}

/* 적 렌더링 */

function drawEnemies(
    depthBuffer,
    fieldOfView
) {
    const visibleEnemies =
        enemies
        .map(enemy => {
            return {
                enemy: enemy,
                distance: Math.hypot(
                    enemy.x - player.x,
                    enemy.y - player.y
                ),
                angle: Math.atan2(
                    enemy.y - player.y,
                    enemy.x - player.x
                )
            };
        })
        .sort(
            (a, b) =>
                b.distance -
                a.distance
        );

    for (const data of visibleEnemies) {
        let angleDifference =
            data.angle -
            player.angle;

        angleDifference =
            Math.atan2(
                Math.sin(angleDifference),
                Math.cos(angleDifference)
            );

        if (
            Math.abs(angleDifference) >
            fieldOfView * 0.65
        ) {
            continue;
        }

        const screenX =
            WIDTH / 2 +
            angleDifference /
            fieldOfView *
            WIDTH;

        const size =
            Math.min(
                280,
                340 /
                Math.max(
                    data.distance,
                    0.2
                )
            );

        const depthIndex =
            Math.max(
                0,
                Math.min(
                    depthBuffer.length - 1,
                    Math.floor(
                        screenX / 2
                    )
                )
            );

        if (
            data.distance >
            depthBuffer[depthIndex] +
            0.25
        ) {
            continue;
        }

        const enemyX =
            screenX;

        const enemyY =
            HEIGHT / 2 -
            size * 0.13;

        /* 그림자 */

        ctx.fillStyle =
            "rgba(0,0,0,0.45)";

        ctx.beginPath();
        ctx.ellipse(
            enemyX,
            HEIGHT / 2 +
            size * 0.42,
            size * 0.34,
            size * 0.10,
            0,
            0,
            Math.PI * 2
        );
        ctx.fill();

        /* 몸통 */

        ctx.fillStyle = "#4a0c08";

        ctx.fillRect(
            enemyX - size * 0.25,
            enemyY - size * 0.05,
            size * 0.50,
            size * 0.65
        );

        /* 양팔 */

        ctx.fillStyle = "#8f1f15";

        ctx.fillRect(
            enemyX - size * 0.39,
            enemyY,
            size * 0.16,
            size * 0.52
        );

        ctx.fillRect(
            enemyX + size * 0.23,
            enemyY,
            size * 0.16,
            size * 0.52
        );

        /* 머리 */

        ctx.fillStyle = "#d63c25";

        ctx.beginPath();
        ctx.arc(
            enemyX,
            enemyY - size * 0.14,
            size * 0.24,
            0,
            Math.PI * 2
        );
        ctx.fill();

        /* 뿔 */

        ctx.fillStyle = "#e7c794";

        ctx.beginPath();
        ctx.moveTo(
            enemyX - size * 0.19,
            enemyY - size * 0.29
        );

        ctx.lineTo(
            enemyX - size * 0.32,
            enemyY - size * 0.48
        );

        ctx.lineTo(
            enemyX - size * 0.08,
            enemyY - size * 0.32
        );

        ctx.fill();

        ctx.beginPath();
        ctx.moveTo(
            enemyX + size * 0.19,
            enemyY - size * 0.29
        );

        ctx.lineTo(
            enemyX + size * 0.32,
            enemyY - size * 0.48
        );

        ctx.lineTo(
            enemyX + size * 0.08,
            enemyY - size * 0.32
        );

        ctx.fill();

        /* 눈 */

        ctx.fillStyle = "#fff25e";

        ctx.fillRect(
            enemyX - size * 0.13,
            enemyY - size * 0.20,
            size * 0.08,
            size * 0.06
        );

        ctx.fillRect(
            enemyX + size * 0.05,
            enemyY - size * 0.20,
            size * 0.08,
            size * 0.06
        );

        /* 체력 표시 */

        ctx.fillStyle =
            "rgba(0,0,0,0.7)";

        ctx.fillRect(
            enemyX - size * 0.25,
            enemyY - size * 0.55,
            size * 0.50,
            6
        );

        ctx.fillStyle = "#ff3b25";

        ctx.fillRect(
            enemyX - size * 0.25,
            enemyY - size * 0.55,
            size * 0.25 *
            data.enemy.health,
            6
        );
    }
}

/* 무기 */

function drawWeapon() {
    ctx.fillStyle = "#332b28";

    ctx.fillRect(
        WIDTH / 2 - 58,
        HEIGHT - 122,
        116,
        122
    );

    ctx.fillStyle = "#151515";

    ctx.fillRect(
        WIDTH / 2 - 20,
        HEIGHT - 190,
        40,
        105
    );

    if (muzzleFlash > 0) {
        ctx.fillStyle = "#ffd85a";

        ctx.beginPath();

        ctx.arc(
            WIDTH / 2,
            HEIGHT - 195,
            36,
            0,
            Math.PI * 2
        );

        ctx.fill();

        muzzleFlash -= 1;
    }
}

/* 조준점 */

function drawCrosshair() {
    ctx.strokeStyle = "white";
    ctx.lineWidth = 2;

    ctx.beginPath();

    ctx.moveTo(
        WIDTH / 2 - 12,
        HEIGHT / 2
    );

    ctx.lineTo(
        WIDTH / 2 + 12,
        HEIGHT / 2
    );

    ctx.moveTo(
        WIDTH / 2,
        HEIGHT / 2 - 12
    );

    ctx.lineTo(
        WIDTH / 2,
        HEIGHT / 2 + 12
    );

    ctx.stroke();
}

/* 상태창 */

function drawHud() {
    ctx.fillStyle =
        "rgba(0,0,0,0.80)";

    ctx.fillRect(
        0,
        HEIGHT - 62,
        WIDTH,
        62
    );

    ctx.font =
        "bold 23px monospace";

    ctx.fillStyle =
        player.health < 30
        ? "#ff3322"
        : "#ffb23d";

    ctx.fillText(
        "HP " +
        Math.ceil(player.health),
        20,
        HEIGHT - 24
    );

    ctx.fillStyle = "#eeeeee";

    ctx.fillText(
        "AMMO " +
        player.ammo +
        "/12",
        WIDTH / 2 - 76,
        HEIGHT - 24
    );

    ctx.fillStyle = "#ffb23d";

    ctx.fillText(
        "ENEMY " +
        enemies.length,
        WIDTH - 330,
        HEIGHT - 24
    );

    ctx.fillText(
        "SCORE " +
        player.score,
        WIDTH - 175,
        HEIGHT - 24
    );
}

/* 종료 화면 */

function drawEndScreen() {
    if (playing) {
        return;
    }

    ctx.fillStyle =
        "rgba(0,0,0,0.76)";

    ctx.fillRect(
        0,
        0,
        WIDTH,
        HEIGHT
    );

    ctx.textAlign = "center";
    ctx.font = "bold 55px Impact";

    if (enemies.length === 0) {
        ctx.fillStyle = "#f5b82e";

        ctx.fillText(
            "MISSION COMPLETE",
            WIDTH / 2,
            HEIGHT / 2 - 20
        );
    } else {
        ctx.fillStyle = "#e43b25";

        ctx.fillText(
            "MISSION FAILED",
            WIDTH / 2,
            HEIGHT / 2 - 20
        );
    }

    ctx.font = "20px Arial";
    ctx.fillStyle = "white";

    ctx.fillText(
        "화면을 두 번 눌러 다시 시작",
        WIDTH / 2,
        HEIGHT / 2 + 35
    );

    ctx.textAlign = "left";
}

/* 전체 화면 렌더링 */

function render() {
    drawWorld();
    drawWeapon();
    drawCrosshair();
    drawHud();
    drawEndScreen();
}

/* 게임 반복 */

function gameLoop(timestamp) {
    const deltaTime =
        Math.min(
            0.04,
            (timestamp - lastFrame) /
            1000 || 0
        );

    lastFrame = timestamp;

    update(deltaTime);
    render();

    requestAnimationFrame(gameLoop);
}

/* 시작 버튼 */

document
    .getElementById("startButton")
    .addEventListener(
        "click",
        function () {
            document
                .getElementById(
                    "startScreen"
                )
                .style.display = "none";

            resetGame();
        }
    );

/* 터치 버튼 연결 */

function bindHoldButton(
    elementId,
    controlName
) {
    const element =
        document.getElementById(
            elementId
        );

    function activate(event) {
        event.preventDefault();

        controls[controlName] = true;

        element.classList.add(
            "active"
        );
    }

    function deactivate(event) {
        event.preventDefault();

        controls[controlName] = false;

        element.classList.remove(
            "active"
        );
    }

    element.addEventListener(
        "pointerdown",
        activate
    );

    element.addEventListener(
        "pointerup",
        deactivate
    );

    element.addEventListener(
        "pointercancel",
        deactivate
    );

    element.addEventListener(
        "pointerleave",
        deactivate
    );
}

bindHoldButton(
    "forward",
    "forward"
);

bindHoldButton(
    "backward",
    "backward"
);

bindHoldButton(
    "strafeLeft",
    "strafeLeft"
);

bindHoldButton(
    "strafeRight",
    "strafeRight"
);

bindHoldButton(
    "turnLeft",
    "turnLeft"
);

bindHoldButton(
    "turnRight",
    "turnRight"
);

/* 발사 */

const fireButton =
    document.getElementById("fire");

fireButton.addEventListener(
    "pointerdown",
    function (event) {
        event.preventDefault();

        fireButton.classList.add(
            "active"
        );

        shoot();
    }
);

fireButton.addEventListener(
    "pointerup",
    function (event) {
        event.preventDefault();

        fireButton.classList.remove(
            "active"
        );
    }
);

/* 재장전 */

const reloadButton =
    document.getElementById(
        "reload"
    );

reloadButton.addEventListener(
    "pointerdown",
    function (event) {
        event.preventDefault();

        if (player) {
            player.ammo = 12;
        }

        reloadButton.classList.add(
            "active"
        );
    }
);

reloadButton.addEventListener(
    "pointerup",
    function (event) {
        event.preventDefault();

        reloadButton.classList.remove(
            "active"
        );
    }
);

/* 화면 드래그로 회전 */

let previousTouchX = null;

canvas.addEventListener(
    "pointerdown",
    function (event) {
        if (
            event.pointerType ===
            "touch"
        ) {
            previousTouchX =
                event.clientX;

            canvas.setPointerCapture(
                event.pointerId
            );
        }
    }
);

canvas.addEventListener(
    "pointermove",
    function (event) {
        if (
            event.pointerType ===
            "touch" &&
            previousTouchX !== null
        ) {
            const movement =
                event.clientX -
                previousTouchX;

            player.angle +=
                movement * 0.006;

            previousTouchX =
                event.clientX;
        }
    }
);

canvas.addEventListener(
    "pointerup",
    function (event) {
        if (
            event.pointerType ===
            "touch"
        ) {
            previousTouchX = null;
        }
    }
);

/* 게임 재시작 */

canvas.addEventListener(
    "dblclick",
    function () {
        if (!playing) {
            resetGame();
        }
    }
);

/* PC 키보드 지원 */

window.addEventListener(
    "keydown",
    function (event) {
        if (event.code === "KeyW") {
            controls.forward = true;
        }

        if (event.code === "KeyS") {
            controls.backward = true;
        }

        if (event.code === "KeyA") {
            controls.strafeLeft = true;
        }

        if (event.code === "KeyD") {
            controls.strafeRight = true;
        }

        if (
            event.code ===
            "ArrowLeft"
        ) {
            controls.turnLeft = true;
        }

        if (
            event.code ===
            "ArrowRight"
        ) {
            controls.turnRight = true;
        }

        if (
            event.code === "Space"
        ) {
            event.preventDefault();
            shoot();
        }

        if (
            event.code === "KeyR"
        ) {
            player.ammo = 12;
        }
    }
);

window.addEventListener(
    "keyup",
    function (event) {
        if (event.code === "KeyW") {
            controls.forward = false;
        }

        if (event.code === "KeyS") {
            controls.backward = false;
        }

        if (event.code === "KeyA") {
            controls.strafeLeft = false;
        }

        if (event.code === "KeyD") {
            controls.strafeRight = false;
        }

        if (
            event.code ===
            "ArrowLeft"
        ) {
            controls.turnLeft = false;
        }

        if (
            event.code ===
            "ArrowRight"
        ) {
            controls.turnRight = false;
        }
    }
);

/* 최초 실행 */

resetGame();
requestAnimationFrame(gameLoop);
</script>

</body>
</html>
"""

components.html(
    game_html,
    height=720,
    scrolling=False,
)

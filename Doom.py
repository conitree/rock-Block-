import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="DOOM Mobile",
    page_icon="👾",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        padding: 0;
        max-width: 100%;
    }

    header, footer, #MainMenu {
        visibility: hidden;
    }

    iframe {
        border: none;
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
    content="width=device-width, initial-scale=1,
             maximum-scale=1, user-scalable=no"
>

<style>
* {
    box-sizing: border-box;
    -webkit-tap-highlight-color: transparent;
}

html, body {
    margin: 0;
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
    z-index: 20;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    background:
        radial-gradient(circle, #611b0e 0%, #180705 45%, #020202 85%);
}

#startScreen h1 {
    margin: 0 0 12px;
    color: #ef4428;
    font-size: clamp(45px, 12vw, 82px);
    font-family: Impact, sans-serif;
    letter-spacing: 4px;
    text-shadow: 0 5px 0 #690e08;
}

#startButton {
    padding: 15px 35px;
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
    line-height: 1.6;
}

/* 모바일 조작 버튼 */
#mobileControls {
    position: absolute;
    inset: 0;
    z-index: 10;
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
    border: 2px solid rgba(255, 255, 255, 0.5);
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
    background: rgba(186, 39, 23, 0.82);
}

#reload {
    right: 5px;
    bottom: 0;
    width: 67px;
    height: 44px;
    font-size: 12px;
    border-radius: 18px;
}

/* 세로 화면 대응 */
@media (orientation: portrait) {
    #game {
        height: 75vh;
        min-height: 540px;
    }

    .movePad,
    .actionPad {
        transform: scale(0.88);
        bottom: 66px;
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
                왼쪽 방향 패드로 이동<br>
                오른쪽 버튼으로 회전·발사<br>
                게임 화면을 좌우로 밀어서 조준<br>
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

/* 0은 빈 공간, 1~3은 벽 */
const gameMap = [
    "1111111111111111",
    "1000000000000001",
    "1020000100003001",
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
let paused = false;
let lastFrame = 0;

function resetGame() {
    player = {
        x: 2.5,
        y: 2.5,
        angle: 0,
        health: 100,
        ammo: 12,
        score: 0
    };

    enemies = [
        {x: 11.5, y: 2.5, health: 2},
        {x: 13.5, y: 7.5, health: 2},
        {x: 3.5, y: 13.5, health: 2},
        {x: 9.5, y: 11.5, health: 2},
        {x: 12.5, y: 14.5, health: 2}
    ];

    playing = true;
    paused = false;
}

function isWall(x, y) {
    const row = gameMap[Math.floor(y)];
    const cell = row?.[Math.floor(x)];

    return !cell || Number(cell) > 0;
}

/* 광선을 발사하여 벽까지의 거리 계산 */
function castRay(angle) {
    const cos = Math.cos(angle);
    const sin = Math.sin(angle);

    let distance = 0;

    while (distance < 20) {
        distance += 0.025;

        const rayX = player.x + cos * distance;
        const rayY = player.y + sin * distance;

        if (isWall(rayX, rayY)) {
            return {
                distance,
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

function shoot() {
    if (!playing || paused || player.ammo <= 0) {
        return;
    }

    player.ammo -= 1;
    muzzleFlash = 5;

    let selectedEnemy = null;
    let smallestAngle = 0.14;

    for (const enemy of enemies) {
        const dx = enemy.x - player.x;
        const dy = enemy.y - player.y;

        const distance = Math.hypot(dx, dy);

        let angleDifference =
            Math.atan2(dy, dx) - player.angle;

        angleDifference = Math.atan2(
            Math.sin(angleDifference),
            Math.cos(angleDifference)
        );

        const wallDistance =
            castRay(player.angle + angleDifference).distance;

        if (
            Math.abs(angleDifference) < smallestAngle &&
            distance < wallDistance
        ) {
            selectedEnemy = enemy;
            smallestAngle = Math.abs(angleDifference);
        }
    }

    if (selectedEnemy) {
        selectedEnemy.health -= 1;
        player.score += 50;

        if (selectedEnemy.health <= 0) {
            enemies.splice(enemies.indexOf(selectedEnemy), 1);
            player.score += 150;
        }
    }
}

function update(deltaTime) {
    if (!playing || paused) {
        return;
    }

    const moveSpeed = 2.2 * deltaTime;
    const turnSpeed = 2.1 * deltaTime;

    if (controls.turnLeft) {
        player.angle -= turnSpeed;
    }

    if (controls.turnRight) {
        player.angle += turnSpeed;
    }

    let moveX = 0;
    let moveY = 0;

    if (controls.forward) {
        moveX += Math.cos(player.angle) * moveSpeed;
        moveY += Math.sin(player.angle) * moveSpeed;
    }

    if (controls.backward) {
        moveX -= Math.cos(player.angle) * moveSpeed;
        moveY -= Math.sin(player.angle) * moveSpeed;
    }

    if (controls.strafeLeft) {
        moveX += Math.cos(player.angle - Math.PI / 2) * moveSpeed;
        moveY += Math.sin(player.angle - Math.PI / 2) * moveSpeed;
    }

    if (controls.strafeRight) {
        moveX += Math.cos(player.angle + Math.PI / 2) * moveSpeed;
        moveY += Math.sin(player.angle + Math.PI / 2) * moveSpeed;
    }

    if (!isWall(player.x + moveX, player.y)) {
        player.x += moveX;
    }

    if (!isWall(player.x, player.y + moveY)) {
        player.y += moveY;
    }

    /* 적 이동 및 공격 */
    for (const enemy of enemies) {
        const dx = player.x - enemy.x;
        const dy = player.y - enemy.y;
        const distance = Math.hypot(dx, dy);

        if (distance < 0.7) {
            player.health -= 18 * deltaTime;
        } else if (distance < 7) {
            const enemySpeed = 0.45 * deltaTime;

            const nextX =
                enemy.x + (dx / distance) * enemySpeed;

            const nextY =
                enemy.y + (dy / distance) * enemySpeed;

            if (!isWall(nextX, enemy.y)) {
                enemy.x = nextX;
            }

            if (!isWall(enemy.x, nextY)) {
                enemy.y = nextY;
            }
        }
    }

    if (player.health <= 0 || enemies.length === 0) {
        playing = false;
    }
}

function drawWorld() {
    /* 하늘 */
    const sky = ctx.createLinearGradient(
        0, 0, 0, HEIGHT / 2
    );

    sky.addColorStop(0, "#210b0a");
    sky.addColorStop(1, "#6b251a");

    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, WIDTH, HEIGHT / 2);

    /* 바닥 */
    const floor = ctx.createLinearGradient(
        0, HEIGHT / 2, 0, HEIGHT
    );

    floor.addColorStop(0, "#332a23");
    floor.addColorStop(1, "#080706");

    ctx.fillStyle = floor;
    ctx.fillRect(0, HEIGHT / 2, WIDTH, HEIGHT / 2);

    const fieldOfView = Math.PI / 3;
    const depthBuffer = [];

    /* 벽 그리기 */
    for (let column = 0; column < WIDTH; column += 2) {
        const rayAngle =
            player.angle -
            fieldOfView / 2 +
            fieldOfView * column / WIDTH;

        const ray = castRay(rayAngle);

        const correctedDistance =
            ray.distance *
            Math.cos(rayAngle - player.angle);

        depthBuffer[column / 2] = correctedDistance;

        const wallHeight = Math.min(
            HEIGHT,
            HEIGHT / correctedDistance
        );

        const brightness = Math.max(
            0.22,
            1 - correctedDistance / 14
        );

        ctx.fillStyle =
            wallColors[ray.type] || wallColors[1];

        ctx.globalAlpha = brightness;

        ctx.fillRect(
            column,
            HEIGHT / 2 - wallHeight / 2,
            2,
            wallHeight
        );

        ctx.globalAlpha = 1;
    }

    drawEnemies(depthBuffer, fieldOfView);
}

function drawEnemies(depthBuffer, fieldOfView) {
    const orderedEnemies = enemies
        .map(enemy => ({
            ...enemy,
            distance: Math.hypot(
                enemy.x - player.x,
                enemy.y - player.y
            ),
            angle: Math.atan2(
                enemy.y - player.y,
                enemy.x - player.x
            )
        }))
        .sort((a, b) => b.distance - a.distance);

    for (const enemy of orderedEnemies) {
        let angleDifference =
            enemy.angle - player.angle;

        angleDifference = Math.atan2(
            Math.sin(angleDifference),
            Math.cos(angleDifference)
        );

        if (Math.abs(angleDifference) > fieldOfView * 0.65) {
            continue;
        }

        const screenX =
            WIDTH / 2 +
            angleDifference / fieldOfView * WIDTH;

        const size = Math.min(
            260,
            300 / enemy.distance
        );

        const depthIndex = Math.max(
            0,
            Math.min(
                depthBuffer.length - 1,
                Math.floor(screenX / 2)
            )
        );

        if (enemy.distance < depthBuffer[depthIndex] + 0.2) {
            /* 몸 */
            ctx.fillStyle = "#260907";
            ctx.fillRect(
                screenX - size * 0.27,
                HEIGHT / 2 - size * 0.42,
                size * 0.54,
                size * 0.84
            );

            /* 머리 */
            ctx.fillStyle = "#d63c25";
            ctx.beginPath();
            ctx.arc(
                screenX,
                HEIGHT / 2 - size * 0.42,
                size * 0.25,
                0,
                Math.PI * 2
            );
            ctx.fill();

            /* 눈 */
            ctx.fillStyle = "#ffe25e";

            ctx.fillRect(
                screenX - size * 0.13,
                HEIGHT / 2 - size * 0.48,
                size * 0.08,
                size * 0.06
            );

            ctx.fillRect(
                screenX + size * 0.05,
                HEIGHT / 2 - size * 0.48,
                size * 0.08,
                size * 0.06
            );
        }
    }
}

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
            HEIGHT - 193,
            35,
            0,
            Math.PI * 2
        );
        ctx.fill();

        muzzleFlash -= 1;
    }
}

function drawCrosshair() {
    ctx.strokeStyle = "white";
    ctx.lineWidth = 2;

    ctx.beginPath();
    ctx.moveTo(WIDTH / 2 - 12, HEIGHT / 2);
    ctx.lineTo(WIDTH / 2 + 12, HEIGHT / 2);

    ctx.moveTo(WIDTH / 2, HEIGHT / 2 - 12);
    ctx.lineTo(WIDTH / 2, HEIGHT / 2 + 12);

    ctx.stroke();
}

function drawHud() {
    ctx.fillStyle = "rgba(0, 0, 0, 0.78)";
    ctx.fillRect(0, HEIGHT - 62, WIDTH, 62);

    ctx.font = "bold 23px monospace";

    ctx.fillStyle =
        player.health < 30 ? "#ff3322" : "#ffb23d";

    ctx.fillText(
        "HP " + Math.max(0, Math.ceil(player.health)),
        20,
        HEIGHT - 24
    );

    ctx.fillStyle = "#eeeeee";
    ctx.fillText(
        "AMMO " + player.ammo + "/12",
        WIDTH / 2 - 70,
        HEIGHT - 24
    );

    ctx.fillStyle = "#ffb23d";
    ctx.fillText(
        "SCORE " + player.score,
        WIDTH - 190,
        HEIGHT - 24
    );
}

function drawEndScreen() {
    if (playing) {
        return;
    }

    ctx.fillStyle = "rgba(0, 0, 0, 0.76)";
    ctx.fillRect(0, 0, WIDTH, HEIGHT);

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

function render() {
    drawWorld();
    drawEnemies;
    drawWeapon();
    drawCrosshair();
    drawHud();
    drawEndScreen();
}

function gameLoop(timestamp) {
    const deltaTime = Math.min(
        0.04,
        (timestamp - lastFrame) / 1000 || 0
    );

    lastFrame = timestamp;

    update(deltaTime);
    render();

    requestAnimationFrame(gameLoop);
}

/* 시작 버튼 */
document
    .getElementById("startButton")
    .addEventListener("click", () => {
        document.getElementById("startScreen").style.display = "none";
        resetGame();
    });

/* 터치 버튼을 계속 누르고 있을 때 동작 */
function bindHoldButton(elementId, controlName) {
    const element = document.getElementById(elementId);

    function activate(event) {
        event.preventDefault();
        controls[controlName] = true;
        element.classList.add("active");
    }

    function deactivate(event) {
        event.preventDefault();
        controls[controlName] = false;
        element.classList.remove("active");
    }

    element.addEventListener("pointerdown", activate);
    element.addEventListener("pointerup", deactivate);
    element.addEventListener("pointercancel", deactivate);
    element.addEventListener("pointerleave", deactivate);
}

bindHoldButton("forward", "forward");
bindHoldButton("backward", "backward");
bindHoldButton("strafeLeft", "strafeLeft");
bindHoldButton("strafeRight", "strafeRight");
bindHoldButton("turnLeft", "turnLeft");
bindHoldButton("turnRight", "turnRight");

/* 발사 버튼 */
const fireButton = document.getElementById("fire");

fireButton.addEventListener("pointerdown", event => {
    event.preventDefault();
    fireButton.classList.add("active");
    shoot();
});

fireButton.addEventListener("pointerup", event => {
    event.preventDefault();
    fireButton.classList.remove("active");
});

/* 재장전 버튼 */
const reloadButton = document.getElementById("reload");

reloadButton.addEventListener("pointerdown", event => {
    event.preventDefault();
    player.ammo = 12;
    reloadButton.classList.add("active");
});

reloadButton.addEventListener("pointerup", event => {
    event.preventDefault();
    reloadButton.classList.remove("active");
});

/* 화면 드래그로 시점 회전 */
let previousTouchX = null;

canvas.addEventListener("pointerdown", event => {
    if (event.pointerType === "touch") {
        previousTouchX = event.clientX;
        canvas.setPointerCapture(event.pointerId);
    }
});

canvas.addEventListener("pointermove", event => {
    if (
        event.pointerType === "touch" &&
        previousTouchX !== null
    ) {
        const movement = event.clientX - previousTouchX;

        player.angle += movement * 0.006;
        previousTouchX = event.clientX;
    }
});

canvas.addEventListener("pointerup", event => {
    if (event.pointerType === "touch") {
        previousTouchX = null;
    }
});

/* 게임 종료 후 두 번 터치하여 재시작 */
canvas.addEventListener("dblclick", () => {
    if (!playing) {
        resetGame();
    }
});

/* PC 키보드도 지원 */
window.addEventListener("keydown", event => {
    if (event.code === "KeyW") controls.forward = true;
    if (event.code === "KeyS") controls.backward = true;
    if (event.code === "KeyA") controls.strafeLeft = true;
    if (event.code === "KeyD") controls.strafeRight = true;
    if (event.code === "ArrowLeft") controls.turnLeft = true;
    if (event.code === "ArrowRight") controls.turnRight = true;

    if (event.code === "Space") {
        event.preventDefault();
        shoot();
    }

    if (event.code === "KeyR") {
        player.ammo = 12;
    }
});

window.addEventListener("keyup", event => {
    if (event.code === "KeyW") controls.forward = false;
    if (event.code === "KeyS") controls.backward = false;
    if (event.code === "KeyA") controls.strafeLeft = false;
    if (event.code === "KeyD") controls.strafeRight = false;
    if (event.code === "ArrowLeft") controls.turnLeft = false;
    if (event.code === "ArrowRight") controls.turnRight = false;
});

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

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="DOOM MOBILE",
    page_icon="👹",
    layout="wide",
    initial_sidebar_state="collapsed"
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
        border: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

GAME = r'''
<!doctype html>
<html lang="ko">

<head>
<meta charset="utf-8">

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
    overflow: hidden;
    background: #050403;
    color: #fff;
    font-family: Arial, sans-serif;
    touch-action: none;
    user-select: none;
}

#game {
    position: relative;
    width: 100%;
    height: 92vh;
    min-height: 540px;
    overflow: hidden;
    background: #000;
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
    z-index: 50;
    display: grid;
    place-items: center;
    text-align: center;
    background:
        radial-gradient(
            circle,
            #67180d,
            #170403 50%,
            #020101 85%
        );
}

#startScreen h1 {
    margin: 0;
    color: #e83a1f;
    font: 900 clamp(48px, 13vw, 92px) Impact;
    letter-spacing: 4px;
    text-shadow: 0 6px #641006;
}

#startScreen p {
    line-height: 1.65;
    color: #dcc7ae;
}

#startButton {
    padding: 15px 35px;
    border: 2px solid #ff765b;
    border-radius: 10px;
    background: #ad2415;
    color: #fff;
    font-size: 20px;
    font-weight: 900;
}

/* 조작 화면 */

#controls {
    position: absolute;
    inset: 0;
    z-index: 20;
    pointer-events: none;
}

/* 브롤스타즈 방식 이동 조이스틱 */

#joystick {
    position: absolute;
    left: 20px;
    bottom: 78px;
    width: 168px;
    height: 168px;
    border: 3px solid rgba(255,255,255,.30);
    border-radius: 50%;
    background:
        radial-gradient(
            circle,
            rgba(87,77,69,.50),
            rgba(12,10,9,.68)
        );
    pointer-events: auto;
    touch-action: none;
}

#joystickKnob {
    position: absolute;
    left: 49px;
    top: 49px;
    width: 70px;
    height: 70px;
    border: 3px solid rgba(255,255,255,.53);
    border-radius: 50%;
    background:
        radial-gradient(
            circle at 35% 30%,
            #86786a,
            #29231f
        );
    box-shadow: 0 4px 12px #000;
}

/* 행동 버튼 */

.actionButton {
    position: absolute;
    display: grid;
    place-items: center;
    border: 3px solid rgba(255,255,255,.44);
    border-radius: 50%;
    color: #fff;
    font-weight: 900;
    pointer-events: auto;
    touch-action: none;
    box-shadow: 0 4px 12px #000;
}

.actionButton.active {
    transform: scale(.93);
    filter: brightness(1.4);
}

#fireButton {
    right: 18px;
    bottom: 105px;
    width: 118px;
    height: 118px;
    font-size: 22px;
    background:
        radial-gradient(
            circle at 35% 25%,
            #e75136,
            #8c120b
        );
}

#jumpButton {
    right: 150px;
    bottom: 78px;
    width: 72px;
    height: 72px;
    font-size: 13px;
    background: #51453c;
}

#runButton {
    right: 150px;
    bottom: 164px;
    width: 72px;
    height: 72px;
    font-size: 13px;
    background: #493c32;
}

#guide {
    position: absolute;
    top: 10px;
    left: 50%;
    z-index: 25;
    padding: 6px 12px;
    transform: translateX(-50%);
    border-radius: 7px;
    background: rgba(0,0,0,.67);
    color: #ffd98c;
    font-size: 12px;
    white-space: nowrap;
}

@media (orientation: portrait) {
    #game {
        height: 76vh;
        min-height: 560px;
    }

    #joystick {
        left: 7px;
        bottom: 70px;
        transform: scale(.82);
        transform-origin: left bottom;
    }

    #fireButton {
        right: 7px;
        bottom: 100px;
        transform: scale(.82);
        transform-origin: right bottom;
    }

    #jumpButton {
        right: 105px;
        bottom: 65px;
        transform: scale(.8);
    }

    #runButton {
        right: 105px;
        bottom: 135px;
        transform: scale(.8);
    }
}
</style>
</head>

<body>

<div id="game">

    <canvas
        id="canvas"
        width="960"
        height="600"
    ></canvas>

    <div id="guide">
        조이스틱 이동 · 빈 화면 드래그 조준
    </div>

    <div id="controls">

        <div id="joystick">
            <div id="joystickKnob"></div>
        </div>

        <div
            class="actionButton"
            id="runButton"
        >
            RUN
        </div>

        <div
            class="actionButton"
            id="jumpButton"
        >
            JUMP
        </div>

        <div
            class="actionButton"
            id="fireButton"
        >
            FIRE
        </div>

    </div>

    <div id="startScreen">
        <div>
            <h1>DOOM MOBILE</h1>

            <p>
                조이스틱·달리기·점프·2층 전투<br>
                라운드마다 더 많고 빠른 악마가 등장합니다.
            </p>

            <button id="startButton">
                지옥문 열기
            </button>
        </div>
    </div>

</div>

<script>
const canvas =
    document.getElementById("canvas");

const ctx =
    canvas.getContext("2d");

const WIDTH = canvas.width;
const HEIGHT = canvas.height;

/*
0 = 통로
1~3 = 벽
4 = 계단
5 = 점프로 넘는 낮은 장애물
*/

const MAPS = {
    1: [
        "1111111111111111",
        "1000000000000001",
        "1000000100000001",
        "1000000100004001",
        "1000111101110001",
        "1000000001000001",
        "1000000001000001",
        "1000110001000001",
        "1000010000000001",
        "1000010111100001",
        "1000000100000001",
        "1005000000000001",
        "1000001110000001",
        "1000000000000001",
        "1000000000000001",
        "1111111111111111"
    ],

    2: [
        "1111111111111111",
        "1000000000000001",
        "1000111100000001",
        "1400000100000001",
        "1000000101110001",
        "1000000000010001",
        "1011100000010001",
        "1000000000010001",
        "1000011100000001",
        "1000000100111001",
        "1005000100000001",
        "1000000000000001",
        "1011110001110001",
        "1000000000000001",
        "1000000000000001",
        "1111111111111111"
    ]
};

/* 몬스터 생성 위치 */

const SPAWN_POINTS = {
    1: [
        [7.5, 1.5],
        [12.5, 2.5],
        [3.5, 6.5],
        [11.5, 8.5],
        [13.5, 13.5],
        [4.5, 13.5],
        [8.5, 11.5],
        [2.5, 9.5],
        [11.5, 5.5],
        [7.5, 14.5]
    ],

    2: [
        [7.5, 1.5],
        [12.5, 3.5],
        [3.5, 5.5],
        [8.5, 7.5],
        [13.5, 8.5],
        [3.5, 11.5],
        [9.5, 11.5],
        [13.5, 14.5],
        [6.5, 14.5],
        [2.5, 8.5]
    ]
};

let player;
let enemies = [];

let round = 1;
let joystick = {x: 0, y: 0};

let running = false;
let playing = false;

let lastFrame = 0;
let muzzleFlash = 0;

let message = "";
let messageTime = 0;
let stairLock = 0;

function getTile(x, y, floor = player.floor) {
    const row =
        MAPS[floor][Math.floor(y)];

    if (!row) {
        return 1;
    }

    return Number(
        row[Math.floor(x)] ?? 1
    );
}

function isSolid(x, y) {
    const tile = getTile(x, y);

    if (tile > 0 && tile < 4) {
        return true;
    }

    if (
        tile === 5 &&
        player.jumpHeight < .28
    ) {
        return true;
    }

    return false;
}

function showMessage(text, seconds = 1.5) {
    message = text;
    messageTime = seconds;
}

/* 라운드 몬스터 생성 */

function spawnRound() {
    enemies = [];

    const enemyCount =
        Math.min(4 + round * 2, 18);

    const spawnList =
        SPAWN_POINTS[player.floor];

    for (
        let index = 0;
        index < enemyCount;
        index++
    ) {
        const spawn =
            spawnList[
                index % spawnList.length
            ];

        const offset =
            Math.floor(
                index / spawnList.length
            ) * .18;

        enemies.push({
            x: spawn[0] + offset,
            y: spawn[1],
            health:
                1 + Math.floor(round / 3),
            hitTime: 0
        });
    }
}

/* 게임 초기화 */

function resetGame() {
    round = 1;

    player = {
        x: 2.5,
        y: 1.5,
        angle: 0,
        health: 100,
        ammo: 12,
        score: 0,
        floor: 1,
        jumpHeight: 0,
        jumpVelocity: 0
    };

    spawnRound();

    playing = true;

    showMessage("ROUND 1");
}

/* 광선 추적 */

function castRay(angle) {
    const cosine = Math.cos(angle);
    const sine = Math.sin(angle);

    let distance = 0;

    while (distance < 20) {
        distance += .025;

        const rayX =
            player.x +
            cosine * distance;

        const rayY =
            player.y +
            sine * distance;

        const tile =
            getTile(rayX, rayY);

        if (
            (tile > 0 && tile < 4) ||
            (
                tile === 5 &&
                player.jumpHeight < .44
            )
        ) {
            return {
                distance: distance,
                type: tile
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
        player.ammo < 1
    ) {
        return;
    }

    player.ammo -= 1;
    muzzleFlash = 5;

    let target = null;
    let closestAngle = .15;

    for (const enemy of enemies) {
        const dx =
            enemy.x - player.x;

        const dy =
            enemy.y - player.y;

        const distance =
            Math.hypot(dx, dy);

        let angleDifference =
            Math.atan2(dy, dx) -
            player.angle;

        angleDifference =
            Math.atan2(
                Math.sin(angleDifference),
                Math.cos(angleDifference)
            );

        const wallDistance =
            castRay(
                player.angle +
                angleDifference
            ).distance;

        if (
            Math.abs(angleDifference) <
            closestAngle &&
            distance <
            wallDistance + .15
        ) {
            target = enemy;

            closestAngle =
                Math.abs(angleDifference);
        }
    }

    if (!target) {
        return;
    }

    target.health -= 1;
    target.hitTime = .12;

    player.score += 50;

    if (target.health <= 0) {
        enemies.splice(
            enemies.indexOf(target),
            1
        );

        player.score += 150;
    }

    /* 다음 라운드 */

    if (enemies.length === 0) {
        playing = false;

        showMessage(
            "SECTOR CLEAR",
            2
        );

        setTimeout(function () {
            round += 1;

            player.health =
                Math.min(
                    100,
                    player.health + 25
                );

            player.ammo = 12;

            spawnRound();

            playing = true;

            showMessage(
                "ROUND " +
                round +
                " · SPEED UP!",
                2
            );
        }, 1200);
    }
}

/* 점프 */

function jump() {
    if (player.jumpHeight === 0) {
        player.jumpVelocity = 2.7;
    }
}

/* 층 이동 */

function changeFloor(newFloor) {
    player.floor = newFloor;

    if (newFloor === 2) {
        player.x = 2.5;
        player.y = 3.5;
        player.angle = 0;
    } else {
        player.x = 12.5;
        player.y = 3.5;
        player.angle = Math.PI;
    }

    stairLock = 1;

    /*
    층 이동 시 몬스터도 현재 층으로 이동시켜
    보이지 않는 몬스터가 남는 현상을 방지합니다.
    */

    const spawnList =
        SPAWN_POINTS[newFloor];

    enemies.forEach(
        function (enemy, index) {
            const spawn =
                spawnList[
                    index %
                    spawnList.length
                ];

            enemy.x = spawn[0];
            enemy.y = spawn[1];
        }
    );

    showMessage(
        newFloor + "층 진입"
    );
}

/* 게임 상태 갱신 */

function update(deltaTime) {
    if (messageTime > 0) {
        messageTime -= deltaTime;
    }

    if (!playing) {
        return;
    }

    if (stairLock > 0) {
        stairLock -= deltaTime;
    }

    /* 점프 물리 */

    player.jumpVelocity -=
        6.8 * deltaTime;

    player.jumpHeight =
        Math.max(
            0,
            player.jumpHeight +
            player.jumpVelocity *
            deltaTime
        );

    if (
        player.jumpHeight === 0 &&
        player.jumpVelocity < 0
    ) {
        player.jumpVelocity = 0;
    }

    /* 이동 */

    const speed =
        (
            running
            ? 4
            : 2.5
        ) * deltaTime;

    const forward =
        -joystick.y;

    const sideways =
        joystick.x;

    const moveX =
        (
            Math.cos(player.angle) *
            forward +
            Math.cos(
                player.angle +
                Math.PI / 2
            ) * sideways
        ) * speed;

    const moveY =
        (
            Math.sin(player.angle) *
            forward +
            Math.sin(
                player.angle +
                Math.PI / 2
            ) * sideways
        ) * speed;

    if (
        !isSolid(
            player.x +
            moveX +
            Math.sign(moveX) * .18,
            player.y
        )
    ) {
        player.x += moveX;
    }

    if (
        !isSolid(
            player.x,
            player.y +
            moveY +
            Math.sign(moveY) * .18
        )
    ) {
        player.y += moveY;
    }

    /* 계단 진입 */

    if (
        getTile(
            player.x,
            player.y
        ) === 4 &&
        stairLock <= 0
    ) {
        changeFloor(
            player.floor === 1
            ? 2
            : 1
        );
    }

    /*
    라운드가 증가할수록
    몬스터 속도가 증가합니다.
    */

    const monsterSpeed =
        Math.min(
            .76 + round * .08,
            1.6
        );

    for (const enemy of enemies) {
        enemy.hitTime =
            Math.max(
                0,
                enemy.hitTime -
                deltaTime
            );

        const dx =
            player.x - enemy.x;

        const dy =
            player.y - enemy.y;

        const distance =
            Math.hypot(dx, dy);

        if (distance < .67) {
            player.health -=
                Math.min(
                    16 + round * 1.5,
                    31
                ) * deltaTime;
        } else if (distance < 10) {
            const moveAmount =
                monsterSpeed *
                deltaTime;

            const nextX =
                enemy.x +
                dx / distance *
                moveAmount;

            const nextY =
                enemy.y +
                dy / distance *
                moveAmount;

            const xTile =
                getTile(
                    nextX,
                    enemy.y
                );

            const yTile =
                getTile(
                    enemy.x,
                    nextY
                );

            if (
                xTile === 0 ||
                xTile === 4
            ) {
                enemy.x = nextX;
            }

            if (
                yTile === 0 ||
                yTile === 4
            ) {
                enemy.y = nextY;
            }
        }
    }

    if (player.health <= 0) {
        player.health = 0;
        playing = false;

        showMessage(
            "YOU DIED · 두 번 눌러 재시작",
            999
        );
    }
}

/* 벽과 배경 */

function drawWorld() {
    const sky =
        ctx.createLinearGradient(
            0,
            0,
            0,
            HEIGHT / 2
        );

    sky.addColorStop(
        0,
        "#190403"
    );

    sky.addColorStop(
        1,
        player.floor === 1
        ? "#782010"
        : "#5b3020"
    );

    ctx.fillStyle = sky;

    ctx.fillRect(
        0,
        0,
        WIDTH,
        HEIGHT / 2
    );

    ctx.fillStyle = "#17120f";

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

        let wallHeight =
            Math.min(
                HEIGHT,
                HEIGHT /
                Math.max(
                    correctedDistance,
                    .01
                )
            );

        let wallY =
            HEIGHT / 2 -
            wallHeight / 2 +
            player.jumpHeight * 95;

        depthBuffer[column / 2] =
            correctedDistance;

        if (ray.type === 2) {
            ctx.fillStyle = "#3e5946";
        } else if (ray.type === 3) {
            ctx.fillStyle = "#624568";
        } else if (ray.type === 5) {
            ctx.fillStyle = "#65442d";
        } else {
            ctx.fillStyle = "#793025";
        }

        ctx.globalAlpha =
            Math.max(
                .2,
                1 -
                correctedDistance / 15
            );

        if (ray.type === 5) {
            wallHeight *= .48;

            wallY =
                HEIGHT / 2 +
                wallHeight * .05 +
                player.jumpHeight * 95;
        }

        ctx.fillRect(
            column,
            wallY,
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

/* 몬스터 */

function drawEnemies(
    depthBuffer,
    fieldOfView
) {
    const sortedEnemies =
        enemies
        .map(function (enemy) {
            return {
                enemy: enemy,

                distance:
                    Math.hypot(
                        enemy.x -
                        player.x,

                        enemy.y -
                        player.y
                    ),

                angle:
                    Math.atan2(
                        enemy.y -
                        player.y,

                        enemy.x -
                        player.x
                    )
            };
        })
        .sort(function (a, b) {
            return b.distance -
                   a.distance;
        });

    for (
        const data of sortedEnemies
    ) {
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
            fieldOfView * .62
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
                300,
                380 /
                Math.max(
                    data.distance,
                    .2
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
            depthBuffer[
                depthIndex
            ] + .25
        ) {
            continue;
        }

        const centerY =
            HEIGHT / 2 -
            size * .12 +
            player.jumpHeight * 95;

        /* 몸 */

        ctx.fillStyle =
            data.enemy.hitTime > 0
            ? "#ffffff"
            : "#4d0b07";

        ctx.fillRect(
            screenX - size * .25,
            centerY,
            size * .5,
            size * .58
        );

        /* 머리 */

        ctx.fillStyle =
            data.enemy.hitTime > 0
            ? "#ffffff"
            : "#d13b20";

        ctx.beginPath();

        ctx.arc(
            screenX,
            centerY - size * .13,
            size * .25,
            0,
            Math.PI * 2
        );

        ctx.fill();

        /* 왼쪽 뿔 */

        ctx.fillStyle = "#e6cc92";

        ctx.beginPath();

        ctx.moveTo(
            screenX - size * .18,
            centerY - size * .27
        );

        ctx.lineTo(
            screenX - size * .34,
            centerY - size * .49
        );

        ctx.lineTo(
            screenX - size * .06,
            centerY - size * .31
        );

        ctx.fill();

        /* 오른쪽 뿔 */

        ctx.beginPath();

        ctx.moveTo(
            screenX + size * .18,
            centerY - size * .27
        );

        ctx.lineTo(
            screenX + size * .34,
            centerY - size * .49
        );

        ctx.lineTo(
            screenX + size * .06,
            centerY - size * .31
        );

        ctx.fill();

        /* 눈 */

        ctx.fillStyle = "#fff04e";

        ctx.fillRect(
            screenX - size * .13,
            centerY - size * .2,
            size * .08,
            size * .06
        );

        ctx.fillRect(
            screenX + size * .05,
            centerY - size * .2,
            size * .08,
            size * .06
        );
    }
}

/* 총과 HUD */

function drawHud() {
    /* 총 몸통 */

    ctx.fillStyle = "#302925";

    ctx.fillRect(
        WIDTH / 2 - 62,
        HEIGHT - 132 +
        player.jumpHeight * 30,
        124,
        132
    );

    ctx.fillStyle = "#101010";

    ctx.fillRect(
        WIDTH / 2 - 22,
        HEIGHT - 205 +
        player.jumpHeight * 30,
        44,
        116
    );

    /* 총구 화염 */

    if (muzzleFlash > 0) {
        ctx.fillStyle = "#ffd447";

        ctx.beginPath();

        ctx.arc(
            WIDTH / 2,
            HEIGHT - 207 +
            player.jumpHeight * 30,
            42,
            0,
            Math.PI * 2
        );

        ctx.fill();

        muzzleFlash -= 1;
    }

    /* 조준점 */

    ctx.strokeStyle = "#ffffff";
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

    /* 하단 상태창 */

    ctx.fillStyle =
        "rgba(0,0,0,.87)";

    ctx.fillRect(
        0,
        HEIGHT - 64,
        WIDTH,
        64
    );

    ctx.font =
        "bold 22px monospace";

    ctx.fillStyle =
        player.health < 30
        ? "#ff3322"
        : "#f0a73b";

    ctx.fillText(
        "HP " +
        Math.ceil(player.health),
        18,
        HEIGHT - 25
    );

    ctx.fillStyle = "#eeeeee";

    ctx.fillText(
        "AMMO " +
        player.ammo +
        "/12",
        WIDTH / 2 - 78,
        HEIGHT - 25
    );

    ctx.fillStyle = "#f0a73b";

    ctx.fillText(
        "R" + round +
        " F" + player.floor +
        " ENEMY " +
        enemies.length,
        WIDTH - 245,
        HEIGHT - 25
    );

    /* 마지막 몬스터 방향 표시 */

    if (enemies.length > 0) {
        const nearest =
            enemies.reduce(
                function (a, b) {
                    const distanceA =
                        Math.hypot(
                            a.x - player.x,
                            a.y - player.y
                        );

                    const distanceB =
                        Math.hypot(
                            b.x - player.x,
                            b.y - player.y
                        );

                    return (
                        distanceA <
                        distanceB
                    ) ? a : b;
                }
            );

        let direction =
            Math.atan2(
                nearest.y -
                player.y,

                nearest.x -
                player.x
            ) - player.angle;

        direction =
            Math.atan2(
                Math.sin(direction),
                Math.cos(direction)
            );

        ctx.save();

        ctx.translate(
            WIDTH / 2,
            42
        );

        ctx.rotate(direction);

        ctx.fillStyle = "#ff3b21";

        ctx.beginPath();

        ctx.moveTo(0, -17);
        ctx.lineTo(-11, 9);
        ctx.lineTo(11, 9);

        ctx.fill();

        ctx.restore();
    }

    /* 안내 메시지 */

    if (messageTime > 0) {
        ctx.fillStyle =
            "rgba(0,0,0,.72)";

        ctx.fillRect(
            WIDTH / 2 - 230,
            HEIGHT / 2 - 45,
            460,
            90
        );

        ctx.fillStyle = "#ef4827";

        ctx.font =
            "bold 34px Impact";

        ctx.textAlign = "center";

        ctx.fillText(
            message,
            WIDTH / 2,
            HEIGHT / 2 + 12
        );

        ctx.textAlign = "left";
    }
}

/* 게임 반복 */

function gameLoop(timestamp) {
    const deltaTime =
        Math.min(
            .04,
            (
                timestamp -
                lastFrame
            ) / 1000 || 0
        );

    lastFrame = timestamp;

    update(deltaTime);
    drawWorld();
    drawHud();

    requestAnimationFrame(
        gameLoop
    );
}

/* 시작 버튼 */

document
    .getElementById(
        "startButton"
    )
    .onclick = function () {
        document
            .getElementById(
                "startScreen"
            )
            .style.display = "none";

        resetGame();
    };

/* 조이스틱 */

const joystickBase =
    document.getElementById(
        "joystick"
    );

const joystickKnob =
    document.getElementById(
        "joystickKnob"
    );

let joystickPointer = null;

function moveJoystick(event) {
    const rect =
        joystickBase
        .getBoundingClientRect();

    let deltaX =
        event.clientX -
        rect.left -
        rect.width / 2;

    let deltaY =
        event.clientY -
        rect.top -
        rect.height / 2;

    const maximum =
        rect.width * .31;

    const length =
        Math.hypot(
            deltaX,
            deltaY
        );

    if (length > maximum) {
        deltaX *=
            maximum / length;

        deltaY *=
            maximum / length;
    }

    joystick.x =
        deltaX / maximum;

    joystick.y =
        deltaY / maximum;

    joystickKnob.style.transform =
        "translate(" +
        deltaX + "px," +
        deltaY + "px)";
}

joystickBase.onpointerdown =
    function (event) {
        event.preventDefault();

        joystickPointer =
            event.pointerId;

        joystickBase
            .setPointerCapture(
                joystickPointer
            );

        moveJoystick(event);
    };

joystickBase.onpointermove =
    function (event) {
        if (
            event.pointerId ===
            joystickPointer
        ) {
            moveJoystick(event);
        }
    };

function stopJoystick(event) {
    if (
        event.pointerId !==
        joystickPointer
    ) {
        return;
    }

    joystickPointer = null;

    joystick.x = 0;
    joystick.y = 0;

    joystickKnob.style.transform =
        "translate(0,0)";
}

joystickBase.onpointerup =
    stopJoystick;

joystickBase.onpointercancel =
    stopJoystick;

/* 터치 버튼 */

function bindButton(
    elementId,
    startAction,
    endAction
) {
    const element =
        document.getElementById(
            elementId
        );

    element.onpointerdown =
        function (event) {
            event.preventDefault();

            element.classList.add(
                "active"
            );

            startAction();
        };

    element.onpointerup =
    element.onpointercancel =
        function (event) {
            event.preventDefault();

            element.classList.remove(
                "active"
            );

            if (endAction) {
                endAction();
            }
        };
}

/* 달리기는 누르고 있는 동안 작동 */

bindButton(
    "runButton",
    function () {
        running = true;
    },
    function () {
        running = false;
    }
);

/* 점프 */

bindButton(
    "jumpButton",
    jump
);

/* 발사 */

bindButton(
    "fireButton",
    shoot
);

/* 빈 화면 드래그로 조준 */

let lookPointer = null;
let previousLookX = 0;

canvas.onpointerdown =
    function (event) {
        if (
            event.pointerType ===
            "touch"
        ) {
            lookPointer =
                event.pointerId;

            previousLookX =
                event.clientX;

            canvas.setPointerCapture(
                lookPointer
            );
        }
    };

canvas.onpointermove =
    function (event) {
        if (
            event.pointerId ===
            lookPointer
        ) {
            player.angle +=
                (
                    event.clientX -
                    previousLookX
                ) * .006;

            previousLookX =
                event.clientX;
        }
    };

canvas.onpointerup =
canvas.onpointercancel =
    function (event) {
        if (
            event.pointerId ===
            lookPointer
        ) {
            lookPointer = null;
        }
    };

/* 사망 후 두 번 눌러 재시작 */

canvas.ondblclick =
    function () {
        if (
            !playing &&
            player.health <= 0
        ) {
            resetGame();
        }
    };

/* 최초 상태 */

resetGame();

requestAnimationFrame(
    gameLoop
);
</script>

</body>
</html>
'''

components.html(
    GAME,
    height=760,
    scrolling=False
)

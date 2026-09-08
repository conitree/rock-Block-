import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="DOOM MOBILE",
    page_icon="👹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.block-container{padding:0!important;max-width:100%!important}
header,footer,#MainMenu{display:none!important}
iframe{border:0}
</style>
""", unsafe_allow_html=True)

GAME = r'''
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport"
content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">

<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}

html,body{
    margin:0;
    overflow:hidden;
    background:#050403;
    color:#fff;
    font-family:Arial,sans-serif;
    touch-action:none;
    user-select:none
}

#game{
    position:relative;
    width:100%;
    height:92vh;
    min-height:540px;
    background:#000;
    overflow:hidden
}

canvas{
    width:100%;
    height:100%;
    display:block;
    image-rendering:pixelated;
    touch-action:none
}

#start{
    position:absolute;
    inset:0;
    z-index:50;
    display:grid;
    place-items:center;
    text-align:center;
    background:radial-gradient(circle,#67180d,#170403 50%,#020101 85%)
}

#start h1{
    margin:0;
    color:#e83a1f;
    font:900 clamp(48px,13vw,92px) Impact;
    letter-spacing:4px;
    text-shadow:0 6px #641006
}

#start p{
    line-height:1.65;
    color:#dcc7ae
}

#startButton{
    padding:15px 35px;
    border:2px solid #ff765b;
    border-radius:10px;
    background:#ad2415;
    color:#fff;
    font-size:20px;
    font-weight:900
}

#controls{
    position:absolute;
    inset:0;
    z-index:20;
    pointer-events:none
}

#joystick{
    position:absolute;
    left:20px;
    bottom:78px;
    width:168px;
    height:168px;
    border-radius:50%;
    border:3px solid rgba(255,255,255,.3);
    background:radial-gradient(circle,rgba(88,79,70,.52),rgba(12,10,9,.65));
    pointer-events:auto;
    touch-action:none
}

#knob{
    position:absolute;
    left:49px;
    top:49px;
    width:70px;
    height:70px;
    border-radius:50%;
    border:3px solid rgba(255,255,255,.52);
    background:radial-gradient(circle at 35% 30%,#86786a,#29231f);
    box-shadow:0 4px 12px #000
}

.action{
    position:absolute;
    display:grid;
    place-items:center;
    border-radius:50%;
    border:3px solid rgba(255,255,255,.42);
    color:#fff;
    font-weight:900;
    pointer-events:auto;
    touch-action:none;
    box-shadow:0 4px 12px rgba(0,0,0,.55)
}

.action.active{
    transform:scale(.94);
    filter:brightness(1.4)
}

#fireButton{
    right:18px;
    bottom:105px;
    width:118px;
    height:118px;
    background:radial-gradient(circle at 35% 25%,#e75136,#8c120b);
    font-size:22px
}

#jumpButton{
    right:150px;
    bottom:78px;
    width:72px;
    height:72px;
    background:#51453c;
    font-size:13px
}

#runButton{
    right:150px;
    bottom:164px;
    width:72px;
    height:72px;
    background:#493c32;
    font-size:13px
}

#runButton.running{
    background:#c34720;
    border-color:#ffd36c;
    box-shadow:0 0 20px #ff6a31
}

#guide{
    position:absolute;
    top:10px;
    left:50%;
    transform:translateX(-50%);
    z-index:25;
    padding:6px 12px;
    border-radius:7px;
    background:rgba(0,0,0,.67);
    color:#ffd98c;
    font-size:12px;
    white-space:nowrap
}

@media(orientation:portrait){
    #game{height:76vh;min-height:560px}

    #joystick{
        left:7px;
        bottom:70px;
        transform:scale(.82);
        transform-origin:left bottom
    }

    #fireButton{
        right:7px;
        bottom:100px;
        transform:scale(.82);
        transform-origin:right bottom
    }

    #jumpButton{
        right:105px;
        bottom:65px;
        transform:scale(.8)
    }

    #runButton{
        right:105px;
        bottom:135px;
        transform:scale(.8)
    }
}
</style>
</head>

<body>
<div id="game">

<canvas id="canvas" width="960" height="600"></canvas>

<div id="guide">조이스틱 이동 · 빈 화면 드래그 조준</div>

<div id="controls">
    <div id="joystick">
        <div id="knob"></div>
    </div>

    <div class="action" id="runButton">RUN</div>
    <div class="action" id="jumpButton">JUMP</div>
    <div class="action" id="fireButton">FIRE</div>
</div>

<div id="start">
    <div>
        <h1>DOOM MOBILE</h1>
        <p>
            조이스틱·달리기·점프·2층 전투<br>
            RUN은 한 번 누르면 계속 달립니다.<br>
            빛나는 포탈로 층을 이동하세요.
        </p>
        <button id="startButton">지옥문 열기</button>
    </div>
</div>

</div>

<script>
const canvas=document.getElementById("canvas");
const ctx=canvas.getContext("2d");
const WIDTH=canvas.width;
const HEIGHT=canvas.height;

/*
0 = 통로
1~3 = 벽
4 = 포탈
5 = 낮은 장애물
*/

const MAPS={
    1:[
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
    2:[
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

const SPAWNS={
    1:[
        [7.5,1.5],[12.5,2.5],[3.5,6.5],[11.5,8.5],
        [13.5,13.5],[4.5,13.5],[8.5,11.5],[2.5,9.5],
        [11.5,5.5],[7.5,14.5]
    ],
    2:[
        [7.5,1.5],[12.5,3.5],[3.5,5.5],[8.5,7.5],
        [13.5,8.5],[3.5,11.5],[9.5,11.5],[13.5,14.5],
        [6.5,14.5],[2.5,8.5]
    ]
};

const PORTALS={
    1:{x:12.5,y:3.5,label:"2층 PORTAL"},
    2:{x:1.5,y:3.5,label:"1층 PORTAL"}
};

let player;
let enemies=[];
let round=1;

let joystick={x:0,y:0};
let running=false;
let playing=false;

let muzzleFlash=0;
let hurtTime=0;
let lastFrame=0;
let stairLock=0;

let message="";
let messageTime=0;

function tileAt(x,y,floor=player.floor){
    const row=MAPS[floor][Math.floor(y)];
    return row ? Number(row[Math.floor(x)] ?? 1) : 1;
}

function solidAt(x,y){
    const tile=tileAt(x,y);

    if(tile>=1 && tile<=3){
        return true;
    }

    if(tile===5 && player.jumpHeight<.28){
        return true;
    }

    return false;
}

function announce(text,time=1.5){
    message=text;
    messageTime=time;
}

function resetGame(){
    round=1;
    running=false;
    hurtTime=0;

    document
        .getElementById("runButton")
        .classList.remove("running");

    player={
        x:2.5,
        y:1.5,
        angle:0,
        health:100,
        ammo:12,
        score:0,
        floor:1,
        jumpHeight:0,
        jumpVelocity:0
    };

    spawnRound();
    playing=true;
    announce("ROUND 1");
}

function spawnRound(){
    enemies=[];

    const count=Math.min(4+round*2,18);
    const points=SPAWNS[player.floor];

    for(let i=0;i<count;i++){
        const point=points[i%points.length];
        const offset=Math.floor(i/points.length)*.18;

        enemies.push({
            x:point[0]+offset,
            y:point[1],
            health:1+Math.floor(round/3),
            hitTime:0
        });
    }
}

/*
벽 광선 판정은 점프 상태와 관계없이 고정합니다.
점프할 때 벽이 사라지거나 맵이 무너져 보이는 현상을 방지합니다.
*/

function castRay(angle){
    const cos=Math.cos(angle);
    const sin=Math.sin(angle);
    let distance=0;

    while(distance<20){
        distance+=.025;

        const rayX=player.x+cos*distance;
        const rayY=player.y+sin*distance;
        const tile=tileAt(rayX,rayY);

        if(
            (tile>=1 && tile<=3) ||
            tile===5
        ){
            return{
                distance:distance,
                type:tile
            };
        }
    }

    return{distance:20,type:1};
}

function shoot(){
    if(!playing || player.ammo<1){
        return;
    }

    player.ammo--;
    muzzleFlash=5;

    let target=null;
    let smallestAngle=.15;

    for(const enemy of enemies){
        const dx=enemy.x-player.x;
        const dy=enemy.y-player.y;
        const distance=Math.hypot(dx,dy);

        let difference=
            Math.atan2(dy,dx)-player.angle;

        difference=Math.atan2(
            Math.sin(difference),
            Math.cos(difference)
        );

        const wallDistance=
            castRay(player.angle+difference).distance;

        if(
            Math.abs(difference)<smallestAngle &&
            distance<wallDistance+.15
        ){
            target=enemy;
            smallestAngle=Math.abs(difference);
        }
    }

    if(!target){
        return;
    }

    target.health--;
    target.hitTime=.12;
    player.score+=50;

    if(target.health<=0){
        enemies.splice(enemies.indexOf(target),1);
        player.score+=150;
    }

    if(enemies.length===0){
        playing=false;
        announce("SECTOR CLEAR",2);

        setTimeout(function(){
            round++;

            player.health=Math.min(
                100,
                player.health+25
            );

            player.ammo=12;

            spawnRound();
            playing=true;

            announce(
                "ROUND "+round+" · SPEED UP!",
                2
            );
        },1200);
    }
}

function jump(){
    if(player.jumpHeight===0){
        player.jumpVelocity=2.7;
    }
}

function changeFloor(newFloor){
    player.floor=newFloor;

    if(newFloor===2){
        player.x=2.5;
        player.y=3.5;
        player.angle=0;
    }else{
        player.x=12.5;
        player.y=3.5;
        player.angle=Math.PI;
    }

    stairLock=1;

    /*
    몬스터를 현재 층의 접근 가능한 위치로 옮겨
    다른 층에 한 마리가 남는 현상을 방지합니다.
    */

    const points=SPAWNS[newFloor];

    enemies.forEach(function(enemy,index){
        const point=points[index%points.length];
        enemy.x=point[0];
        enemy.y=point[1];
    });

    announce(newFloor+"층 진입");
}

function update(deltaTime){
    if(messageTime>0){
        messageTime-=deltaTime;
    }

    hurtTime=Math.max(
        0,
        hurtTime-deltaTime
    );

    if(!playing){
        return;
    }

    if(stairLock>0){
        stairLock-=deltaTime;
    }

    player.jumpVelocity-=6.8*deltaTime;

    player.jumpHeight=Math.max(
        0,
        player.jumpHeight+
        player.jumpVelocity*deltaTime
    );

    if(
        player.jumpHeight===0 &&
        player.jumpVelocity<0
    ){
        player.jumpVelocity=0;
    }

    const speed=
        (running ? 4 : 2.5)*deltaTime;

    const forward=-joystick.y;
    const sideways=joystick.x;

    const moveX=(
        Math.cos(player.angle)*forward+
        Math.cos(player.angle+Math.PI/2)*sideways
    )*speed;

    const moveY=(
        Math.sin(player.angle)*forward+
        Math.sin(player.angle+Math.PI/2)*sideways
    )*speed;

    if(!solidAt(
        player.x+moveX+Math.sign(moveX)*.18,
        player.y
    )){
        player.x+=moveX;
    }

    if(!solidAt(
        player.x,
        player.y+moveY+Math.sign(moveY)*.18
    )){
        player.y+=moveY;
    }

    if(
        tileAt(player.x,player.y)===4 &&
        stairLock<=0
    ){
        changeFloor(
            player.floor===1 ? 2 : 1
        );
    }

    const enemySpeed=Math.min(
        .76+round*.08,
        1.6
    );

    for(const enemy of enemies){
        enemy.hitTime=Math.max(
            0,
            enemy.hitTime-deltaTime
        );

        const dx=player.x-enemy.x;
        const dy=player.y-enemy.y;
        const distance=Math.hypot(dx,dy);

        if(distance<.67){
            player.health-=
                Math.min(
                    16+round*1.5,
                    31
                )*deltaTime;

            hurtTime=.16;
        }else if(distance<10){
            const amount=
                enemySpeed*deltaTime;

            const nextX=
                enemy.x+
                dx/distance*amount;

            const nextY=
                enemy.y+
                dy/distance*amount;

            const xTile=
                tileAt(nextX,enemy.y);

            const yTile=
                tileAt(enemy.x,nextY);

            if(xTile===0 || xTile===4){
                enemy.x=nextX;
            }

            if(yTile===0 || yTile===4){
                enemy.y=nextY;
            }
        }
    }

    if(player.health<=0){
        player.health=0;
        playing=false;

        announce(
            "YOU DIED · 두 번 눌러 재시작",
            999
        );
    }
}

function drawWorld(){
    const sky=ctx.createLinearGradient(
        0,0,0,HEIGHT/2
    );

    sky.addColorStop(0,"#190403");

    sky.addColorStop(
        1,
        player.floor===1
            ? "#782010"
            : "#5b3020"
    );

    ctx.fillStyle=sky;
    ctx.fillRect(0,0,WIDTH,HEIGHT/2);

    ctx.fillStyle="#17120f";
    ctx.fillRect(0,HEIGHT/2,WIDTH,HEIGHT/2);

    const fov=Math.PI/3;
    const depthBuffer=[];

    for(let column=0;column<WIDTH;column+=2){
        const rayAngle=
            player.angle-
            fov/2+
            fov*column/WIDTH;

        const ray=castRay(rayAngle);

        const distance=
            ray.distance*
            Math.cos(rayAngle-player.angle);

        let wallHeight=Math.min(
            HEIGHT,
            HEIGHT/Math.max(distance,.01)
        );

        let wallY=
            HEIGHT/2-
            wallHeight/2+
            player.jumpHeight*95;

        depthBuffer[column/2]=distance;

        if(ray.type===2){
            ctx.fillStyle="#3e5946";
        }else if(ray.type===3){
            ctx.fillStyle="#624568";
        }else if(ray.type===5){
            ctx.fillStyle="#65442d";
        }else{
            ctx.fillStyle="#793025";
        }

        ctx.globalAlpha=Math.max(
            .2,
            1-distance/15
        );

        if(ray.type===5){
            wallHeight*=.48;

            wallY=
                HEIGHT/2+
                wallHeight*.05+
                player.jumpHeight*95;
        }

        ctx.fillRect(
            column,
            wallY,
            2,
            wallHeight
        );

        ctx.globalAlpha=1;
    }

    drawEnemies(depthBuffer,fov);
    drawPortal(depthBuffer,fov);
}

function drawEnemies(depthBuffer,fov){
    const visible=enemies
        .map(function(enemy){
            return{
                enemy:enemy,
                distance:Math.hypot(
                    enemy.x-player.x,
                    enemy.y-player.y
                ),
                angle:Math.atan2(
                    enemy.y-player.y,
                    enemy.x-player.x
                )
            };
        })
        .sort(function(a,b){
            return b.distance-a.distance;
        });

    for(const data of visible){
        let difference=
            data.angle-player.angle;

        difference=Math.atan2(
            Math.sin(difference),
            Math.cos(difference)
        );

        if(Math.abs(difference)>fov*.62){
            continue;
        }

        const screenX=
            WIDTH/2+
            difference/fov*WIDTH;

        const size=Math.min(
            300,
            380/Math.max(data.distance,.2)
        );

        const index=Math.max(
            0,
            Math.min(
                depthBuffer.length-1,
                Math.floor(screenX/2)
            )
        );

        if(
            data.distance>
            depthBuffer[index]+.25
        ){
            continue;
        }

        const centerY=
            HEIGHT/2-
            size*.12+
            player.jumpHeight*95;

        ctx.fillStyle=
            data.enemy.hitTime>0
                ? "#fff"
                : "#4d0b07";

        ctx.fillRect(
            screenX-size*.25,
            centerY,
            size*.5,
            size*.58
        );

        ctx.fillStyle=
            data.enemy.hitTime>0
                ? "#fff"
                : "#d13b20";

        ctx.beginPath();

        ctx.arc(
            screenX,
            centerY-size*.13,
            size*.25,
            0,
            Math.PI*2
        );

        ctx.fill();

        ctx.fillStyle="#e6cc92";

        ctx.beginPath();

        ctx.moveTo(
            screenX-size*.18,
            centerY-size*.27
        );

        ctx.lineTo(
            screenX-size*.34,
            centerY-size*.49
        );

        ctx.lineTo(
            screenX-size*.06,
            centerY-size*.31
        );

        ctx.fill();

        ctx.beginPath();

        ctx.moveTo(
            screenX+size*.18,
            centerY-size*.27
        );

        ctx.lineTo(
            screenX+size*.34,
            centerY-size*.49
        );

        ctx.lineTo(
            screenX+size*.06,
            centerY-size*.31
        );

        ctx.fill();

        ctx.fillStyle="#fff04e";

        ctx.fillRect(
            screenX-size*.13,
            centerY-size*.2,
            size*.08,
            size*.06
        );

        ctx.fillRect(
            screenX+size*.05,
            centerY-size*.2,
            size*.08,
            size*.06
        );
    }
}

/* 직관적으로 보이는 층 이동 포탈 */

function drawPortal(depthBuffer,fov){
    const portal=PORTALS[player.floor];

    const dx=portal.x-player.x;
    const dy=portal.y-player.y;

    const distance=Math.hypot(dx,dy);

    let difference=
        Math.atan2(dy,dx)-player.angle;

    difference=Math.atan2(
        Math.sin(difference),
        Math.cos(difference)
    );

    if(Math.abs(difference)>fov*.58){
        return;
    }

    const screenX=
        WIDTH/2+
        difference/fov*WIDTH;

    const depthIndex=Math.max(
        0,
        Math.min(
            depthBuffer.length-1,
            Math.floor(screenX/2)
        )
    );

    if(
        distance>
        depthBuffer[depthIndex]+.3
    ){
        return;
    }

    const size=Math.min(
        320,
        430/Math.max(distance,.2)
    );

    const centerY=
        HEIGHT/2+
        player.jumpHeight*95;

    ctx.save();

    ctx.globalAlpha=
        .82+
        .18*Math.sin(
            performance.now()*.01
        );

    const glow=
        ctx.createRadialGradient(
            screenX,
            centerY,
            5,
            screenX,
            centerY,
            size*.44
        );

    glow.addColorStop(0,"#ffffff");
    glow.addColorStop(.22,"#37eaff");
    glow.addColorStop(.65,"#713cff");
    glow.addColorStop(1,"rgba(18,0,43,0)");

    ctx.fillStyle=glow;

    ctx.beginPath();

    ctx.ellipse(
        screenX,
        centerY,
        size*.44,
        size*.7,
        0,
        0,
        Math.PI*2
    );

    ctx.fill();

    ctx.strokeStyle="#88f6ff";
    ctx.lineWidth=Math.max(
        3,
        size*.035
    );

    ctx.beginPath();

    ctx.ellipse(
        screenX,
        centerY,
        size*.31,
        size*.59,
        0,
        0,
        Math.PI*2
    );

    ctx.stroke();

    ctx.fillStyle="#ffffff";
    ctx.font=
        "bold "+
        Math.max(12,size*.08)+
        "px Arial";

    ctx.textAlign="center";

    ctx.fillText(
        portal.label,
        screenX,
        centerY+size*.8
    );

    ctx.textAlign="left";
    ctx.restore();
}

function drawHud(){
    /* 총 */

    ctx.fillStyle="#302925";

    ctx.fillRect(
        WIDTH/2-62,
        HEIGHT-132+
        player.jumpHeight*30,
        124,
        132
    );

    ctx.fillStyle="#101010";

    ctx.fillRect(
        WIDTH/2-22,
        HEIGHT-205+
        player.jumpHeight*30,
        44,
        116
    );

    if(muzzleFlash>0){
        ctx.fillStyle="#ffd447";

        ctx.beginPath();

        ctx.arc(
            WIDTH/2,
            HEIGHT-207+
            player.jumpHeight*30,
            42,
            0,
            Math.PI*2
        );

        ctx.fill();
        muzzleFlash--;
    }

    /* 조준점 */

    ctx.strokeStyle="#fff";
    ctx.lineWidth=2;

    ctx.beginPath();

    ctx.moveTo(WIDTH/2-12,HEIGHT/2);
    ctx.lineTo(WIDTH/2+12,HEIGHT/2);

    ctx.moveTo(WIDTH/2,HEIGHT/2-12);
    ctx.lineTo(WIDTH/2,HEIGHT/2+12);

    ctx.stroke();

    /* 상태 표시 */

    ctx.fillStyle="rgba(0,0,0,.87)";
    ctx.fillRect(0,HEIGHT-64,WIDTH,64);

    ctx.font="bold 22px monospace";

    ctx.fillStyle=
        player.health<30
            ? "#ff3322"
            : "#f0a73b";

    ctx.fillText(
        "HP "+Math.ceil(player.health),
        18,
        HEIGHT-25
    );

    ctx.fillStyle="#eee";

    ctx.fillText(
        "AMMO "+player.ammo+"/12",
        WIDTH/2-78,
        HEIGHT-25
    );

    ctx.fillStyle="#f0a73b";

    ctx.fillText(
        "R"+round+
        " F"+player.floor+
        " ENEMY "+enemies.length,
        WIDTH-245,
        HEIGHT-25
    );

    /* 가장 가까운 적 방향 */

    if(enemies.length>0){
        const nearest=enemies.reduce(
            function(a,b){
                const aDistance=Math.hypot(
                    a.x-player.x,
                    a.y-player.y
                );

                const bDistance=Math.hypot(
                    b.x-player.x,
                    b.y-player.y
                );

                return aDistance<bDistance
                    ? a
                    : b;
            }
        );

        let direction=
            Math.atan2(
                nearest.y-player.y,
                nearest.x-player.x
            )-player.angle;

        direction=Math.atan2(
            Math.sin(direction),
            Math.cos(direction)
        );

        ctx.save();
        ctx.translate(WIDTH/2,42);
        ctx.rotate(direction);

        ctx.fillStyle="#ff3b21";

        ctx.beginPath();
        ctx.moveTo(0,-17);
        ctx.lineTo(-11,9);
        ctx.lineTo(11,9);
        ctx.fill();

        ctx.restore();
    }

    if(messageTime>0){
        ctx.fillStyle="rgba(0,0,0,.72)";

        ctx.fillRect(
            WIDTH/2-230,
            HEIGHT/2-45,
            460,
            90
        );

        ctx.fillStyle="#ef4827";
        ctx.font="bold 34px Impact";
        ctx.textAlign="center";

        ctx.fillText(
            message,
            WIDTH/2,
            HEIGHT/2+12
        );

        ctx.textAlign="left";
    }
}

/* 플레이어 피격 효과 */

function drawDamageEffect(){
    if(hurtTime<=0){
        return;
    }

    const alpha=Math.min(
        .42,
        hurtTime*2.6
    );

    ctx.fillStyle=
        "rgba(255,0,0,"+
        alpha+
        ")";

    ctx.fillRect(
        0,
        0,
        WIDTH,
        HEIGHT
    );

    ctx.strokeStyle="#ff2418";
    ctx.lineWidth=18;

    ctx.strokeRect(
        5,
        5,
        WIDTH-10,
        HEIGHT-10
    );
}

function gameLoop(timestamp){
    const deltaTime=Math.min(
        .04,
        (timestamp-lastFrame)/1000 || 0
    );

    lastFrame=timestamp;

    update(deltaTime);

    ctx.save();

    /* 피격 시 화면 흔들림 */

    if(hurtTime>0){
        ctx.translate(
            (Math.random()-.5)*12,
            (Math.random()-.5)*12
        );
    }

    drawWorld();
    drawHud();
    drawDamageEffect();

    ctx.restore();

    requestAnimationFrame(gameLoop);
}

/* 시작 */

document
    .getElementById("startButton")
    .onclick=function(){
        document
            .getElementById("start")
            .style.display="none";

        resetGame();
    };

/* 이동 조이스틱 */

const joystickBase=
    document.getElementById("joystick");

const joystickKnob=
    document.getElementById("knob");

let joystickPointer=null;

function moveJoystick(event){
    const rect=
        joystickBase.getBoundingClientRect();

    let dx=
        event.clientX-
        rect.left-
        rect.width/2;

    let dy=
        event.clientY-
        rect.top-
        rect.height/2;

    const maximum=rect.width*.31;
    const length=Math.hypot(dx,dy);

    if(length>maximum){
        dx*=maximum/length;
        dy*=maximum/length;
    }

    joystick.x=dx/maximum;
    joystick.y=dy/maximum;

    joystickKnob.style.transform=
        "translate("+dx+"px,"+dy+"px)";
}

joystickBase.onpointerdown=function(event){
    event.preventDefault();

    joystickPointer=event.pointerId;

    joystickBase.setPointerCapture(
        joystickPointer
    );

    moveJoystick(event);
};

joystickBase.onpointermove=function(event){
    if(event.pointerId===joystickPointer){
        moveJoystick(event);
    }
};

function stopJoystick(event){
    if(event.pointerId!==joystickPointer){
        return;
    }

    joystickPointer=null;
    joystick.x=0;
    joystick.y=0;

    joystickKnob.style.transform=
        "translate(0,0)";
}

joystickBase.onpointerup=stopJoystick;
joystickBase.onpointercancel=stopJoystick;

/*
RUN 토글:
한 번 누르면 계속 달리고
다시 누르면 일반 이동으로 돌아옵니다.
*/

const runButton=
    document.getElementById("runButton");

runButton.onpointerdown=function(event){
    event.preventDefault();

    running=!running;

    runButton.classList.toggle(
        "running",
        running
    );

    runButton.textContent=
        running ? "RUN ON" : "RUN";
};

/* 점프 */

const jumpButton=
    document.getElementById("jumpButton");

jumpButton.onpointerdown=function(event){
    event.preventDefault();
    jumpButton.classList.add("active");
    jump();
};

jumpButton.onpointerup=
jumpButton.onpointercancel=function(event){
    event.preventDefault();
    jumpButton.classList.remove("active");
};

/* 발사 */

const fireButton=
    document.getElementById("fireButton");

fireButton.onpointerdown=function(event){
    event.preventDefault();
    fireButton.classList.add("active");
    shoot();
};

fireButton.onpointerup=
fireButton.onpointercancel=function(event){
    event.preventDefault();
    fireButton.classList.remove("active");
};

/* 빈 화면 드래그로 시점 회전 */

let lookPointer=null;
let previousLookX=0;

canvas.onpointerdown=function(event){
    if(event.pointerType==="touch"){
        lookPointer=event.pointerId;
        previousLookX=event.clientX;

        canvas.setPointerCapture(
            lookPointer
        );
    }
};

canvas.onpointermove=function(event){
    if(event.pointerId===lookPointer){
        player.angle+=
            (event.clientX-previousLookX)*.006;

        previousLookX=event.clientX;
    }
};

canvas.onpointerup=
canvas.onpointercancel=function(event){
    if(event.pointerId===lookPointer){
        lookPointer=null;
    }
};

/* 사망 후 화면 두 번 터치 */

canvas.ondblclick=function(){
    if(
        !playing &&
        player.health<=0
    ){
        resetGame();
    }
};

resetGame();
requestAnimationFrame(gameLoop);
</script>

</body>
</html>
'''

components.html(
    GAME,
    height=760,
    scrolling=False
)

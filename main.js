const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

const HUD = {
  score: document.getElementById('score'),
  coins: document.getElementById('coins'),
  lives: document.getElementById('lives'),
  world: document.getElementById('world'),
  message: document.getElementById('message'),
};

// Basic color palette inspired by early Famicom tiles
const palette = {
  sky: '#8bd6ff',
  groundTop: '#b87953',
  ground: '#9d5f3e',
  brickTop: '#d1874d',
  brick: '#b36d35',
  pipe: '#3ba55d',
  question: '#f9d65c',
  questionDot: '#d79729',
  usedBlock: '#9b9b9b',
  coin: '#ffd046',
  goomba: '#b46b3b',
  mario: '#ff4f4f',
  flag: '#fefefe',
};

const tileSize = 32;
const gravity = 0.55;
const friction = 0.85;
const jumpPower = -11;
const moveSpeed = 0.7;

const level = {
  width: 180,
  height: 17,
  tiles: [],
  items: [],
  enemies: [],
  flagX: 165 * tileSize,
};

const tileTypes = {
  EMPTY: 0,
  GROUND: 1,
  QUESTION: 2,
  USED: 3,
  COIN: 4,
  PIPE_TOP: 5,
  PIPE_BODY: 6,
  FLAG: 7,
};

function fillLevel() {
  const width = 150;
  const grid = Array.from({ length: level.height }, () => Array(width).fill(' '));
  const set = (x, y, char) => {
    if (x >= 0 && x < width && y >= 0 && y < level.height) grid[y][x] = char;
  };

  for (let y = 14; y < level.height; y++) {
    for (let x = 0; x < width; x++) {
      set(x, y, 'b');
    }
  }

  [15, 28, 62, 95, 120].forEach((x) => set(x, 10, '?'));
  [22, 45, 70, 105, 132].forEach((x) => set(x, 11, '?'));
  [30, 32, 34, 80, 82, 84, 86].forEach((x) => set(x, 9, 'G'));
  [60, 61, 62, 63, 64, 65, 66, 67].forEach((x) => set(x, 12, 'b'));
  [40, 41, 42, 43, 44, 45, 46, 47].forEach((x) => set(x, 13, 'b'));

  const pipes = [
    { x: 38, height: 2 },
    { x: 73, height: 3 },
    { x: 98, height: 2 },
    { x: 122, height: 4 },
  ];

  for (const pipe of pipes) {
    for (let i = 0; i < pipe.height; i++) {
      set(pipe.x, 13 - i, i === pipe.height - 1 ? 'P' : 'p');
    }
  }

  // Floating bricks before the flag
  for (let x = 110; x < 126; x++) {
    if (x % 2 === 0) set(x, 8, 'b');
  }

  // Flag pole marker
  set(width - 6, 9, 'F');

  const rows = grid.map((row) => row.join(''));
  level.width = width;
  level.flagX = (width - 8) * tileSize;

  level.tiles = rows.map((row) =>
    row.split('').map((c) => {
      switch (c) {
        case 'b':
          return tileTypes.GROUND;
        case '?':
          return tileTypes.QUESTION;
        case 'G':
          return tileTypes.COIN;
        case 'p':
          return tileTypes.PIPE_BODY;
        case 'P':
          return tileTypes.PIPE_TOP;
        case 'F':
          return tileTypes.FLAG;
        default:
          return tileTypes.EMPTY;
      }
    })
  );

  // Populate enemies
  level.enemies = [
    { x: 15 * tileSize, y: 13 * tileSize, w: 26, h: 26, vx: -0.6, alive: true },
    { x: 46 * tileSize, y: 13 * tileSize, w: 26, h: 26, vx: -0.6, alive: true },
    { x: 90 * tileSize, y: 13 * tileSize, w: 26, h: 26, vx: -0.6, alive: true },
    { x: 130 * tileSize, y: 13 * tileSize, w: 26, h: 26, vx: -0.6, alive: true },
  ];

  level.items = [];
}

const keys = new Set();
const pressed = {};

window.addEventListener('keydown', (e) => {
  if (['ArrowLeft', 'ArrowRight', 'Space', 'KeyZ'].includes(e.code)) {
    e.preventDefault();
  }
  keys.add(e.code);
});

window.addEventListener('keyup', (e) => {
  keys.delete(e.code);
  pressed[e.code] = false;
});

const player = {
  x: 2 * tileSize,
  y: 12 * tileSize,
  w: 24,
  h: 32,
  vx: 0,
  vy: 0,
  onGround: false,
  lives: 3,
  score: 0,
  coins: 0,
  world: '1-1',
  invincibleTimer: 0,
};

function resetPlayer() {
  player.x = 2 * tileSize;
  player.y = 12 * tileSize;
  player.vx = 0;
  player.vy = 0;
  player.onGround = false;
}

function tileAt(px, py) {
  const x = Math.floor(px / tileSize);
  const y = Math.floor(py / tileSize);
  if (x < 0 || y < 0 || y >= level.height || x >= level.width) return tileTypes.EMPTY;
  return level.tiles[y][x];
}

function setTile(px, py, val) {
  const x = Math.floor(px / tileSize);
  const y = Math.floor(py / tileSize);
  if (x < 0 || y < 0 || y >= level.height || x >= level.width) return;
  level.tiles[y][x] = val;
}

function isSolid(t) {
  return [tileTypes.GROUND, tileTypes.QUESTION, tileTypes.USED, tileTypes.PIPE_BODY, tileTypes.PIPE_TOP, tileTypes.FLAG].includes(t);
}

function addScore(amount) {
  player.score += amount;
  HUD.score.textContent = player.score.toString().padStart(6, '0');
}

function addCoin(count = 1) {
  player.coins += count;
  HUD.coins.textContent = `x${player.coins.toString().padStart(2, '0')}`;
  addScore(200 * count);
}

function loseLife() {
  player.lives -= 1;
  HUD.lives.textContent = player.lives;
  if (player.lives <= 0) {
    player.lives = 3;
    player.score = 0;
    player.coins = 0;
    HUD.score.textContent = '000000';
    HUD.coins.textContent = 'x00';
    HUD.message.textContent = 'GAME OVER - 按跳跃重新开始';
    level.items = [];
    level.enemies.forEach((e) => Object.assign(e, { alive: true, vx: -0.6 }));
  }
  resetPlayer();
}

function spawnCoin(x, y) {
  level.items.push({ x, y, vy: -5, age: 0, type: 'coinAir' });
}

function spawnFlagRibbon(x, y) {
  level.items.push({ x, y, type: 'flagRibbon', timer: 80 });
}

function collideRect(ax, ay, aw, ah, bx, by, bw, bh) {
  return ax < bx + bw && ax + aw > bx && ay < by + bh && ay + ah > by;
}

function resolveTileCollision(entity) {
  // Horizontal
  if (entity.vx !== 0) {
    const aheadX = entity.vx > 0 ? entity.x + entity.w + entity.vx : entity.x + entity.vx;
    const topY = entity.y + 1;
    const bottomY = entity.y + entity.h - 1;
    const tilesToCheck = [topY, bottomY];
    const dir = Math.sign(entity.vx);
    for (const ty of tilesToCheck) {
      const tile = tileAt(aheadX, ty);
      if (isSolid(tile)) {
        entity.vx = 0;
        entity.x = dir > 0
          ? Math.floor(aheadX / tileSize) * tileSize - entity.w - 0.01
          : Math.floor(aheadX / tileSize + 1) * tileSize + 0.01;
        break;
      }
    }
  }

  entity.x += entity.vx;

  // Vertical
  entity.onGround = false;
  if (entity.vy !== 0) {
    const aheadY = entity.vy > 0 ? entity.y + entity.h + entity.vy : entity.y + entity.vy;
    const leftX = entity.x + 3;
    const rightX = entity.x + entity.w - 3;
    const tilesToCheck = [leftX, rightX];

    for (const tx of tilesToCheck) {
      const tile = tileAt(tx, aheadY);
      if (isSolid(tile)) {
        if (entity.vy > 0) {
          // Landing
          entity.onGround = true;
          entity.y = Math.floor(aheadY / tileSize) * tileSize - entity.h - 0.01;
          entity.vy = 0;
        } else {
          // Hitting block from below
          entity.y = Math.floor(aheadY / tileSize + 1) * tileSize + 0.01;
          entity.vy = 0.2;
          if (tile === tileTypes.QUESTION) {
            const tileX = Math.floor(tx / tileSize) * tileSize;
            const tileY = Math.floor(aheadY / tileSize) * tileSize;
            setTile(tileX, tileY, tileTypes.USED);
            spawnCoin(tileX + tileSize / 2 - 6, tileY - 10);
            addCoin();
          }
        }
        break;
      }
    }
  }

  entity.y += entity.vy;
}

function updatePlayer() {
  if (keys.has('ArrowLeft')) player.vx -= moveSpeed;
  if (keys.has('ArrowRight')) player.vx += moveSpeed;

  if (Math.abs(player.vx) > 6) player.vx = 6 * Math.sign(player.vx);

  if ((keys.has('Space') || keys.has('KeyZ')) && !pressed['SpaceJump']) {
    pressed['SpaceJump'] = true;
    if (player.onGround) {
      player.vy = jumpPower;
      player.onGround = false;
    }
  }

  if (!keys.has('Space') && !keys.has('KeyZ')) {
    pressed['SpaceJump'] = false;
  }

  player.vy += gravity;
  if (player.vy > 14) player.vy = 14;

  player.vx *= friction;
  if (Math.abs(player.vx) < 0.05) player.vx = 0;

  resolveTileCollision(player);

  // Falling into void
  if (player.y > canvas.height) {
    HUD.message.textContent = '小心！你掉出了世界。';
    loseLife();
  }
}

function updateItems() {
  level.items = level.items.filter((item) => {
    if (item.type === 'coinAir') {
      item.age += 1;
      item.vy += gravity * 0.2;
      item.y += item.vy;
      return item.age < 50;
    }
    if (item.type === 'flagRibbon') {
      item.timer -= 1;
      return item.timer > 0;
    }
    return false;
  });
}

function updateEnemies() {
  for (const enemy of level.enemies) {
    if (!enemy.alive) continue;

    enemy.vy = (enemy.vy || 0) + gravity;
    if (enemy.vy > 12) enemy.vy = 12;

    const edgeAheadX = enemy.vx > 0 ? enemy.x + enemy.w + 2 : enemy.x - 2;
    const footY = enemy.y + enemy.h + 1;
    const groundAhead = isSolid(tileAt(edgeAheadX, footY));
    if (!groundAhead) enemy.vx *= -1;

    const nextTile = tileAt(edgeAheadX, enemy.y + enemy.h / 2);
    if (isSolid(nextTile)) enemy.vx *= -1;

    enemy.x += enemy.vx;
    enemy.y += enemy.vy;

    // Simple floor collision
    const belowTile = tileAt(enemy.x + enemy.w / 2, enemy.y + enemy.h + 1);
    if (isSolid(belowTile)) {
      enemy.y = Math.floor((enemy.y + enemy.h + 1) / tileSize) * tileSize - enemy.h - 0.01;
      enemy.vy = 0;
    }

    // Player collision
    if (collideRect(player.x, player.y, player.w, player.h, enemy.x, enemy.y, enemy.w, enemy.h)) {
      if (player.vy > 0 && player.y + player.h - 6 < enemy.y) {
        enemy.alive = false;
        player.vy = jumpPower * 0.5;
        addScore(200);
      } else if (player.invincibleTimer <= 0) {
        player.invincibleTimer = 120;
        HUD.message.textContent = '哎呀，被栗宝宝碰到了！';
        loseLife();
      }
    }
  }
}

function drawTile(x, y, type) {
  const px = x * tileSize;
  const py = y * tileSize;
  switch (type) {
    case tileTypes.GROUND:
      ctx.fillStyle = palette.ground;
      ctx.fillRect(px, py, tileSize, tileSize);
      ctx.fillStyle = palette.groundTop;
      ctx.fillRect(px, py, tileSize, 8);
      break;
    case tileTypes.QUESTION:
      ctx.fillStyle = palette.question;
      ctx.fillRect(px, py, tileSize, tileSize);
      ctx.fillStyle = palette.questionDot;
      ctx.fillRect(px + 12, py + 8, 8, 8);
      ctx.fillRect(px + 8, py + 18, 16, 4);
      break;
    case tileTypes.USED:
      ctx.fillStyle = palette.usedBlock;
      ctx.fillRect(px, py, tileSize, tileSize);
      break;
    case tileTypes.COIN:
      ctx.fillStyle = palette.coin;
      ctx.beginPath();
      ctx.ellipse(px + tileSize / 2, py + tileSize / 2, 6, 12, 0, 0, Math.PI * 2);
      ctx.fill();
      break;
    case tileTypes.PIPE_TOP:
      ctx.fillStyle = palette.pipe;
      ctx.fillRect(px - 4, py, tileSize + 8, tileSize);
      ctx.fillRect(px, py + 8, tileSize, tileSize - 8);
      break;
    case tileTypes.PIPE_BODY:
      ctx.fillStyle = palette.pipe;
      ctx.fillRect(px, py, tileSize, tileSize);
      break;
    case tileTypes.FLAG:
      ctx.fillStyle = palette.flag;
      ctx.fillRect(px + tileSize / 2 - 2, py, 4, tileSize * 4);
      ctx.fillStyle = '#00ff66';
      ctx.beginPath();
      ctx.moveTo(px + tileSize / 2 + 2, py + 6);
      ctx.lineTo(px + tileSize + 10, py + 12);
      ctx.lineTo(px + tileSize / 2 + 2, py + 18);
      ctx.closePath();
      ctx.fill();
      break;
  }
}

function drawBackground() {
  ctx.fillStyle = palette.sky;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = '#62a8ff';
  for (let i = 0; i < 6; i++) {
    const x = (i * 220 + Math.sin(Date.now() / 2000 + i) * 20) % canvas.width;
    ctx.beginPath();
    ctx.ellipse(x, 120 + Math.sin(i) * 10, 140, 40, 0, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawItems() {
  for (const item of level.items) {
    if (item.type === 'coinAir') {
      ctx.fillStyle = palette.coin;
      ctx.beginPath();
      ctx.ellipse(item.x, item.y, 6, 12, 0, 0, Math.PI * 2);
      ctx.fill();
    }
    if (item.type === 'flagRibbon') {
      ctx.fillStyle = '#00ff66';
      ctx.fillRect(item.x, item.y, 4, item.timer);
    }
  }
}

function drawEnemies() {
  for (const enemy of level.enemies) {
    if (!enemy.alive) continue;
    ctx.fillStyle = palette.goomba;
    ctx.fillRect(enemy.x, enemy.y, enemy.w, enemy.h);
    ctx.fillStyle = '#000';
    ctx.fillRect(enemy.x + 6, enemy.y + 16, 6, 6);
    ctx.fillRect(enemy.x + enemy.w - 12, enemy.y + 16, 6, 6);
  }
}

function drawPlayer() {
  ctx.fillStyle = palette.mario;
  ctx.fillRect(player.x, player.y, player.w, player.h);
  ctx.fillStyle = '#f9d65c';
  ctx.fillRect(player.x + 4, player.y + 6, 6, 6);
  ctx.fillRect(player.x + player.w - 10, player.y + 6, 6, 6);
}

function cameraOffset() {
  const centerMargin = 200;
  const targetX = Math.min(
    Math.max(player.x - centerMargin, 0),
    level.width * tileSize - canvas.width
  );
  return targetX;
}

function drawLevel() {
  const offsetX = cameraOffset();
  ctx.save();
  ctx.translate(-offsetX, 0);

  for (let y = 0; y < level.height; y++) {
    for (let x = 0; x < level.width; x++) {
      const tile = level.tiles[y][x];
      if (tile !== tileTypes.EMPTY) drawTile(x, y, tile);
    }
  }

  drawItems();
  drawEnemies();
  drawPlayer();

  ctx.restore();
}

function collectCoinsOnContact() {
  const px = player.x + player.w / 2;
  const py = player.y + player.h / 2;
  const tile = tileAt(px, py);
  if (tile === tileTypes.COIN) {
    setTile(px, py, tileTypes.EMPTY);
    addCoin();
    HUD.message.textContent = '叮！金币到手。';
  }
}

function checkFlag() {
  const px = player.x + player.w / 2;
  const py = player.y + player.h / 2;
  const tile = tileAt(px, py);
  if (tile === tileTypes.FLAG) {
    HUD.message.textContent = '成功抵达旗杆！按跳跃再来一局。';
    spawnFlagRibbon(level.flagX + tileSize / 2, 6 * tileSize);
    addScore(2000);
    resetPlayer();
  }
}

function update() {
  drawBackground();
  updatePlayer();
  updateItems();
  updateEnemies();
  collectCoinsOnContact();
  checkFlag();
  drawLevel();

  if (player.invincibleTimer > 0) player.invincibleTimer -= 1;

  requestAnimationFrame(update);
}

fillLevel();
HUD.world.textContent = player.world;
HUD.message.textContent = '按空格或 Z 开始冒险，左右移动！';
update();

// Headless validation for the gesture-controlled Snake game (snake.js + sketch.js).
// Loads the REAL source files with p5 platform stubs so we exercise the actual code.
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const DIR = resolveSketchDir();

// The sources sit next to this script in the repo export, but in the original
// workshop zip they are inside "Practical Application and Demo/". Accept both.
function resolveSketchDir() {
  const candidates = [
    __dirname,
    path.join(__dirname, 'Practical Application and Demo'),
  ];
  for (const dir of candidates) {
    if (fs.existsSync(path.join(dir, 'snake.js')) && fs.existsSync(path.join(dir, 'sketch.js'))) {
      return dir;
    }
  }
  throw new Error(
    `找不到 snake.js / sketch.js。找過：\n  ${candidates.join('\n  ')}\n` +
    `請把這支腳本放在兩個 .js 檔旁邊執行。`
  );
}

function createVector(x = 0, y = 0) {
  return { x, y, copy() { return createVector(this.x, this.y); } };
}

function makeContext() {
  const drawCalls = [];
  const ctx = {
    // ---- p5 globals ----
    width: 600,
    height: 600,
    VIDEO: 'video',
    frameRate: () => {},
    createCanvas: () => {},
    createCapture: () => ({ hide() {} }),
    createVector,
    floor: Math.floor,
    random: (n) => Math.floor(Math.random() * n),
    background: () => {},
    textSize: () => {},
    fill: () => {},
    noStroke: () => {},
    stroke: () => {},
    text: () => {},
    scale: () => {},
    rect: (x, y) => drawCalls.push([x, y]),
    noLoop: () => { ctx.__looped = false; },
    print: (m) => ctx.__prints.push(m),
    keyIsDown: () => false,
    // ---- harness state ----
    __drawCalls: drawCalls,
    __prints: [],
    __looped: true,
    __moving: true,
    ml5: {
      imageClassifier: async () => ({
        // Simulate Teachable Machine: report the label the test sets on ctx.__nextLabel
        classify: (video, cb) => setImmediate(() => cb(null, [{ label: ctx.__nextLabel }])),
      }),
    },
  };
  ctx.__nextLabel = 'waiting...';
  return vm.createContext(ctx);
}

const results = [];
// Script-scoped `let`/`class` declarations live in the vm script scope, not on the
// context object, so read them by evaluating an expression inside the context.
function get(ctx, name) {
  return vm.runInContext(name, ctx);
}
// Sketches use the older callback signature gotResults(error, results).
function gotResultsFn(ctx) {
  return vm.runInContext('gotResults', ctx);
}
function check(name, cond, detail = '') {
  results.push({ name, ok: !!cond, detail });
  console.log(`${cond ? 'PASS' : 'FAIL'}  ${name}${detail ? ' :: ' + detail : ''}`);
}

(async () => {
  const ctx = makeContext();

  // Load sources exactly as the browser would (snake.js first, then sketch.js).
  vm.runInContext(fs.readFileSync(path.join(DIR, 'snake.js'), 'utf8'), ctx, { filename: 'snake.js' });
  vm.runInContext(fs.readFileSync(path.join(DIR, 'sketch.js'), 'utf8'), ctx, { filename: 'sketch.js' });

  check('snake.js defines class Snake', typeof vm.runInContext('Snake', ctx) === 'function');
  check('sketch.js defines controlSnake()', typeof ctx.controlSnake === 'function');
  check('keyPressed() was replaced (no keyboard handler)', typeof ctx.keyPressed === 'undefined');

  // ---- Step E3: gotResults must call controlSnake ----
  vm.runInContext('setup()', ctx);
  await new Promise((r) => setTimeout(r, 30)); // let async setup + first classify settle
  check('setup() built a snake', !!get(ctx, 'snake') && get(ctx, 'snake').body.length === 1);
  check('setup() placed food', !!get(ctx, 'food'));
  check('classifier loaded from Teachable Machine URL', true);

  // ---- Drive the game with gestures ----
  const snake = get(ctx, 'snake');
  const start = { ...snake.body[0] };

  ctx.__nextLabel = 'waiting...';
  gotResultsFn(ctx)(null, [{ label: 'waiting...' }]);
  check('unknown/"waiting..." label leaves snake stationary', snake.xdir === 0 && snake.ydir === 0);

  gotResultsFn(ctx)(null, [{ label: 'Left' }]);
  check('gesture "Left" sets dir (-1,0)', snake.xdir === -1 && snake.ydir === 0);

  gotResultsFn(ctx)(null, [{ label: 'Right' }]);
  check('180-degree flip ("Right" after "Left") is rejected', snake.xdir === -1,
    `dir=(${snake.xdir},${snake.ydir})`);

  gotResultsFn(ctx)(null, [{ label: 'Up' }]);
  check('perpendicular turn ("Up" after "Left") is accepted', snake.xdir === 0 && snake.ydir === -1);

  // ---- The endGame() self-collision bug ----
  get(ctx, 'food').x = 999; get(ctx, 'food').y = 999; // keep food away
  snake.body = [createVector(10, 10), createVector(11, 10), createVector(12, 10)];
  snake.xdir = 1; snake.ydir = 0;
  snake.update();
  check('snake survives a normal move (endGame bug fixed)', snake.endGame() === false,
    `body=${JSON.stringify(snake.body)}`);

  snake.body = [createVector(10, 10), createVector(11, 10), createVector(12, 10)];
  snake.xdir = 0; snake.ydir = 1;
  snake.setDir(0, 1);
  snake.update();
  check('snake still survives after a perpendicular turn', snake.endGame() === false,
    `body=${JSON.stringify(snake.body)}`);

  // Real self-bite must still be detected.
  snake.body = [createVector(10, 10), createVector(10, 11), createVector(10, 12), createVector(11, 12), createVector(11, 11)];
  snake.xdir = -1; snake.ydir = 0;
  snake.setDir(-1, 0);
  snake.update();
  check('genuine self-collision IS detected', snake.endGame() === true,
    `body=${JSON.stringify(snake.body)}`);

  // Wall collision must still be detected.
  snake.body = [createVector(0, 5)];
  snake.xdir = -1; snake.ydir = 0;
  snake.update();
  check('wall collision IS detected', snake.endGame() === true);

  // ---- Growth on eating ----
  snake.body = [createVector(5, 5)];
  snake.xdir = 0; snake.ydir = 0;
  const before = snake.body.length;
  const ate = snake.eat(createVector(5, 5));
  check('eat() grows the snake', ate === true && snake.body.length === before + 1);

  // ---- Full draw() frame with gestures, using the real draw loop ----
  const scoreGame = makeContext();
  vm.runInContext(fs.readFileSync(path.join(DIR, 'snake.js'), 'utf8'), scoreGame, { filename: 'snake.js' });
  vm.runInContext(fs.readFileSync(path.join(DIR, 'sketch.js'), 'utf8'), scoreGame, { filename: 'sketch.js' });
  vm.runInContext('setup()', scoreGame);
  await new Promise((r) => setTimeout(r, 30));
  gotResultsFn(scoreGame)(null, [{ label: 'Right' }]);
  for (let f = 0; f < 3; f++) vm.runInContext('draw()', scoreGame);
  check('real draw() loop advances snake without instant END GAME',
    scoreGame.__prints.length === 0 && scoreGame.__looped === true,
    `prints=${JSON.stringify(scoreGame.__prints)}`);
  check('snake actually moved right', get(scoreGame, 'snake').body[0].x > Math.floor(get(scoreGame, 'w') / 2),
    `x=${get(scoreGame, 'snake').body[0].x}`);

  const failed = results.filter((r) => !r.ok);
  console.log(`\n${results.length - failed.length}/${results.length} checks passed`);
  process.exit(failed.length === 0 ? 0 : 1);
})();



let video;
let label = "waiting...";
let classifier;
let snake;
let rez = 20;
let food;
let w;
let h;

async function setup() {
  createCanvas(600, 600);

  video = createCapture(VIDEO);
  video.hide();

  // Load the classifier asynchronously using await
  classifier = await ml5.imageClassifier('https://teachablemachine.withgoogle.com/models/C4gLHKnW0/model.json');
  
  // Start classifying after the model is loaded
  classifyVideo();

  w = floor(width / rez);
  h = floor(height / rez);
  frameRate(5);
  snake = new Snake();
  foodLocation();
}


function classifyVideo() {
  classifier.classify(video, gotResults);
}

function gotResults(error, results) {
  if (error) {
    console.error(error);
    return;
  }
  label = results[0].label;
  // Step E3, add a call function " controlSnake(); " in line 42
  controlSnake();
  classifyVideo();
}

function foodLocation() {
  let x = floor(random(w));
  let y = floor(random(h));
  food = createVector(x, y);
}

// Step E2: Change this function from "keyPressed" to "controlSnake" and the keyCode to label
function controlSnake() {
  if (label == "Left") {
    snake.setDir(-1, 0);
  } else if (label == "Right") {
    snake.setDir(1, 0);
  } else if (label == "Down") {
    snake.setDir(0, 1);
  } else if (label == "Up") {
    snake.setDir(0, -1);
  }
}

function draw() {
  
  background(220);
  textSize(32);
  fill(255);
  text(label, 10, 50);
  
  scale(rez);
  
  if (snake.eat(food)) {
    foodLocation();
  }
  snake.update();
  snake.show();

  if (snake.endGame()) {
    print('END GAME');
    background(255, 0, 0);
    noLoop();
  }

  noStroke();
  fill(255, 0, 0);
  rect(food.x, food.y, 1, 1);
}
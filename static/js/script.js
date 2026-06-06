let board = $("#board");
let aiPlaying = false;
// colors
// --imperial-red: #f94144ff;
// --orange-crayola: #f3722cff;
// --carrot-orange: #f8961eff;
// --coral: #f9844aff;
// --saffron: #f9c74fff;
// --pistachio: #90be6dff;
// --zomp: #43aa8bff;
// --dark-cyan: #4d908eff;
// --paynes-gray: #577590ff;
// --cerulean: #277da1ff;

// get variable from style.css
let primaryColor = getComputedStyle(document.documentElement).getPropertyValue(
  "--primary"
);
let secondaryColor = getComputedStyle(
  document.documentElement
).getPropertyValue("--secondary");

colors = {
  0: secondaryColor,
  2: "#577590ff",
  8: "#277da1ff",
  4: "#f94144ff",
  32: "#f9844aff",
  16: "#f9c74fff",
  64: "#43aa8bff",
  128: "#90be6dff",
  256: "#4d908eff",
  512: "#f8961eff",
  1024: "#f3722cff",
  2048: "#f94144ff",
};
keyCodes = {
  37: "a",
  38: "w",
  39: "d",
  40: "s",
  87: "w",
  83: "s",
  65: "a",
  68: "d",
};
// on ready function

var populateBoard = function () {
  data = $.get("/board", function (data, status) {
    updateBoard(data);
  });
};

// SLEEP FUNCTION
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

$(document).ready(function () {
  populateBoard();
  // play();
});
// add event listener to the tiles
// add listeners to arrow keys
$(document).keydown(function (e) {
  // if key in arrow keys is pressed
  if (
    (e.keyCode >= 37 && e.keyCode <= 40) ||
    e.keyCode == 87 ||
    e.keyCode == 83 ||
    e.keyCode == 65 ||
    e.keyCode == 68
  ) {
    // prevent default action
    e.preventDefault();
    let direction = keyCodes[e.keyCode];
    move(direction);
  }
});

var move = function (direction) {
  $.post(`/move/${direction}`, function (data) {
    //on success
    updateBoard(data);
    // on failure
  }).fail(function () {
    alert("Game over  ");
    populateBoard();
  });
};

var updateBoard = function (data) {
  let tiles = $(".tile");
  // colort the tiles
  let tileValues = data["board"];
  let score = data["score"];
  $("#score").html(score);
  for (let i = 0; i < tiles.length; i++) {
    let num = tileValues[i];
    if (num != 0) tiles[i].innerHTML = num;
    else tiles[i].innerHTML = "";
    tiles[i].style.backgroundColor = colors[num];
  }
};

async function play() {
  await sleep(10);
  $.get("/ai_move", function (data, status) {
    updateBoard(data);
    if (aiPlaying) play(); // Recursive call to continue the loop
  });
}

// on reset button click
$("#resetGame").click(function () {
  $.post("/reset", function (data) {
    updateBoard(data);
  });
});

// on let ai play button click
$("#ai").click(function () {
  //  change label
  if ($("#ai").html() == "Let AI Play") {
    $("#ai").html("Stop AI");
    aiPlaying = true;
    play();
  } else {
    aiPlaying = false;
    $("#ai").html("Let AI Play");
  }
});

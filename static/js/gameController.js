

game_uuid = window.location.href.split('/').at(-1);

var ws = new WebSocket(url = `ws://localhost:8000/ws/${game_uuid}`);

ws.onmessage = function (event) 
{
    var data = JSON.parse(event.data);
    displayBoard(data);
}

ws.onopen = function (event) 
{
    console.log("Connection open")
}

ws.onclose= function (event) 
{
    console.log("Connection close")
}

function displayBoard(data) {
    var board = document.getElementById('board');
    var context = board.getContext("2d");
    var w_figure = document.getElementById('white_figure')
    var b_figure = document.getElementById('black_figure')
    var background = document.getElementById('board_background')
    context.drawImage(background, 0, 0, 500, 500);
    for (var i = 0; i < 8; i++) {
        for (var j = 0; j < 8; j++) {
            var figure;
            if (data[i][j] == 0)
                figure = w_figure
            else if (data[i][j] == 1)
                figure = b_figure
            else continue

            var offset = 24
            var size = (500-2*offset)/8
            var x = offset + size*j
            var y = 500 - size*i - 3.3*offset
            context.drawImage(figure, x, y, size, size);
        }
    }
}


function calltest(command) {
    ws.send(command);
}




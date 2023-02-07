

var game_uuid = window.location.href.split('/').at(-1);

var ws = new WebSocket(url = `ws://localhost:8000/ws/${game_uuid}`);


const ServerMessageType = {
    FigureType: 0,
    Board: 1,
    MoveResponse: 2,
    InvalidRequest: 3,
    NotYourMove: 4,
    InvalidMove: 5,
}; 

const ClientMessageType = {
    GetMyFigureType: 0,
    GetBoard: 1,
    MakeMove: 2, 
}


ws.onmessage = function (event) 
{
    var data = JSON.parse(event.data);

    switch(data.type)
    {
        case ServerMessageType.FigureType:
            figureText = document.getElementById('figureType');
            figureText.innerText = "Your figures: " + String(data.message);
            break;
    
        case ServerMessageType.Board:
            displayBoard(data.message);
            break;

        case ServerMessageType.InvalidRequest:
            displayMessage("Invalid request! ");
            break;

        case ServerMessageType.NotYourMove:
            displayMessage("Not your move! ");
            break;

        case ServerMessageType.InvalidMove:
            displayMessage("Invalid move! ");
            break;
       
        default:
            displayMessage("Invalid server response!");
    }
}

ws.onopen = function (event) 
{
    console.log("Connection open")
}

ws.onclose= function (event) 
{
    console.log("Connection close")
}

function displayMessage(message){
    figureText = document.getElementById('message')
    figureText.innerText = "Message: " + message
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

setTimeout(() => {
    ws.send(JSON.stringify({'type': 0}));
    ws.send(JSON.stringify({'type': 1}));
}, 1000)







var game_uuid = window.location.href.split('/').at(-1);

let host = window.location.host;
var ws = new WebSocket(url = `ws:${host}/ws/${game_uuid}`);

var board = document.getElementById('board');
var context = board.getContext("2d");

var board_map = NaN;
var figure = NaN;
var targetCell = NaN;
var userFigureImage = NaN

const ServerMessageType = {
    FigureType: 0,
    Board: 1,
    MoveResponse: 2,
    InvalidRequest: 3,
    NotYourMove: 4,
    InvalidMove: 5,
    Winner: 6,
}; 

const ClientMessageType = {
    GetMyFigureType: 0,
    GetBoard: 1,
    MakeMove: 2,
    Surrender: 3,
}


document.getElementById('surrenderButton').addEventListener('click', surrender);


ws.onmessage = function (event) 
{
    var data = JSON.parse(event.data);

    switch(data.type)
    {
        case ServerMessageType.FigureType:
            figureText = document.getElementById('figureType');
            f = data.message == 0 ? "White" : "Black";
            figureText.innerText = "Your figures: " + f;
            figure = data.message;
            break;
    
        case ServerMessageType.Board:
            rev = figure == 0 ? false : true
            displayBoard(data.message, rev);
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

        case ServerMessageType.Winner:
            f = data.message == 0 ? "White" : "Black";
            displayMessage("Winner: " + f);
            confirm("Winner: " + f);
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
    ul = document.getElementById('message')
    li = document.createElement('li')
    li.innerText = "Message: " + message
    ul.appendChild(li)
}

function displayBoard(data, rev=false) {
    var w_figure = document.getElementById('white_figure')
    var b_figure = document.getElementById('black_figure')
    var background = document.getElementById('board_background')
    board_map = data;
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
            if(rev)
            {
                var jr = 7 - j;
                var ir = 7 - i;
            }
            else
            {
                var jr = j;
                var ir = i;
            }
            var x = offset + size*jr
            var y = 500 - size*ir - 3.3*offset
            context.drawImage(figure, x, y, size, size);
        }
    }
}

function drawChoseFigure(posx, posy, fig=false)
{

    if (figure == 0){
        var figureChoseImage = document.getElementById('white_figure_ch')
    }
    else{
        var figureChoseImage = document.getElementById('black_figure_ch')
    }
    if (fig){
        if (figure == 0){
            figureChoseImage = document.getElementById('white_figure')
        }
        else{
            figureChoseImage = document.getElementById('black_figure')
        }
    }


    var offset = 24
    var size = (500-2*offset)/8
    var x = offset + size*posy
    var y = 500 - size*posx - 3.3*offset
    targetCell = figureChoseImage;
    context.drawImage(figureChoseImage, x, y, size, size);
}


board.addEventListener('mousedown', function(event) {
    var rawX = event.pageX - event.target.offsetLeft;
    var rawY = event.pageY - event.target.offsetTop;

    var offset = 24
    var size = (500-2*offset)/8
    if(figure == 0)
    {
        var x = Math.ceil((rawX - offset) / size) - 1
        var y = 7 - (Math.ceil((rawY - offset) / size) - 1) 
    }
    else
    {
        var x = 7 - Math.ceil((rawX - offset) / size) + 1
        var y = (Math.ceil((rawY - offset) / size) - 1)  
    }

    if (board_map[y][x] == figure){
        if(figure == 0){
            drawChoseFigure(targetCell[0], targetCell[1], true);
            drawChoseFigure(y, x);
        }
        else{
            drawChoseFigure(7 - targetCell[0], 7 - targetCell[1], true);
            drawChoseFigure(7 - y, 7 -x);
        }
        targetCell = [y, x]
    }
    else if (board_map[y][x] == null){
        move = boardPositionConvert([targetCell[1], targetCell[0]], [x, y])
        if(figure == 0){
            drawChoseFigure(targetCell[0], targetCell[1], true);
        }
        else{
            drawChoseFigure(7-targetCell[0], 7-targetCell[1], true);
        }
        ws.send(JSON.stringify({
            'type': ClientMessageType.MakeMove,
            'message': move,
        }));
    }


  });

function boardPositionConvert(f, t)
{
    const letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
    var from = `${letters[f[0]]}${f[1]+1}`;
    var to = `${letters[t[0]]}${t[1]+1}`;
    
    return from + ' ' + to
}


function surrender()
{
    ws.send(JSON.stringify({
        'type': ClientMessageType.Surrender,
    }));
}


function calltest(command) {
    ws.send(JSON.stringify({
        'type': ClientMessageType.MakeMove,
        'message': command,
    }));
}

setTimeout(() => {
    ws.send(JSON.stringify({'type': ClientMessageType.GetMyFigureType}));
    ws.send(JSON.stringify({'type': ClientMessageType.GetBoard}));
}, 1000)








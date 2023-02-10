
 
const request = new XMLHttpRequest();
let host = window.location.host;
const url = `http://${host}/game/list?page=0`


function UpdateGameList(){
    request.open('GET', url);

    request.setRequestHeader('Content-Type', 'application/x-www-form-url');
    
    request.addEventListener("readystatechange", () => {
        if (request.readyState === 4 && request.status === 200) {

            try {
                var data = JSON.parse(request.responseText);
            } catch(err) {
                console.log(err.message + " in " + request.responseText);
                return;
            }

            var gameUI = document.getElementById("gameUI")
            while (gameUI.firstChild) {
                gameUI.removeChild(gameUI.firstChild);
            }
            for(var i=0; i<data.length; i++){
                var child = document.createElement('li')
                child.className = 'list-group-item'
                child.innerHTML = `
                    <form action="http://${host}/game/field/${data[i][1]}" method="get">
                        <button type="submit" class="btn btn-info">Join</button>
                    </form>
                `
                child.prepend(document.createTextNode(data[i][0]));
                gameUI.appendChild(child);
            }
        }
    });
     
    request.send();
}

UpdateGameList();


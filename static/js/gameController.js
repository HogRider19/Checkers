

var ws = new WebSocket(url='ws://localhost:8000/ws/ihsaghsvka')

ws.onmessage = function(event){
    console.log(event.data)
}

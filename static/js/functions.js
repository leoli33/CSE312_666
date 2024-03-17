const socket = io();

document.getElementById("send-button").addEventListener("click", function(){
    let message = document.getElementById("chat-input").value.trim();
    if (message !== "") {
        socket.emit("chat_message", message);
        document.getElementById("chat-input").value = ""; 
    }
});
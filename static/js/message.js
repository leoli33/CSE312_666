const socket = io('wss://cupid-666.me/message', {transports: ['websocket']});
const chatMessages = document.getElementById("chat-messages");
const clearButton = document.getElementById("clear-button");
const chatForm = document.getElementById('chat-form');

chatForm.addEventListener('submit',function(event) {
    event.preventDefault();
    let message = document.getElementById("chat-input").value.trim();
    if (message !== "") {
        socket.emit("chat_message", {sender: username, message: message});
        document.getElementById("chat-input").value = ""; 
    }
});

socket.on("load_chat", function(data) {
    const sender = data.username;
    const message = data.message;
    const profilePic = data.profile_pic;
    
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message-container');
    const messageElement = document.createElement('default');
    messageElement.textContent = sender + ": " + message;

    // Create and append the image element
    const imgElement = document.createElement('img');
    imgElement.src = profilePic;
    imgElement.classList.add('profile-pic');
    messageDiv.appendChild(imgElement);

    messageDiv.appendChild(messageElement);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
});

clearButton.addEventListener('click', function() {
    while (chatMessages.firstChild) {
        chatMessages.removeChild(chatMessages.firstChild);
    }
});

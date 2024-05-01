//const socket = io({transports:['websocket']});
const socket = io('wss://cupid-666.me', { path: '/socket.io', transports: ['websocket'] });
const chatMessages = document.getElementById("chat-messages");
// const clearButton = document.getElementById("clear-button");
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
    const usernameElement = document.createElement('div');
    usernameElement.classList.add('username');
    usernameElement.textContent = sender
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.textContent = message;

    // Create and append the image element
    const imgElement = document.createElement('img');
    imgElement.src = profilePic;
    imgElement.classList.add('profile-pic');
    usernameElement.appendChild(imgElement);
    messageDiv.appendChild(usernameElement);
    messageDiv.appendChild(messageElement);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
});

// clearButton.addEventListener('click', function() {
//     while (chatMessages.firstChild) {
//         chatMessages.removeChild(chatMessages.firstChild);
//     }
// });

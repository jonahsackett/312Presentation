window.onload=function(){
    document.getElementById("background_buttonred").addEventListener('click', function() {document.body.style.backgroundColor = "red";});
    document.getElementById("background_buttonblue").addEventListener('click', function(){document.body.style.backgroundColor = "#87d6d4";});
}


function addMessageToChat(messageJSON, auth) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("chat-message");
    messageElement.id = messageJSON.id;
    var messageHTML = '';
    if (auth == "True"){
        messageHTML = `
        <p>${messageJSON.username}: ${messageJSON.message}</p> <a href="/like/${messageJSON.id}">Like</a><span id = "like${messageJSON.id}">-Likes: ${messageJSON.likes}</span>
    `;
    }else{
        messageHTML = `
        <p>${messageJSON.username}: ${messageJSON.message}</p> 
    `;
    }
    messageElement.innerHTML = messageHTML;
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateLike(messageJSON, auth){
    if(auth == "True"){
        console.log("works")
        console.log("like"+messageJSON.id)
        console.log(document.getElementById("like"+messageJSON.id).innerHTML)
        document.getElementById("like"+messageJSON.id).innerHTML = "-Likes: " + messageJSON.likes;
    }
}

function sendChat(){
    console.log("sent")
    const message = document.getElementById('textbox').value;
    socket.emit("chatMessage", { "message": message })
    document.getElementById('textbox').value = '';
}

function toggleForms() {
    const forms = document.getElementById("forms");
    const logout = document.getElementById("logged-in");
    forms.style.display = (forms.style.display === "none") ? "block" : "none";
    logout.style.display = (logout.style.display === "none") ? "block" : "none";
}

function chatRoomDirect() {
    window.location.href = "/chatroom";
}

function chatRoomLeave() {
    window.location.href = "/";
}
window.onload=function(){
    document.getElementById("background_buttonred").addEventListener('click', function() {document.body.style.backgroundColor = "red";});
    document.getElementById("background_buttonblue").addEventListener('click', function(){document.body.style.backgroundColor = "#87d6d4";});
}

function toggleForms() {
    var forms = document.getElementById("forms");
    var logout = document.getElementById("logged-in");
    if (forms.style.display === "none"){
        forms.style.display = "block";
        logout.style.display = "none";
    }
    else{
        forms.style.display = "none";
        logout.style.display = "block";
    }
}

function sendChat(){
    const chatTextBox = document.getElementById("textbox");
    const message = chatTextBox.value;
    chatTextBox.value = "";
    const messageJSON = {"message": message};
    const request = new XMLHttpRequest();
    request.open("POST", "/chatroom-message");
    request.send(JSON.stringify(messageJSON));
}

function chatRoomDirect(){
    // const request = new XMLHttpRequest();
    // request.open("GET", "/chatroom");
    // request.send();
    window.location.href = "/chatroom";
}

function chatRoomLeave(){
    window.location.href = "/";
}
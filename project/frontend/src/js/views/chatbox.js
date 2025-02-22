const chatBox = document.getElementById('chat-box');
const chatInput = document.getElementById('chat-input');
const sendButton = document.getElementById('send-button');

function loadChatHistory(){
    const history = JSON.parse(localStorage.getItem('chatHistory')) || [];
    history.forEach(message => addMessage(message));
}

function addMessage(message){
    const messageElement = document.createElement('div');
    messageElement.className = 'chat-message';
    messageElement.innerText = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}
function storeMessage(message){
    const history = JSON.parse(localStorage.getItem('chatHistory')) || [];
    history.push(message);
    localStorage.setItem('chatHistory', JSON.stringify(history));
}

export function load() {    
    sendButton.addEventListener('click', () => {
        const msg = chatInput.value.trim();
        if(msg){
            addMessage(msg);
            storeMessage(msg);
            chatInput.value = '';
        }
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter'){
            sendButton.click();
        }
    });
    loadChatHistory();
}


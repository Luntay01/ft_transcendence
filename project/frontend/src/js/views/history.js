const historyContainer = document.getElementById('history-container');

function displayChatHistory(){
    const history = JSON.parse(localStorage.getItem('chatHistory')) || [];
    history.forEach(message =>{
        const messageElement = document.createElement('div');
        messageElement.className = 'history-message';
        messageElement.innerText = message;
        historyContainer.appendChild(messageElement);
    });
}

export function load() {    
    displayChatHistory();
}


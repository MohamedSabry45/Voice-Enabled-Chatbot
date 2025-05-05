class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector(".chatbox__button"),
            chatBox: document.querySelector(".chatbox__support"),
            sendButton: document.querySelector(".send__button"),
            textButton: document.querySelector(".send__button .text-btn"),
            microphoneButton: document.querySelector(".send__button .microphone-btn"),
            inputField: document.querySelector(".chatbox__footer input"),
            recordText: document.querySelector(".send__button span"),
        };
 
        this.state = false; 
        this.messages = [];
        this.isVoiceMode = false;
        this.isRecording = false;
        this.agentResponseMode = 'voice';
        this.isSending = false;
        this.isSpeaking = false; // إضافة متغير لتتبع حالة التحدث

        this.initSpeechRecognition();
        this.setupEventListeners();
    }

    initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            this.recognition = new SpeechRecognition();
            this.recognition.lang = 'en-US'; //this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.setupRecognitionCallbacks();
        }
    }
    setupRecognitionCallbacks() {
        this.recognition.onstart = () => {
            this.isRecording = true;
            this.args.microphoneButton.classList.add('active');
            this.args.recordText.textContent = 'Recording...';
        };

        this.recognition.onend = () => {
            this.isRecording = false;
            if (this.isVoiceMode) this.recognition.start();
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[event.resultIndex][0].transcript;
            this.args.inputField.value = transcript;
        };

        this.recognition.onerror = (event) => {
            console.error('Recognition error:', event.error);
            this.switchToTextMode();
        };
    }

    setupEventListeners() {
        this.args.microphoneButton?.addEventListener("click", () => this.toggleVoiceRecognition());
        this.args.textButton?.addEventListener("click", () => this.switchToTextMode());
        this.args.inputField?.addEventListener("keyup", (e) => e.key === "Enter" && this.onSendButton());
        this.args.openButton?.addEventListener("click", () => this.toggleState());
        this.args.sendButton?.addEventListener("click", () => this.onSendButton());
    }
    
    setResponseMode(mode) {
        this.agentResponseMode = mode;
    }

    getResponseMode() {
        return this.agentResponseMode;
    }

    display() {
        // Initial display setup
    }

    toggleState() {
        this.state = !this.state;
        this.args.chatBox.classList.toggle("chatbox--active", this.state);
    }

    async onSendButton() {
        if (this.isSending || this.isSpeaking) return;
        this.isSending = true;
    
        const message = this.args.inputField.value.trim();
        if (!message) {
            this.isSending = false;
            return;
        }
    
        this.args.inputField.value = "";
        this.addMessage('User', message, true);
    
        try {
            const response = await this.sendMessageToServer(message);
            if (response?.answer === "__CLEAR__") {
                // مسح المحادثة من الواجهة
                const chatMessages = this.args.chatBox.querySelector(".chatbox__messages");
                chatMessages.innerHTML = '<div></div>';
                this.messages = [];
            } else if (response?.answer) {
                this.addMessage('Sam', response.answer, false);
                if (this.agentResponseMode === 'voice') {
                    await this.speakText(response.answer);
                }
            }
        } catch (error) {
            console.error("Error:", error);
        } finally {
            this.isSending = false;
        }
    }
    addMessage(sender, message, isUser) {
        const chatmessage = this.args.chatBox.querySelector(".chatbox__messages");
        const messageDiv = document.createElement('div');
        
        messageDiv.classList.add('messages__item');
        messageDiv.classList.add(isUser ? 'messages__item--user' : 'messages__item--bot');
        messageDiv.textContent = message;
        
        chatmessage.appendChild(messageDiv);
        chatmessage.scrollTop = chatmessage.scrollHeight;
        
        this.messages.push({ name: sender, message: message, isUser: isUser });
    }

    async sendMessageToServer(message) {
        const response = await fetch("/predict", {
            method: "POST",
            body: JSON.stringify({ 
                message: message,
                agentResponseMode: this.agentResponseMode
            }),
            headers: {
                "Content-Type": "application/json"
            }
        });
        if (!response.ok) throw new Error('Network error');
        return await response.json();
    }

    toggleVoiceRecognition() {
        if (this.isVoiceMode) {
            this.switchToTextMode();
        } else {
            this.startVoiceRecognition();
        }
    }

    startVoiceRecognition() {
        if (this.recognition && !this.isRecording) {
            this.recognition.start();
            this.isVoiceMode = true;
        }
    }

    switchToTextMode() {
        this.recognition?.stop();
        this.isVoiceMode = false;
        this.isRecording = false;
        this.args.microphoneButton?.classList.remove('active');
        this.args.inputField.focus();
        this.args.recordText.textContent = 'Record Now';
    }

    speakText(text) {
        return new Promise((resolve) => {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel(); // إلغاء أي كلام جاري
                this.isSpeaking = true;
                
                const utterance = new SpeechSynthesisUtterance(text);
                // utterance.lang = 'ar-SA';
                // utterance.rate = 0.9;
                utterance.lang = 'en-US'; 
                utterance.rate = 0.7; 
                
                utterance.onend = () => {
                    this.isSpeaking = false;
                    resolve();
                };
                
                utterance.onerror = () => {
                    this.isSpeaking = false;
                    resolve();
                };
                
                window.speechSynthesis.speak(utterance);
            } else {
                resolve();
            }
        });
    }
}

// CSS المطلوب
const style = document.createElement('style');
style.textContent = `
.chatbox__messages {
    display: flex;
    flex-direction: column;
    padding: 10px;
    overflow-y: auto;
    max-height: 300px;
    gap: 10px;
}

.messages__item--user {
    align-self: flex-end;
    background: #4e8cff;
    color: white;
    border-radius: 18px 18px 0 18px;
    padding: 10px 15px;
    max-width: 70%;
}

.messages__item--bot {
    align-self: flex-start;
    background: #f1f1f1;
    color: #000;
    border-radius: 18px 18px 18px 0;
    padding: 10px 15px;
    max-width: 70%;
}
`;
document.head.appendChild(style);

// Initialize chatbox
const chatbox = new Chatbox();
chatbox.display();
window.chatbox = chatbox;
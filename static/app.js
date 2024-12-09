class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector(".chatbox__button"),
            chatBox: document.querySelector(".chatbox__support"),
            sendButton: document.querySelector(".send__button"),
            microphoneButton: document.querySelector(".send__button i.fa-microphone"), // إضافة الميكروفون
        };

        this.state = false;
        this.messages = [];

        // التحقق من دعم SpeechRecognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.lang = 'en-US'; // تحديد اللغة (اختياري)
        this.recognition.continuous = true; // استمرار التسجيل

        // إضافة EventListener للميكروفون
        this.args.microphoneButton.addEventListener("click", () => this.toggleVoiceRecognition());
    }

    display() {
        const { openButton, chatBox, sendButton } = this.args;

        openButton.addEventListener("click", () => this.toggleState(chatBox));
        sendButton.addEventListener("click", () => this.onSendButton(chatBox));

        const node = chatBox.querySelector("input");
        node.addEventListener("keyup", ({ key }) => {
            if (key === "Enter") {
                this.onSendButton(chatBox);
            }
        });
    }

    toggleState(chatbox) {
        this.state = !this.state;

        // show or hides the box
        if (this.state) {
            chatbox.classList.add("chatbox--active");
        } else {
            chatbox.classList.remove("chatbox--active");
        }
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector("input");
        let text1 = textField.value;
        if (text1 === "") {
            return;
        }

        let msg1 = { name: "User", message: text1 };
        this.messages.push(msg1);

        fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            body: JSON.stringify({ message: text1 }),
            mode: "cors",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((r) => r.json())
            .then((r) => {
                let msg2 = { name: "Sam", message: r.answer };
                this.messages.push(msg2);
                this.updateChatText(chatbox);
                textField.value = "";
            })
            .catch((error) => {
                console.error("Error:", error);
                this.updateChatText(chatbox);
                textField.value = "";
            });
    }

    updateChatText(chatbox) {
        var html = "";
        this.messages
            .slice()
            .reverse()
            .forEach(function (item, index) {
                if (item.name === "Sam") {
                    html += '<div class="messages__item messages__item--visitor">' + item.message + "</div>";
                } else {
                    html += '<div class="messages__item messages__item--operator">' + item.message + "</div>";
                }
            });

        const chatmessage = chatbox.querySelector(".chatbox__messages");
        chatmessage.innerHTML = html;
    }

    // تفعيل / إيقاف التعرف على الصوت عند الضغط على أيقونة الميكروفون
    toggleVoiceRecognition() {
        if (this.recognition) {
            if (this.recognition.started) {
                this.recognition.stop(); // إيقاف التسجيل
                this.args.microphoneButton.classList.remove('active');
                this.recognition.started = false;
            } else {
                this.recognition.start(); // بدء التسجيل
                this.args.microphoneButton.classList.add('active');
                this.recognition.started = true;
            }
        }
    }

    // التعامل مع النصوص الناتجة من التعرف على الصوت
    handleVoiceInput(event) {
        const transcript = event.results[event.resultIndex][0].transcript;
        const chatbox = this.args.chatBox;
        const textField = chatbox.querySelector("input");
        textField.value = transcript; // عرض النص في حقل الإدخال
    }

    // إضافة الحدث الخاص بالتعرف على الصوت
    initVoiceRecognition() {
        this.recognition.onstart = () => console.log('Voice recognition started.');
        this.recognition.onend = () => console.log('Voice recognition ended.');
        this.recognition.onresult = (event) => this.handleVoiceInput(event);
    }
}

// إنشاء الكائن وتشغيل الدالة initVoiceRecognition
const chatbox = new Chatbox();
chatbox.initVoiceRecognition();
chatbox.display();

class Chatbox {
    constructor() {
        this.args = {
            
            openButton: document.querySelector(".chatbox__button"),
            chatBox: document.querySelector(".chatbox__support"),
            sendButton: document.querySelector(".send__button"),
            textButton: document.querySelector(".send__button .text-btn"), // أيقونة الكتابة
            microphoneButton: document.querySelector(".send__button .microphone-btn"), // أيقونة الميكروفون
            inputField: document.querySelector(".chatbox__footer input"), // حقل النص
            recordText: document.querySelector(".send__button span"), // النص الذي يعرض عند التسجيل
        };
        

        this.state = false;
        this.messages = [];
        this.isVoiceMode = false; // تحديد وضع الصوت
        this.isRecording = false; // إضافة متغير لتحديد ما إذا كان الميكروفون يعمل أو لا
        

        // التحقق من دعم SpeechRecognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Voice recognition is not supported in your browser.");
            return; // الخروج إذا لم يكن التعرف على الصوت مدعومًا
        }
        

        this.recognition = new SpeechRecognition();
        this.recognition.lang = 'en-US'; // تحديد اللغة (اختياري)
        this.recognition.continuous = true; // استمرار التسجيل
        this.recognition.interimResults = true; // الحصول على النتائج مؤقتة أثناء التسجيل

        // إضافة EventListener للميكروفون
        this.args.microphoneButton.addEventListener("click", () => this.toggleVoiceRecognition());
        // إضافة EventListener لزر الكتابة
        this.args.textButton.addEventListener("click", () => {
            this.switchToTextMode();
        
            // Show the plane icon
            const planeIcon = document.querySelector('.sendIcon');
            planeIcon.classList.remove('d-none');
        
            // Hide the settings button
            const settingsBtn = document.querySelector('.settings-btn');
            settingsBtn.classList.add('d-none');
        });
        

        // إضافة EventListener للضغط على Enter
        this.args.inputField.addEventListener("keyup", (event) => {
            if (event.key === "Enter") {
                this.onSendButton(this.args.chatBox);
            }
        });
    }

    display() {
        const { openButton, chatBox, sendButton } = this.args;

        openButton.addEventListener("click", () => this.toggleState(chatBox));
        sendButton.addEventListener("click", () => this.onSendButton(chatBox));

        const node = chatBox.querySelector("input");
        node.addEventListener("keyup", ({ key }) => {
            if (key === "Enter") {
                this.onSendButton(chatbox);
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
 
        // إذا كان التسجيل الصوتي مفعلاً، توقفه
        if (this.isVoiceMode) {
            this.recognition.stop();
            this.isVoiceMode = false;
            this.args.microphoneButton.classList.remove('active');
            this.args.recordText.textContent = 'Record Now'; // إعادة النص إلى "Record Now"
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
                // Stop any ongoing voice output
                window.speechSynthesis.cancel();
        
                let msg2 = { name: "Sam", message: r.answer };
                this.messages.push(msg2);
                this.updateChatText(chatbox);
                textField.value = "";
        
                // Show the microphone button again
                this.args.microphoneButton.style.display = 'inline-block';
                this.args.recordText.textContent = 'Record Now'; // Reset record text
        
                // Optional: Speak the response (if needed)
                speakText(r.answer);
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

    toggleVoiceRecognition() {
        if (this.isVoiceMode) {
            this.switchToTextMode(); // العودة لوضع النص
        } else {
            if (this.recognition && !this.isRecording) { // التأكد من عدم التسجيل إذا كان الميكروفون في حالة تسجيل
                try {
                    this.recognition.start(); // بدء التسجيل
                    this.isRecording = true; // تعيين حالة التسجيل
                    this.args.microphoneButton.classList.add('active');
                    this.args.recordText.textContent = 'Recording...'; // عرض نص "Recording..." أثناء التسجيل
                    this.isVoiceMode = true; // تفعيل وضع الصوت
                } catch (error) {
                    console.error('Error starting recognition:', error);
                    // لا تعرض رسالة الخطأ الآن
                    alert('There was an issue starting voice recognition.');
                }
            }
        }
    }

    // التبديل لوضع الكتابة
    switchToTextMode() {
        this.isVoiceMode = false;
        this.args.microphoneButton.classList.remove('active');
        this.args.inputField.focus(); // إعادة التركيز على حقل الكتابة
        this.args.recordText.textContent = 'Record Now'; // إعادة النص إلى "Record Now"
        this.isRecording = false; // إيقاف حالة التسجيل
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
        this.recognition.onstart = () => {
            console.log('Voice recognition started.');
            this.isRecording = true; // تعيين حالة التسجيل
        };
        this.recognition.onend = () => {
            console.log('Voice recognition ended.');
            this.isRecording = false; // إيقاف حالة التسجيل
            if (this.isVoiceMode) {
                this.recognition.start(); // إعادة البدء تلقائيًا في حال عدم توقف الصوت
            }
        };
        this.recognition.onresult = (event) => this.handleVoiceInput(event);
    }
}

// إنشاء الكائن وتشغيل الدالة initVoiceRecognition
const chatbox = new Chatbox();
chatbox.initVoiceRecognition();
chatbox.display();
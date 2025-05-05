import random
import json
import torch
import nltk
import os
import sys
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

# تهيئة مسار بيانات NLTK
nltk.data.path.append(r'D:\PRO\source_code\chatbot-deployment\venv\Lib\site-packages\nltk')

# تحديد الجهاز (GPU إذا متاح)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# مسارات الملفات
intents_file = 'intents_old.json'
data_file = 'data.pth'

# التحقق من وجود الملفات المطلوبة
if not os.path.exists(intents_file):
    print(f"خطأ: لم يتم العثور على ملف {intents_file}")
    sys.exit(1)

if not os.path.exists(data_file):
    print(f"خطأ: لم يتم العثور على ملف {data_file}")
    sys.exit(1)

# تحميل بيانات النوايا
with open(intents_file, 'r', encoding='utf-8') as json_data:
    intents = json.load(json_data)

# تحميل نموذج المدرب
data = torch.load(data_file, weights_only=True)

# معلمات النموذج
input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

# تهيئة النموذج
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

# إعدادات البوت
# ... (الجزء العلوي من الكود يبقى كما هو بدون تغيير حتى bot_name)

bot_name = "Sam"
chat_history = []

def clear_chat():
    """مسح سجل المحادثة تمامًا دون أي رد"""
    global chat_history
    chat_history.clear()
    try:
        open('chat_log.txt', 'w').close()
    except:
        pass
    return "__CLEAR__"  # إشارة خاصة للمسح

def get_response(msg):
    user_input = msg.lower().strip()
    
    # أوامر المسح
    clear_commands = ["clear chat", "مسح المحادثة", "احذف الشات", "clear", "مسح", "امسح", "delete chat"]
    if user_input in clear_commands:
        return clear_chat()
    
    # ... (باقي الدالة الأصلي يبقى كما هو)
    
    # المعالجة العادية للرسائل
    import string
    translator = str.maketrans('', '', string.punctuation)
    cleaned_input = user_input.translate(translator)
    
    best_match = None
    highest_score = 0
    
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            cleaned_pattern = pattern.lower().translate(translator)
            score = sum(1 for word in cleaned_input.split() 
                       if word in cleaned_pattern.split())
            
            if score > highest_score:
                highest_score = score
                best_match = intent
    
    if best_match and highest_score >= 1:
        return random.choice(best_match['responses'])
    
    return "I'm not sure what you mean. Can you rephrase?"

def log_conversation(user_input, bot_response):
    """تسجيل المحادثة مع تجاهل أوامر المسح"""
    if bot_response is not False:  # تجاهل أوامر المسح
        with open("chat_log.txt", "a", encoding='utf-8') as log_file:
            log_file.write(f"You: {user_input}\n{bot_name}: {bot_response}\n\n")

if __name__ == "__main__":
    print("مرحبًا! أنا بوت الدردشة (اكتب 'quit' للخروج)")
    while True:
        try:
            sentence = input("You: ")
            if sentence.lower() == "quit":
                break

            resp = get_response(sentence)
            
            if resp is False:  # حالة أمر المسح
                continue  # لا تعرض أي شيء
                
            if resp:  # الردود العادية
                chat_history.append((sentence, resp))
                print(f"{bot_name}: {resp}")
                log_conversation(sentence, resp)
                
        except KeyboardInterrupt:
            print("\nتم إيقاف البوت.")
            break
        except Exception as e:
            print(f"حدث خطأ: {str(e)}")
            continue
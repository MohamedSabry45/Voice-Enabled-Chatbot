import random
import json
import torch
import nltk

# تأكد من إضافة المسار المناسب إذا كان لديك مشاكل مع المسار
nltk.data.path.append(r'D:\PRO\source_code\chatbot-deployment\venv\Lib\site-packages\nltk')  # استخدم المسار الخاص بك

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# التعامل مع الخطأ لو الملف مفقود
try:
    with open('intents.json', 'r') as json_data:
        intents = json.load(json_data)
except FileNotFoundError:
    print("intents.json file not found.")
    exit()

FILE = "data.pth"
# التعامل مع الخطأ لو الملف مفقود
try:
    data = torch.load(FILE)
except FileNotFoundError:
    print("data.pth file not found.")
    exit()

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

# الشرح هنا
"""
1. يتم تحميل نموذج الشبكة العصبية باستخدام البيانات المحفوظة.
2. ثم يتم تغيير الوضع إلى التقييم باستخدام eval().
"""
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Sam"

def get_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    
    # إعادة تشكيل X ليكون مناسبًا للمدخلات
    X = X.reshape(1, X.shape[0])  # تحويل الأبعاد لتكون متوافقة مع المدخلات
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    # التأكد من احتمالية كبيرة للرد
    if prob.item() > 0.75:  # تغيير النسبة إلى 0.75 أو أعلى لضمان الردود الدقيقة
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])
    
    # الرد إذا كانت الاحتمالية أقل من 0.75
    return "I'm not sure what you mean. Can you rephrase?"  # الرد عند انخفاض الاحتمالية

if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence.lower() == "quit":
            break

        resp = get_response(sentence)
        print(f"{bot_name}: {resp}")

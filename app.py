from flask import Flask, render_template, request, jsonify, redirect, url_for
from chat import get_response  # تأكد من أن هذه الدالة موجودة في chat.py

app = Flask(__name__)

# تخزين بيانات المستخدمين في قاموس (يمكنك استخدام قاعدة بيانات في المستقبل)
users_db = {
    "mohamedsabry": "1111",  # اسم المستخدم وكلمة المرور
    "admin": "1234"
}

# صفحة تسجيل الدخول
@app.route("/login", methods=["GET", "POST"])
def login():
    error_message = None  # متغير لتخزين رسالة الخطأ

    if request.method == "POST":
        # استلام اسم المستخدم وكلمة المرور من النموذج
        username = request.form.get("username")
        password = request.form.get("password")
        
        # التحقق من صحة بيانات تسجيل الدخول
        if username in users_db and users_db[username] == password:
            return redirect(url_for("index_get"))  # إذا كانت صحيحة، الانتقال إلى صفحة البوت
        else:
            error_message = "Invalid username or password. Please try again."  # تخزين رسالة الخطأ

    return render_template("login.html", error_message=error_message)  # تمرير رسالة الخطأ إلى الـ HTML

# صفحة إنشاء حساب جديد
@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    error_message = None

    if request.method == "POST":
        # استلام بيانات المستخدم
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        
        # التحقق إذا كان المستخدم موجود بالفعل
        if first_name and last_name and email and password:  # تأكد من أن الحقول ليست فارغة
            username = email.split('@')[0]  # يمكن إنشاء اسم المستخدم من البريد الإلكتروني

            if username in users_db:
                error_message = "Username already exists. Please choose another one."
            else:
                # إضافة المستخدم الجديد
                users_db[username] = password
                return redirect(url_for("login"))  # بعد إنشاء الحساب، الانتقال إلى صفحة تسجيل الدخول
        else:
            error_message = "All fields are required. Please fill them all."

    return render_template("create_account.html", error_message=error_message)  # تمرير رسالة الخطأ إلى الـ HTML

# صفحة البوت
@app.route("/")
def index_get():
    return render_template("base.html")

# معالجة الرسائل الواردة إلى الشات بوت
@app.post("/predict")
def predict():
    # استلام الرسالة من الـ Frontend
    text = request.get_json().get("message")
    
    # التحقق من أنه تم إرسال الرسالة بشكل صحيح
    if not text:
        return jsonify({"error": "No message provided"}), 400  # الرد إذا كانت الرسالة فارغة أو مفقودة
    
    # الحصول على الرد من الشات بوت
    response = get_response(text)  # هنا سيتم معالجة الرسالة عبر الدالة get_response
    
    # إرسال الرد إلى الـ Frontend
    message = {"answer": response}  # الرد الذي سيرجع
    return jsonify(message)

if __name__ == "__main__":
    app.run(debug=True)

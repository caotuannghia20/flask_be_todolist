from flask import render_template,request, flash, redirect,url_for, session, jsonify
from .model import User , Note
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
from .import app, mail
import json

@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email = email).first()
        if user:
            if check_password_hash(user.password, password):
                session.permanent = True
                login_user(user, remember = True)
                flash("Đã đăng nhập thành công", category="success")
                return redirect(url_for("home"))
            else:
                flash("Sai mật khẩu", category="error")
        else:
            flash("Email không tồn tại", category="error")

    return render_template("login.html", user = current_user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/signup", methods = ["POST", "GET"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("User existed", category = "error")
        elif (len(email)<4):
            flash("Email cần nhiều hơn 3 ký tự", category = "error")
        elif len(password)<7:
            flash("Password cần nhiều hơn 7 ký tự",category = "error")
        elif password != confirm_password:
            flash("Không khớp yêu cầu nhập lại", category = "error")
        else:
            password = generate_password_hash(password, method = "sha256")
            new_user = User(email,user_name,password)
            db.session.add(new_user)
            db.session.commit()
            flash("Đã thêm vào cơ sử dữ liệu")
            login_user(new_user, remember = True)
            return redirect(url_for("home"))
    return render_template("signup.html", user = current_user)

@app.route("/changePassword",methods = ["POST", "GET"])
@login_required
def change_password():
    if request.method == "POST":
        password =  request.form.get("password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("new_password_confirm")
        if check_password_hash(current_user.password, password):
            if len(new_password)<7:
                flash("Password cần nhiều hơn 7 ký tự",category = "error")
            elif new_password != confirm_password:
                flash("Không khớp yêu cầu nhập lại", category = "error")
            else:
                new_password = generate_password_hash(new_password, method = "sha256")
                flash("Đã đổi mật khẩu thành công", category = "success")
                current_user.password = new_password
                db.session.commit()
        else:
               flash("Password hiện tại không đúng",category = "error")
    return render_template("edit.html", user = current_user)

@app.route("/changeInfo",methods = ["POST", "GET"])
@login_required
def change_info():
    if request.method == "POST":
        email = request.form.get("email")
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        if check_password_hash(current_user.password, password):
            if len(email) == 0 and len(user_name) !=0:
                flash("Cập nhật thông tin thành công", category = "success")
                current_user.user_name = user_name
                db.session.commit()
            elif len(user_name) == 0 and len(email) !=0:
                if (len(email)<4):
                    flash("Email cần nhiều hơn 3 ký tự", category = "error")
                else:
                    flash("Cập nhật thông tin thành công", category = "success")
                    current_user.email=email
                    db.session.commit()
            else:
                if (len(email)<4):
                    flash("Email cần nhiều hơn 3 ký tự", category = "error")
                else:
                    flash("Cập nhật thông tin thành công", category = "success")
                    current_user.user_name = user_name
                    current_user.email=email
                    db.session.commit()
                
        else:
            flash("Password hiện tại không đúng",category = "error")
    return render_template("edit_name_email.html", user = current_user)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            send_mail(user)
            flash('Check your email for the instructions to reset your password', category="success")
        else:
            flash('Tài khoản chưa được tạo', category="error")
            return render_template("signup.html", user = current_user)
    return render_template('reset_password_request.html',user = current_user,
                            title='Reset Password')
    
@app.route("/reset_password/<token>", methods = ["GET", "POST"])
def reset_token(token):
    user = User.verify_reset_password_token(token)
    if user is None:
        flash("That is invalid token or expried. Please try gain", category="error")
        return redirect(url_for("reset_password_request"))
    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("new_password_confirm")
        if len(new_password)<7:
                flash("Password cần nhiều hơn 7 ký tự",category = "error")
        elif new_password != confirm_password:
                flash("Không khớp yêu cầu nhập lại", category = "error")
        else:
            new_password = generate_password_hash(new_password, method = "sha256")
            flash("Đã đổi mật khẩu thành công", category = "success")
            user.password = new_password
            db.session.commit()
    return render_template("reset_password.html", user = current_user)

def send_mail(user):
    token= user.get_reset_password_token()
    msg = Message("Password Reset Resquet", recipients = [user.email], sender = "noreply@haha.com")
    msg.body = f"""
    To reset your password. Please follow the link below.
    {url_for("reset_token", token = token, _external = True)}
    If you didn't send a password reset request. Please ignore this message.
    This link is valid in 5 minutes.
    """
    mail.send(msg)
@app.route("/home", methods = ["POST", "GET"])
@app.route("/",  methods = ["POST", "GET"])
@login_required
def home():
    if request.method == "POST":
        note = request.form.get("note")
        if len(note) < 1:
            flash("Note quá ngắn" , category= "error")
        else:
            new_note = Note(data=note, user_id = current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash("Note đã được thêm", category="success")
    return render_template("home.html", user = current_user)
@app.route("/delete-note", methods = ["POST"])
def delete_note():
    note = json.loads(request.data)
    print(note)
    note_id = note["note_id"]
    result= Note.query.get(note_id)
    if result:
        if result.user_id == current_user.id:
            db.session.delete(result)
            db.session.commit()
    return jsonify({"code" : 200})

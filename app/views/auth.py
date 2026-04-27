from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models.user import User

# 修改變量名稱為 auth，以匹配 app/__init__.py 的導入
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # 修正 endpoint：將 public.index 改為 main.index
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'歡迎回來，{username}！', 'success')
            next_page = request.args.get('next')
            # 修正 endpoint
            return redirect(next_page or url_for('main.index'))
        else:
            flash('使用者名稱或密碼錯誤', 'danger')
    
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功登出', 'info')
    # 修正 endpoint
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('使用者名稱已被使用', 'danger')
            return redirect(url_for('auth.register'))
            
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('註冊成功！請登入', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')
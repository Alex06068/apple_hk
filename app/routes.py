import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, session

from flask_login import login_user, logout_user, current_user, login_required

from app.models.product import Product

from app.models.category import Category

from app.models.user import User

from app import db

from werkzeug.security import check_password_hash, generate_password_hash

from flask_mail import Message

from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime
from .models.order import Order, OrderItem


# 定義藍圖

main = Blueprint('main', __name__)

admin_bp = Blueprint('admin_custom', __name__, url_prefix='/admin_custom')

auth = Blueprint('auth', __name__)



# --- 前台路由 (main) ---



@main.route('/')

def index():

    categories = Category.query.all()

    products = Product.query.filter_by(is_featured=True).all()

    return render_template('index.html', categories=categories, products=products)



@main.route('/products')

def products():

    products = Product.query.all()

    return render_template('products.html', products=products)



@main.route('/category/<int:category_id>')

def category(category_id):

    cat = Category.query.get_or_404(category_id)

    products = Product.query.filter_by(category_id=category_id).all()

    return render_template('products.html', products=products, category=cat)



@main.route('/product/<int:product_id>')

def product(product_id):

    product = Product.query.get_or_404(product_id)

    return render_template('product.html', product=product)



@main.route('/add_to_cart/<int:product_id>', methods=['POST'])

def add_to_cart(product_id):

    cart = session.get('cart', {})

    str_id = str(product_id)

    cart[str_id] = cart.get(str_id, 0) + 1

    session['cart'] = cart

    session.modified = True

    flash('已成功加入購物車！', 'success')

    return redirect(url_for('main.product', product_id=product_id))



@main.route('/search')

def search():

    query = request.args.get('q', '')

    products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()

    return render_template('products.html', products=products, search_query=query)



@main.route('/cart')

def view_cart():

    cart = session.get('cart', {})

    products_in_cart = []

    total_price = 0

    for product_id, quantity in cart.items():

        product = Product.query.get(int(product_id))

        if product:

            product.quantity = quantity

            total_price += product.price * quantity

            products_in_cart.append(product)

    return render_template('cart.html', products=products_in_cart, total_price=total_price)



# 🆕 新增：結帳頁面路由

@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """處理結帳邏輯：將購物車轉化為真實訂單"""
    cart = session.get('cart', {})
    if not cart:
        flash('您的購物車是空的。', 'warning')
        return redirect(url_for('main.products'))

    # 計算結帳明細
    checkout_items = []
    total_price = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price * quantity
            total_price += subtotal
            checkout_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})

    if request.method == 'POST':
        # --- 🆕 新增：資料庫寫入邏輯 ---
        try:
            # 1. 建立 Order 主紀錄
            new_order = Order(
                user_id=current_user.id,
                order_number=str(uuid.uuid4().hex[:12].upper()), # 生成隨機編號
                total_amount=total_price,
                status='pending',
                created_at=datetime.utcnow()
            )
            db.session.add(new_order)
            db.session.flush() # 提前獲取 new_order.id 以供關聯

            # 2. 建立 OrderItem 詳細內容
            for item in checkout_items:
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=item['product'].id,
                    quantity=item['quantity'],
                    price=item['product'].price
                )
                db.session.add(order_item)

            # 3. 提交變更並清空購物車
            db.session.commit()
            session.pop('cart', None) 
            flash(f'訂單提交成功！訂單編號為：{new_order.order_number}', 'success')
            return redirect(url_for('main.orders'))

        except Exception as e:
            db.session.rollback()
            flash('系統錯誤，無法建立訂單。請聯繫客服。', 'danger')
            return redirect(url_for('main.view_cart'))

    return render_template('checkout.html', items=checkout_items, total=total_price)



@main.route('/clear_cart')

def clear_cart():

    session.pop('cart', None)

    flash('購物車已清空。', 'info')

    return redirect(url_for('main.view_cart'))



@main.route('/support')

def support():

    return render_template('support.html')



# 確保這裡的縮進正確，不要有多餘的空格或少縮進
@main.route('/profile')

@login_required

def profile():
    # 直接傳遞當前用戶對象到模板
    return render_template('profile.html', user=current_user)

@main.route('/orders')

@login_required

def orders():
    
    from .models.order import Order
    # 再次檢查：確保使用 created_at 而不是 timestamp，避免 AttributeError
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)



@main.route('/privacy')

def privacy():

    return "<h1>私隱政策建設中</h1>"



@main.route('/terms')

def terms():

    return "<h1>使用條款建設中</h1>"



# --- 身份驗證路由 (auth) --- (代碼維持不變)

@auth.route('/login', methods=['GET', 'POST'])

def login():

    if current_user.is_authenticated:

        return redirect(url_for('main.index'))

    if request.method == 'POST':

        email = request.form.get('email')

        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):

            login_user(user)

            flash('歡迎回來，Apple 專家！', 'success')

            return redirect(url_for('main.index'))

        flash('登入失敗，請檢查電郵或密碼。', 'danger')

    return render_template('login.html')



@auth.route('/register', methods=['GET', 'POST'])

def register():

    if current_user.is_authenticated:

        return redirect(url_for('main.index'))

    if request.method == 'POST':

        username = request.form.get('username')

        email = request.form.get('email')

        password = request.form.get('password')

        if User.query.filter_by(email=email).first():

            flash('此電郵地址已被註冊。', 'warning')

            return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email, password_hash=generate_password_hash(password))

        try:

            db.session.add(new_user)

            db.session.commit()

            flash('帳號建立成功！請立即登入。', 'success')

            return redirect(url_for('auth.login'))

        except:

            db.session.rollback()

            flash('註冊失敗。', 'danger')

    return render_template('register.html')



@auth.route('/logout')

@login_required

def logout():

    logout_user()

    flash('您已成功登出。', 'info')

    return redirect(url_for('main.index'))



# --- 後台管理路由 (admin) ---

@admin_bp.route('/') # 這樣訪問 http://IP:5001/admin_custom/ 就會進到這裡
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        abort(403)
    # 你可以從資料庫抓數據傳給 dashboard.html
    return render_template('admin/dashboard.html')

@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            send_reset_email(user)
            flash('重設密碼郵件已發送，請檢查信箱。', 'info')
            return redirect(url_for('auth.login'))
    return render_template('reset_request.html')

# 執行重設密碼頁面
@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        user_id = s.loads(token, max_age=1800)['user_id'] # Token 30分鐘有效
    except:
        flash('該連結無效或已過期。', 'warning')
        return redirect(url_for('auth.reset_request'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        user = User.query.get(user_id)
        # 這裡應使用 generate_password_hash
        user.password = new_password 
        db.session.commit()
        flash('您的密碼已更新！', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_token.html')

def send_reset_email(user):
    s = Serializer(current_app.config['SECRET_KEY'])
    token = s.dumps({'user_id': user.id})
    msg = Message('密碼重設請求', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''請點擊以下連結重設密碼：
{url_for('auth.reset_token', token=token, _external=True)}
如果您沒有發出此請求，請忽略。
'''
    mail.send(msg)

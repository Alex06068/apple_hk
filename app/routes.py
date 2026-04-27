from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, session

from flask_login import login_user, logout_user, current_user, login_required

from app.models.product import Product

from app.models.category import Category

from app.models.user import User

from app import db

from werkzeug.security import check_password_hash, generate_password_hash



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

    """處理結帳逻辑"""

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

        # 這裡通常會建立資料庫 Order 紀錄，目前先以模擬成功為主

        session.pop('cart', None) # 結帳完清空購物車

        flash('訂單提交成功！感謝您的選購。', 'success')

        return redirect(url_for('main.orders'))



    return render_template('checkout.html', items=checkout_items, total=total_price)



@main.route('/clear_cart')

def clear_cart():

    session.pop('cart', None)

    flash('購物車已清空。', 'info')

    return redirect(url_for('main.view_cart'))



@main.route('/support')

def support():

    return render_template('support.html')



@main.route('/orders')

@login_required

def orders():

    # 這裡目前是靜態顯示，後續可改為從資料庫抓取 User 的訂單

    return render_template('orders.html')



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

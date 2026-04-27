from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required
from app import db
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order, OrderItem
import uuid

# 1. 確保藍圖名稱統稱為 'main'
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # 抓取前 6 個產品顯示在首頁
    products = Product.query.limit(6).all()
    # 抓取所有分類供首頁導航使用
    categories = Category.query.all()
    return render_template('index.html', products=products, categories=categories)

@main_bp.route('/products')
def products():
    # 取得所有產品
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)

@main_bp.route('/product/<int:product_id>')
def product(product_id):
    """產品詳情頁：對應 {{ url_for('main.product', product_id=...) }}"""
    p = Product.query.get_or_404(product_id)
    # 這裡確保對應到 templates/product.html
    return render_template('product.html', product=p)

@main_bp.route('/category/<int:category_id>')
def category(category_id):
    """分類頁面"""
    cat = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category_id).all()
    return render_template('products.html', products=products, category=cat)

@main_bp.route('/support')
def support():
    """支援服務：解決 TemplateNotFound 錯誤"""
    return render_template('support.html')

# --- 購物車邏輯 ---

@main_bp.route('/add_to_cart/<int:product_id>', methods=['POST', 'GET'])
def add_to_cart(product_id):
    # 同時支援 POST (按鈕) 和 GET (連結) 加入購物車
    quantity = int(request.form.get('quantity', 1)) if request.method == 'POST' else 1
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    cart[product_id_str] = cart.get(product_id_str, 0) + quantity
    session['cart'] = cart
    session.modified = True
    flash('已加入購物車', 'success')
    return redirect(url_for('main.view_cart'))

@main_bp.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    if isinstance(cart, dict):
        for pid, quantity in cart.items():
            product_obj = Product.query.get(int(pid))
            if product_obj:
                subtotal = product_obj.price * quantity
                total += subtotal
                cart_items.append({
                    'product': product_obj,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
    return render_template('cart.html', cart_items=cart_items, total=total)

@main_bp.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 0))
    cart = session.get('cart', {})
    pid_str = str(product_id)
    if quantity > 0:
        cart[pid_str] = quantity
    else:
        cart.pop(pid_str, None)
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('main.view_cart'))

@main_bp.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    session.modified = True
    flash('商品已移除', 'info')
    return redirect(url_for('main.view_cart'))

# --- 訂單與結帳邏輯 ---

@main_bp.route('/checkout')
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('購物車是空的', 'info')
        return redirect(url_for('main.view_cart'))
    
    cart_items = []
    total = 0
    for pid, quantity in cart.items():
        product_obj = Product.query.get(int(pid))
        if product_obj:
            subtotal = product_obj.price * quantity
            total += subtotal
            cart_items.append({'product': product_obj, 'quantity': quantity, 'subtotal': subtotal})
    return render_template('checkout.html', cart_items=cart_items, total=total)

@main_bp.route('/place_order', methods=['POST'])
@login_required
def place_order():
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('main.index'))
    
    total = 0
    items_to_create = []
    for pid, quantity in cart.items():
        p = Product.query.get(int(pid))
        if p:
            total += p.price * quantity
            items_to_create.append({'id': p.id, 'qty': quantity, 'price': p.price})
    
    order_num = str(uuid.uuid4()).replace('-', '')[:12].upper()
    order = Order(user_id=current_user.id, order_number=order_num, total_amount=total, status='pending')
    
    try:
        db.session.add(order)
        db.session.flush()
        for item in items_to_create:
            oi = OrderItem(order_id=order.id, product_id=item['id'], quantity=item['qty'], price=item['price'])
            db.session.add(oi)
        db.session.commit()
        session.pop('cart', None)
        flash('訂單建立成功！', 'success')
        return redirect(url_for('main.order_detail', order_id=order.id))
    except Exception as e:
        db.session.rollback()
        flash(f'建立訂單失敗: {str(e)}', 'danger')
        return redirect(url_for('main.checkout'))

@main_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return redirect(url_for('main.index'))
    return render_template('order_detail.html', order=order)

@main_bp.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)

@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    res = Product.query.filter(Product.name.contains(query)).all()
    return render_template('products.html', products=res)

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main_bp.route('/terms')
def terms():
    return render_template('terms.html')
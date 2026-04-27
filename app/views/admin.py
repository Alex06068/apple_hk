import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from app import db
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order

# 核心修改：將藍圖名稱從 'admin' 改為 'admin_custom'，避免與 Flask-Admin 衝突
admin_bp = Blueprint('admin_custom', __name__, url_prefix='/admin_custom')

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # 確保你的 User 模型中有 is_admin 欄位
        if not getattr(current_user, 'is_admin', False):
            flash('您沒有權限訪問此頁面。', 'danger')
            return redirect(url_for('main.index')) # 修正導向為你的主頁藍圖名
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# --- 儀表板 ---
@admin_bp.route('/')
@admin_required
def index():
    product_count = Product.query.count()
    category_count = Category.query.count()
    order_count = Order.query.count()
    return render_template('admin/index.html', 
                           product_count=product_count, 
                           category_count=category_count,
                           order_count=order_count)

# --- 產品管理 ---
@admin_bp.route('/products')
@admin_required
def products():
    all_products = Product.query.all()
    return render_template('admin/products.html', products=all_products)

@admin_bp.route('/product/new', methods=['GET', 'POST'])
@admin_required
def new_product():
    categories = Category.query.all()
    if request.method == 'POST':
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                upload_folder = os.path.join(current_app.static_folder, 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                image_url = url_for('static', filename=f'uploads/{filename}')
        
        if not image_url:
            image_url = request.form.get('image_url', '/static/images/default.jpg')
        
        product = Product(
            name=request.form['name'],
            subtitle=request.form['subtitle'],
            description=request.form['description'],
            price=float(request.form['price']),
            image_url=image_url,
            category_id=int(request.form['category_id']),
            is_featured='is_featured' in request.form
        )
        db.session.add(product)
        db.session.commit()
        flash('產品已新增！', 'success')
        return redirect(url_for('admin_custom.products'))
    return render_template('admin/product_form.html', categories=categories, product=None)

@admin_bp.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    if request.method == 'POST':
        product.name = request.form['name']
        product.subtitle = request.form['subtitle']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.category_id = int(request.form['category_id'])
        product.is_featured = 'is_featured' in request.form
        
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                upload_folder = os.path.join(current_app.static_folder, 'uploads')
                file.save(os.path.join(upload_folder, filename))
                product.image_url = url_for('static', filename=f'uploads/{filename}')
        
        db.session.commit()
        flash('產品已更新！', 'success')
        return redirect(url_for('admin_custom.products'))
    return render_template('admin/product_form.html', categories=categories, product=product)

@admin_bp.route('/product/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('產品已刪除！', 'success')
    return redirect(url_for('admin_custom.products'))

# --- 訂單管理 ---
@admin_bp.route('/orders')
@admin_required
def orders():
    all_orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('admin/orders.html', orders=all_orders)

@admin_bp.route('/order/<int:order_id>/status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ['pending', 'processing', 'completed', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash(f'訂單 #{order.id} 狀態已更新為 {new_status}', 'success')
    return redirect(url_for('admin_custom.orders'))
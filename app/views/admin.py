from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import (
    User, Product, Category, Review, Cart, Address, Payment,
    Order, OrderItem, Coupon, Wishlist, Notification
)
from functools import wraps
from wtforms import Form, StringField, IntegerField, FloatField, TextAreaField, SelectField, BooleanField, DateTimeField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Optional, Email, Length
import datetime

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.username != 'admin':
            flash('无权访问', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated

# 模型配置（同上，略去重复，确保有 'list_fields' 等）
MODELS_CONFIG = {
    'user': {
        'model': User,
        'name': '用户',
        'list_fields': ['id', 'username', 'email', 'created_at'],
        'form_fields': ['username', 'email', 'password'],
        'fk_options': {},
    },
    'product': {
        'model': Product,
        'name': '产品',
        'list_fields': ['id', 'name', 'price', 'category_id'],
        'form_fields': ['name', 'description', 'price', 'image_url', 'category_id'],
        'fk_options': {'category_id': ('category', 'id', 'name')},
    },
    # ... 其他模型配置（请确保包含所有12个模型）
    'category': {
        'model': Category,
        'name': '分类',
        'list_fields': ['id', 'name'],
        'form_fields': ['name'],
        'fk_options': {},
    },
    'review': {
        'model': Review,
        'name': '评论',
        'list_fields': ['id', 'user_id', 'product_id', 'rating', 'comment'],
        'form_fields': ['user_id', 'product_id', 'rating', 'comment'],
        'fk_options': {'user_id': ('user', 'id', 'username'), 'product_id': ('product', 'id', 'name')},
    },
    'cart': {
        'model': Cart,
        'name': '购物车',
        'list_fields': ['id', 'user_id', 'product_id', 'quantity'],
        'form_fields': ['user_id', 'product_id', 'quantity'],
        'fk_options': {'user_id': ('user', 'id', 'username'), 'product_id': ('product', 'id', 'name')},
    },
    'address': {
        'model': Address,
        'name': '地址',
        'list_fields': ['id', 'user_id', 'recipient', 'phone', 'address_line'],
        'form_fields': ['user_id', 'recipient', 'phone', 'address_line', 'is_default'],
        'fk_options': {'user_id': ('user', 'id', 'username')},
    },
    'payment': {
        'model': Payment,
        'name': '支付',
        'list_fields': ['id', 'order_id', 'method', 'amount', 'status'],
        'form_fields': ['order_id', 'method', 'amount', 'status'],
        'fk_options': {'order_id': ('order', 'id', 'order_number')},
    },
    'order': {
        'model': Order,
        'name': '订单',
        'list_fields': ['id', 'user_id', 'order_number', 'total_amount', 'status', 'created_at'],
        'form_fields': ['user_id', 'order_number', 'total_amount', 'status'],
        'fk_options': {'user_id': ('user', 'id', 'username')},
    },
    'order_item': {
        'model': OrderItem,
        'name': '订单项',
        'list_fields': ['id', 'order_id', 'product_id', 'quantity', 'price'],
        'form_fields': ['order_id', 'product_id', 'quantity', 'price'],
        'fk_options': {'order_id': ('order', 'id', 'order_number'), 'product_id': ('product', 'id', 'name')},
    },
    'coupon': {
        'model': Coupon,
        'name': '优惠券',
        'list_fields': ['id', 'code', 'discount_type', 'discount_value', 'expiry_date'],
        'form_fields': ['code', 'discount_type', 'discount_value', 'min_spend', 'expiry_date', 'usage_limit'],
        'fk_options': {},
    },
    'wishlist': {
        'model': Wishlist,
        'name': '收藏',
        'list_fields': ['id', 'user_id', 'product_id', 'added_at'],
        'form_fields': ['user_id', 'product_id'],
        'fk_options': {'user_id': ('user', 'id', 'username'), 'product_id': ('product', 'id', 'name')},
    },
    'notification': {
        'model': Notification,
        'name': '通知',
        'list_fields': ['id', 'user_id', 'title', 'is_read', 'created_at'],
        'form_fields': ['user_id', 'title', 'message'],
        'fk_options': {'user_id': ('user', 'id', 'username')},
    },
}

# 辅助函数：获取外键选项
def get_fk_choices(fk_info):
    related_model_name, pk_field, display_field = fk_info
    # 动态获取模型类
    model_map = {
        'user': User,
        'product': Product,
        'category': Category,
        'order': Order,
    }
    related_model = model_map.get(related_model_name)
    if not related_model:
        return []
    items = related_model.query.all()
    return [(str(getattr(item, pk_field)), str(getattr(item, display_field))) for item in items]

def create_dynamic_form(model_key, obj=None):
    config = MODELS_CONFIG[model_key]
    model = config['model']
    form_fields = config['form_fields']
    fk_options = config.get('fk_options', {})

    class DynamicForm(Form):
        pass

    for field_name in form_fields:
        if field_name in fk_options:
            choices = get_fk_choices(fk_options[field_name])
            setattr(DynamicForm, field_name, SelectField(field_name, choices=choices, coerce=str, validators=[DataRequired()]))
        else:
            # 简化，统一使用 StringField
            setattr(DynamicForm, field_name, StringField(field_name, validators=[Optional()]))
    return DynamicForm

@admin.route('/admin')
@admin_required
def index():
    return render_template('admin/index.html', models=MODELS_CONFIG.keys())

# 动态生成 CRUD 路由，为每个模型指定唯一的 endpoint
for model_key, config in MODELS_CONFIG.items():
    model = config['model']
    name = config['name']
    list_fields = config['list_fields']

    # 列表页
    @admin.route(f'/admin/{model_key}', endpoint=f'list_{model_key}')
    @admin_required
    def list_items(model_key=model_key, model=model, list_fields=list_fields, name=name):
        items = model.query.all()
        return render_template('admin/list.html', items=items, fields=list_fields, name=name, model_key=model_key)

    # 添加页
    @admin.route(f'/admin/{model_key}/new', endpoint=f'new_{model_key}', methods=['GET', 'POST'])
    @admin_required
    def new_item(model_key=model_key, model=model, name=name):
        FormClass = create_dynamic_form(model_key)
        form = FormClass(request.form)
        if request.method == 'POST' and form.validate():
            obj = model()
            for field in config['form_fields']:
                value = getattr(form, field).data
                setattr(obj, field, value)
            db.session.add(obj)
            db.session.commit()
            flash(f'{name} 添加成功', 'success')
            return redirect(url_for(f'admin.list_{model_key}'))
        return render_template('admin/form.html', form=form, name=name, action='new', model_key=model_key)

    # 编辑页
    @admin.route(f'/admin/{model_key}/edit/<int:id>', endpoint=f'edit_{model_key}', methods=['GET', 'POST'])
    @admin_required
    def edit_item(id, model_key=model_key, model=model, name=name):
        item = model.query.get_or_404(id)
        FormClass = create_dynamic_form(model_key)
        form = FormClass(request.form, obj=item)
        if request.method == 'POST' and form.validate():
            for field in config['form_fields']:
                value = getattr(form, field).data
                setattr(item, field, value)
            db.session.commit()
            flash(f'{name} 更新成功', 'success')
            return redirect(url_for(f'admin.list_{model_key}'))
        # 预填充
        for field in config['form_fields']:
            if hasattr(form, field):
                getattr(form, field).data = getattr(item, field, None)
        return render_template('admin/form.html', form=form, name=name, action='edit', model_key=model_key, item_id=id)

    # 删除
    @admin.route(f'/admin/{model_key}/delete/<int:id>', endpoint=f'delete_{model_key}')
    @admin_required
    def delete_item(id, model_key=model_key, model=model, name=name):
        item = model.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        flash(f'{name} 已删除', 'success')
        return redirect(url_for(f'admin.list_{model_key}'))


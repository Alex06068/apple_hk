from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/products')
def products():
    # 这里可以放你的产品列表数据
    items = [
        {'name': 'iPhone 15 Pro', 'price': 'HK$ 8,599', 'img': 'iphone.png'},
        {'name': 'MacBook Air', 'price': 'HK$ 7,799', 'img': 'mac.png'}
    ]
    return render_template('products.html', items=items)

@main.route('/cart')
def view_cart():
    return render_template('cart.html')
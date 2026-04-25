from flask import Blueprint, render_template

apple_bp = Blueprint('apple', __name__)

@apple_bp.route('/apple')
@apple_bp.route('/apple-store')
def apple_store():
    return render_template('apple_store.html')

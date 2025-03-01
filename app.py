from flask import Flask, render_template
from flask_login import LoginManager
from database import db
from database.models import Cliente, Vendedor  # Importar as classes aqui
from controllers.auth_controller import auth_bp
from controllers.product_controller import product_bp
from controllers.cart_controller import cart_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'ULTRAMEGADIFICIL'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    cliente = Cliente.query.get(int(user_id))
    if cliente:
        return cliente
    vendedor = Vendedor.query.get(int(user_id))
    return vendedor

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)
app.register_blueprint(cart_bp)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

from database.models import *
from flask import Flask, request, render_template, redirect, url_for, flash
from database import db
from datetime import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'ULTRAMEGADIFICIL'

db.init_app(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    cliente = Cliente.query.get(int(user_id))
    if cliente:
        return cliente
    vendedor = Vendedor.query.get(int(user_id))
    return vendedor

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
    
        cliente = Cliente.query.filter_by(email=email).first()
        if cliente and cliente.check_password(senha):
            login_user(cliente)
            return redirect(url_for('loja'))
        
        vendedor = Vendedor.query.filter_by(email=email).first()
        if vendedor and vendedor.check_password(senha):
            login_user(vendedor)
            return redirect(url_for('cadastro_produtos'))
        
        flash('Email ou senha inválidos')
    
    return render_template('login.html')

@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']
        if Cliente.query.filter_by(email=email).first() or Vendedor.query.filter_by(email=email).first():
            return "Email já cadastrado!", 400
        else:
            if tipo == "cliente":
                Cliente.cadastrar_cliente(nome, email, senha)
            else:
                Vendedor.cadastrar_vendedor(nome, email, senha)
            return redirect(url_for('login'))
    return render_template('cadastro_user.html')


def verificar_tipo_usuario_email(email):
    # Verifica se o email pertence a um cliente
    cliente = Cliente.query.filter_by(email=email).first()
    if cliente:
        return "cliente"
    
    # Verifica se o email pertence a um vendedor
    vendedor = Vendedor.query.filter_by(email=email).first()
    if vendedor:
        return "vendedor"
    
    return None

@app.route('/cadastrar_produto', methods=['GET', 'POST'])
@login_required
def cadastro_produtos():
 
    vendedor = Vendedor.query.get(current_user.id) 
    if not vendedor:
        flash("Você não tem permissão para cadastrar produtos.")
        return redirect(url_for('loja'))

    # Checa produtos que precisam ser repostos (não esta funcionando muito bem)
    produtos_para_repor = Produto.query.filter(Produto.estoque <= 0).all()
    if produtos_para_repor:
        flash("Atenção: Produtos que precisam ser repostos: " + ", ".join([p.nome for p in produtos_para_repor]))

    if request.method == 'POST':
        nome = request.form['nome']
        preco = float(request.form['preco'])
        estoque = int(request.form['estoque'])

        # Verifica se o produto já existe antes de cadastrar
        if Produto.query.filter_by(nome=nome).first():
            flash("Produto já cadastrado!")
            return redirect(url_for('cadastro_produtos'))

        Produto.cadastrar_produto(nome, preco, estoque)
        flash("Produto cadastrado com sucesso")
        return redirect(url_for('cadastro_produtos'))  # Redireciona após o cadastro

    return render_template('cadastro_produto.html')

@app.route('/loja', methods=['GET', 'POST'])
@login_required
def loja():
    produtos = Produto.lista_produtos()
    return render_template('loja.html', produtos=produtos)
    
@app.route('/adicionar_ao_carrinho/<int:produto_id>', methods=['POST'])
@login_required
def adicionar_ao_carrinho(produto_id):
    produto = Produto.query.get(produto_id)

    if produto.estoque <= 0:
        flash("Produto indisponível.")
        return redirect(url_for('loja'))
    
    carrinho_item = Carrinho.query.filter_by(cliente_id=current_user.id, produto_id=produto_id).first()
    
    if carrinho_item:
        if carrinho_item.quantidade < produto.estoque:
            carrinho_item.quantidade += 1
        else:
            flash("Quantidade máxima atingida para este produto.")
    else:
        if produto.estoque > 0:  # Verifica novamente
            carrinho_item = Carrinho(cliente_id=current_user.id, produto_id=produto_id, quantidade=1)
            db.session.add(carrinho_item)
        else:
            flash("Produto esgotado no momento.")
    
    db.session.commit()
    return redirect(url_for('loja'))


@app.route('/carrinho')
@login_required
def carrinho():
    itens_carrinho = Carrinho.query.filter_by(cliente_id=current_user.id).all()
    total = sum(item.produto.preco * item.quantidade for item in itens_carrinho)
    return render_template('carrinho.html', carrinho2=itens_carrinho, total=total)


@app.route('/alterar_quantidade/<int:item_id>/<action>', methods=['POST'])
@login_required
def alterar_quantidade(item_id, action):
    carrinho_item = Carrinho.query.get(item_id)

    if action == 'increment':
        if carrinho_item.quantidade < carrinho_item.produto.estoque:
            carrinho_item.quantidade += 1
        else:
            flash("Quantidade máxima atingida.")
    elif action == 'decrement':
        if carrinho_item.quantidade > 1:
            carrinho_item.quantidade -= 1
        else:
            db.session.delete(carrinho_item)
            flash("Produto removido do carrinho.")
    
    db.session.commit()
    return redirect(url_for('carrinho'))

    db.session.commit()
    return redirect(url_for('carrinho'))

@app.route('/finalizar_pedido')
@login_required
def finalizar_pedido():
    itens_carrinho = Carrinho.query.filter_by(cliente_id=current_user.id).all()
    total = sum(item.produto.preco * item.quantidade for item in itens_carrinho)
    data = datetime.now()
    novo_pedido = Pedido(cliente_id=current_user.id, total=total, data=data)
    db.session.add(novo_pedido)
    db.session.commit()

    # Limpa o carrinho após finalizar o pedido
    for item in itens_carrinho:
        db.session.delete(item)

    db.session.commit()
    return redirect(url_for('loja'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

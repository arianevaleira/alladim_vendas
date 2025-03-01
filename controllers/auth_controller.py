from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from database.models import Cliente, Vendedor

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/cadastrar_usuario', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']
        
        if Cliente.query.filter_by(email=email).first() or Vendedor.query.filter_by(email=email).first():
            flash("Email já cadastrado!", "error")
            return redirect(url_for('auth.cadastro'))
        else:
            if tipo == "cliente":
                Cliente.cadastrar_cliente(nome, email, senha)
            else:
                Vendedor.cadastrar_vendedor(nome, email, senha)
            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for('auth.login'))
    
    return render_template('cadastro_user.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
    
        cliente = Cliente.query.filter_by(email=email).first()
        if cliente and cliente.check_password(senha):
            session['user_tipo'] = "cliente"
            login_user(cliente)
            return redirect(url_for('product.loja'))
        
        vendedor = Vendedor.query.filter_by(email=email).first()
        if vendedor and vendedor.check_password(senha):
            session['user_tipo'] = "vendedor"
            login_user(vendedor)
            return redirect(url_for('product.home_vendedor'))
        
        flash('Email ou senha inválidos', "error")
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Você foi desconectado com sucesso.", "success")
    return redirect(url_for('auth.login'))  # Redireciona para a página de login
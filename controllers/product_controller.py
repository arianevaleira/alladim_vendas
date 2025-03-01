from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from database.models import Produto, Carrinho, Pedido
from datetime import datetime

product_bp = Blueprint('product', __name__)

@product_bp.route('/cadastrar_produto', methods=['GET', 'POST'])
@login_required
def cadastro_produtos():
    if session.get('user_tipo') != "vendedor":
        flash("Acesso negado. Somente vendedores podem cadastrar produtos.", "error")
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        nome = request.form['nome']
        preco = float(request.form['preco'])
        estoque = int(request.form['estoque'])

        if Produto.query.filter_by(nome=nome).first():
            flash("Produto já cadastrado!", "error")
            return redirect(url_for('product.cadastro_produtos'))

        Produto.cadastrar_produto(nome, preco, estoque)
        flash("Produto cadastrado com sucesso!", "success")
        return redirect(url_for('product.home_vendedor'))

    return render_template('cadastro_produto.html')


@product_bp.route('/loja', methods=['GET', 'POST'])
@login_required
def loja():
    produtos = Produto.lista_produtos()
    return render_template('loja.html', produtos=produtos)


@product_bp.route('/home_vendedor')
@login_required
def home_vendedor():
    return render_template('home_vendedor.html', vendedor=current_user.nome)


@product_bp.route('/lista_reposicao', methods=['GET', 'POST'])
@login_required
def lista_reposicao():
    if session.get('user_tipo') != "vendedor":
        flash("Acesso negado. Somente vendedores podem acessar esta página.", "error")
        return redirect(url_for('auth.login'))
    
    produtos_para_repor = Produto.query.filter(Produto.estoque == 0).all()
    return render_template('lista_reposicao.html', produtos_para_repor=produtos_para_repor)


@product_bp.route('/repor_produto/<int:id>', methods=['POST'])
@login_required
def repor_produto(id):
    novo_estoque = request.form['qntd']
    Produto.alterar_estoque(id, novo_estoque)
    flash("Estoque atualizado com sucesso!", "success")
    return redirect(url_for('product.lista_reposicao'))
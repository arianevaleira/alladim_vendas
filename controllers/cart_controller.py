from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from database.models import Carrinho, Produto, Pedido  # Importando Pedido
from datetime import datetime
from database import db  # Certifique-se de que o db está importado

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/adicionar_ao_carrinho/<int:produto_id>', methods=['POST'])
@login_required
def adicionar_ao_carrinho(produto_id):
    produto = Produto.query.get(produto_id)

    if produto.estoque <= 0:
        flash("Produto indisponível.")
        return redirect(url_for('product.loja'))
    
    carrinho_item = Carrinho.query.filter_by(cliente_id=current_user.id, produto_id=produto_id).first()
    
    if carrinho_item:
        if carrinho_item.quantidade < produto.estoque:
            carrinho_item.quantidade += 1
        else:
            flash("Quantidade máxima atingida para este produto.")
    else:
        if produto.estoque > 0:
            carrinho_item = Carrinho(cliente_id=current_user.id, produto_id=produto_id, quantidade=1)
            db.session.add(carrinho_item)
        else:
            flash("Produto esgotado no momento.")
    
    db.session.commit()
    return redirect(url_for('product.loja'))

@cart_bp.route('/carrinho')
@login_required
def carrinho():
    itens_carrinho = Carrinho.query.filter_by(cliente_id=current_user.id).all()
    total = sum(item.produto.preco * item.quantidade for item in itens_carrinho)
    return render_template('carrinho.html', carrinho2=itens_carrinho, total=total)

@cart_bp.route('/alterar_quantidade/<int:item_id>/<action>', methods=['POST'])
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
    return redirect(url_for('cart.carrinho'))

@cart_bp.route('/finalizar_pedido', methods=['GET'])
@login_required
def finalizar_pedido():
    itens_carrinho = Carrinho.query.filter_by(cliente_id=current_user.id).all()
    total = sum(item.produto.preco * item.quantidade for item in itens_carrinho)
    
    if not itens_carrinho:
        flash("Seu carrinho está vazio.")
        return redirect(url_for('cart.carrinho'))

    novo_pedido = Pedido(cliente_id=current_user.id, total=total, data=datetime.now())
    db.session.add(novo_pedido)

    for item in itens_carrinho:
        produto = Produto.query.get(item.produto_id)
        if produto:
            produto.estoque -= item.quantidade
            if produto.estoque < 0:
                flash("Estoque insuficiente para finalizar o pedido!", "error")
                return redirect(url_for('cart.carrinho'))

    db.session.commit()

    for item in itens_carrinho:
        db.session.delete(item)

    db.session.commit()
    flash("Pedido finalizado com sucesso!", "success")
    return redirect(url_for('product.loja'))
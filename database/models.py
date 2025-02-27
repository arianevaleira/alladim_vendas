from database import db, Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import create_engine, ForeignKey
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Cliente(db.Model, UserMixin):
    __tablename__ = 'clientes'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str]
    email: Mapped[str]
    senha: Mapped[str]
    pedidos: Mapped[list['Pedido']] = relationship(backref='cliente')
    carrinho: Mapped[list['Carrinho']] = relationship(backref='cliente')

    @classmethod
    def cadastrar_cliente(cls, nome, email, senha):
        hash_senha = generate_password_hash(senha)
        add_cliente = Cliente(nome=nome, email=email, senha=hash_senha)
        db.session.add(add_cliente)
        db.session.commit()

    def check_password(self, senha):
        return check_password_hash(self.senha, senha)

class Vendedor(db.Model, UserMixin):
    __tablename__ = 'vendedores'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    nome: Mapped[str]
    email: Mapped[str]
    senha: Mapped[str]

    @classmethod
    def cadastrar_vendedor(cls, nome, email, senha):
        hash_senha = generate_password_hash(senha)
        add_vendedor = Vendedor(nome=nome, email=email, senha=hash_senha)
        db.session.add(add_vendedor)
        db.session.commit()

    def check_password(self, senha):
        return check_password_hash(self.senha, senha)

class Produto(db.Model):
    __tablename__ = 'produtos'
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    preco: Mapped[float] = mapped_column(nullable=False)
    estoque: Mapped[int]
    carrinho: Mapped[list['Carrinho']] = relationship(backref='produto')

    def __repr__(self):
        return f'<Produto(id={self.id}, nome={self.nome}, preco={self.preco})>'

    @classmethod
    def cadastrar_produto(cls, nome, preco, estoque):
        add_produto = Produto(nome=nome, preco=preco, estoque=estoque)
        db.session.add(add_produto)
        db.session.commit()

    @classmethod
    def lista_produtos(cls):
        return cls.query.all()
    
    @classmethod
    def alterar_estoque(cls, id, novo_estoque):
        produto = cls.query.get(id)
        if produto is not None:
            produto.estoque = novo_estoque
            db.session.commit()



class Carrinho(db.Model):
    __tablename__ = 'carrinho'
    id: Mapped[int] = mapped_column(primary_key=True)
    quantidade: Mapped[int] = mapped_column(default=1)
    cliente_id : Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    produto_id : Mapped[int] = mapped_column(ForeignKey("produtos.id"))

    def __repr__(self):
        return f'<Carrinho(id={self.id}, produto_id={self.produto_id}, quantidade={self.quantidade})>'
    
class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[datetime]
    total: Mapped[float]
    cliente_id : Mapped[int] = mapped_column(ForeignKey("clientes.id"))

"""Carrega categorias, produtos e professores/funcionarios iniciais.

Uso:  python manage.py seed_dados
Pode rodar varias vezes: nao duplica nada (usa get_or_create).
EDITE as listas abaixo com os nomes e precos reais da cantina.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand

from cantina.models import Categoria, Pessoa, Produto

# categoria: [(produto, preco), ...]
PRODUTOS = {
    'Salgados': [
        ('Coxinha', '6.00'), ('Pastel de carne', '7.00'), ('Pastel de queijo', '7.00'),
        ('Pastel de frango', '7.00'), ('Esfiha de carne', '5.50'), ('Enroladinho de salsicha', '5.00'),
        ('Pão de queijo', '4.00'), ('Empada', '6.00'), ('Risole de presunto e queijo', '5.50'),
    ],
    'Lanches': [
        ('Misto quente', '7.00'), ('Hambúrguer', '12.00'), ('X-Salada', '14.00'),
        ('Cachorro-quente', '9.00'), ('Sanduíche natural', '10.00'), ('Pão na chapa', '4.50'),
    ],
    'Refeições': [
        ('Prato feito', '22.00'), ('Marmita', '20.00'), ('Salada de frutas', '8.00'),
    ],
    'Doces': [
        ('Brigadeiro', '3.00'), ('Beijinho', '3.00'), ('Bolo no pote', '8.00'),
        ('Fatia de bolo', '6.00'), ('Brownie', '7.00'), ('Pudim', '6.50'),
        ('Barra de chocolate', '5.00'), ('Pirulito', '1.00'), ('Bala (unidade)', '0.50'),
    ],
    'Bebidas': [
        ('Água mineral 500ml', '3.00'), ('Suco natural 300ml', '7.00'), ('Suco de caixinha', '4.00'),
        ('Refrigerante lata', '6.00'), ('Refrigerante 600ml', '8.00'), ('Café', '3.00'),
        ('Achocolatado', '5.00'), ('Isotônico', '8.00'),
    ],
    'Geladinhos e Sorvetes': [
        ('Geladinho', '2.50'), ('Picolé', '4.00'), ('Sorvete (copinho)', '6.00'),
    ],
}

# Nomes de EXEMPLO (50 professores e 20 funcionarios). Troque pelos nomes reais
# aqui ou depois pelo sistema (tela Pessoas -> Editar).
_NOMES = ['Ana', 'Carlos', 'Fernanda', 'Ricardo', 'Juliana', 'Marcos', 'Patrícia', 'Roberto', 'Luciana', 'Paulo',
          'Camila', 'Rafael', 'Beatriz', 'Eduardo', 'Mariana', 'Felipe', 'Aline', 'Bruno', 'Larissa', 'Gustavo',
          'Renata', 'André', 'Vanessa', 'Diego', 'Cláudia']
_SOBRENOMES = ['Souza', 'Pereira', 'Lima', 'Alves', 'Costa', 'Oliveira', 'Santos', 'Ferreira', 'Rocha', 'Ribeiro',
               'Martins', 'Barbosa', 'Gomes', 'Carvalho']


def _gerar(qtd, tipo, prefixo, deslocamento):
    lista = []
    for i in range(qtd):
        n = i + deslocamento
        lista.append((_NOMES[n % len(_NOMES)], _SOBRENOMES[(n * 3 + n // len(_NOMES)) % len(_SOBRENOMES)],
                      tipo, f'{prefixo}{i + 1:03d}'))
    return lista


PESSOAS = _gerar(50, 'PROFESSOR', 'P', 0) + _gerar(20, 'FUNCIONARIO', 'F', 7)


class Command(BaseCommand):
    help = 'Carrega categorias, produtos e professores/funcionarios iniciais.'

    def handle(self, *args, **opts):
        novos_prod = 0
        for cat_nome, itens in PRODUTOS.items():
            cat, _ = Categoria.objects.get_or_create(nome=cat_nome)
            for nome, preco in itens:
                _, criado = Produto.objects.get_or_create(
                    nome=nome, categoria=cat,
                    defaults={'preco': Decimal(preco), 'quantidade': 50},
                )
                novos_prod += criado

        novas_pessoas = 0
        for nome, sobrenome, tipo, matricula in PESSOAS:
            _, criado = Pessoa.objects.get_or_create(
                nome=nome, sobrenome=sobrenome, tipo=tipo, matricula=matricula,
                defaults={'pode_pagar_mensalmente': True},
            )
            novas_pessoas += criado

        self.stdout.write(self.style.SUCCESS(
            f'Pronto: {novos_prod} produtos e {novas_pessoas} pessoas novas '
            f'(categorias: {Categoria.objects.count()}).'
        ))

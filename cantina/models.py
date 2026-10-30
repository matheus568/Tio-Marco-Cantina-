from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.CharField(max_length=150, blank=True, null=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Pessoa(models.Model):
    TIPO_CHOICES = (
        ('PROFESSOR', 'Professor'),
        ('FUNCIONARIO', 'Funcionário'),
        ('ALUNO', 'Aluno'),
        ('VISITANTE', 'Visitante'),
    )
    nome = models.CharField(max_length=80)
    sobrenome = models.CharField(max_length=80)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    matricula = models.CharField(max_length=40, blank=True, null=True)
    pode_pagar_mensalmente = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'
        ordering = ['nome', 'sobrenome']

    def __str__(self):
        return f'{self.nome} {self.sobrenome} - {self.get_tipo_display()}'

    def nome_completo(self):
        return f'{self.nome} {self.sobrenome}'

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='produtos')
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    quantidade = models.IntegerField(default=0)
    foto = models.ImageField(upload_to='produtos/', blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    ICONES = (
        ('coxinha', '🍗'), ('pastel', '🥟'), ('esfiha', '🥟'), ('enrolad', '🌭'), ('pão de queijo', '🧀'),
        ('empada', '🥧'), ('risole', '🥟'), ('misto', '🥪'), ('hambúrguer', '🍔'), ('x-', '🍔'),
        ('cachorro', '🌭'), ('sanduíche', '🥪'), ('pão', '🍞'), ('prato', '🍛'), ('marmita', '🍱'),
        ('salada', '🥗'), ('brigadeiro', '🍫'), ('beijinho', '🍬'), ('bolo', '🍰'), ('brownie', '🍫'),
        ('pudim', '🍮'), ('chocolate', '🍫'), ('pirulito', '🍭'), ('bala', '🍬'), ('água', '💧'),
        ('suco', '🧃'), ('refrigerante', '🥤'), ('café', '☕'), ('achocolatado', '🥛'), ('isotônico', '🥤'),
        ('geladinho', '🧊'), ('picolé', '🍦'), ('sorvete', '🍨'),
    )

    @property
    def icone(self):
        nome = self.nome.lower()
        for chave, emoji in self.ICONES:
            if chave in nome:
                return emoji
        return '🍽️'

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['categoria__nome', 'nome']

    def __str__(self):
        return self.nome

class Venda(models.Model):
    FORMA_PAGAMENTO = (
        ('CREDITO', 'Crédito'),
        ('DEBITO', 'Débito'),
        ('DINHEIRO', 'Dinheiro'),
        ('PIX', 'Pix'),
    )
    TIPO_PAGAMENTO = (
        ('HORA', 'Na hora'),
        ('MENSAL', 'Mensal'),
    )
    STATUS_CHOICES = (
        ('PAGO', 'Pago'),
        ('ABERTA', 'Em aberto'),
    )

    pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT, null=True, blank=True, related_name='vendas')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    forma_pagamento = models.CharField(max_length=10, choices=FORMA_PAGAMENTO)
    tipo_pagamento = models.CharField(max_length=10, choices=TIPO_PAGAMENTO, default='HORA')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    vencimento = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PAGO')
    observacoes = models.TextField(blank=True, null=True)
    data_venda = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-data_venda']

    def __str__(self):
        return f'Venda #{self.id} - R$ {self.total}'

class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Item da Venda'
        verbose_name_plural = 'Itens da Venda'

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome}'

class ContaMensal(models.Model):
    STATUS_CHOICES = (
        ('ABERTA', 'Em aberto'),
        ('PAGA', 'Paga'),
    )

    pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT, related_name='contas_mensais')
    venda = models.ForeignKey(Venda, on_delete=models.PROTECT)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    vencimento = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ABERTA')
    data_pagamento = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Conta Mensal'
        verbose_name_plural = 'Contas Mensais'
        ordering = ['status', 'vencimento']

    def __str__(self):
        return f'Conta #{self.id} - {self.pessoa.nome_completo()} - R$ {self.valor}'

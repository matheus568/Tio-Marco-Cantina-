from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Q
from decimal import Decimal
from datetime import datetime

from .models import Categoria, Pessoa, Produto, Venda, ItemVenda, ContaMensal
from .forms import PessoaForm, CategoriaForm, ProdutoForm


def eh_admin(user):
    return user.is_authenticated and user.is_staff


def home(request):
    """Pagina publica: produtos com precos e formas de pagamento."""
    categorias = Categoria.objects.filter(ativa=True).prefetch_related('produtos')
    grupos = []
    for c in categorias:
        prods = [p for p in c.produtos.all() if p.ativo]
        if prods:
            grupos.append({'categoria': c, 'produtos': prods})
    return render(request, 'cantina/home.html', {
        'grupos': grupos,
        'formas': Venda.FORMA_PAGAMENTO,
    })


def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        user = authenticate(request, username=username, password=senha)
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Acesso restrito apenas ao Administrador.')
    return render(request, 'cantina/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Sessão encerrada.')
    return redirect('home')


@login_required(login_url='login')
@user_passes_test(eh_admin, login_url='login')
def dashboard(request):
    hoje = timezone.localdate()
    vendas_hoje = Venda.objects.filter(data_venda__date=hoje)
    contas_abertas_qs = ContaMensal.objects.filter(status='ABERTA')
    context = {
        'total_hoje': vendas_hoje.aggregate(t=Sum('total'))['t'] or Decimal('0.00'),
        'qtd_vendas_hoje': vendas_hoje.count(),
        'total_produtos': Produto.objects.filter(ativo=True).count(),
        'total_pessoas': Pessoa.objects.filter(ativo=True).count(),
        'contas_abertas': contas_abertas_qs.count(),
        'valor_contas_abertas': contas_abertas_qs.aggregate(t=Sum('valor'))['t'] or Decimal('0.00'),
        'ultimas_vendas': Venda.objects.select_related('pessoa', 'usuario')[:6],
        'produtos_baixo': Produto.objects.filter(ativo=True, quantidade__lt=10).order_by('quantidade')[:6],
        'contas_vencendo': contas_abertas_qs.select_related('pessoa').order_by('vencimento')[:6],
        'hoje': hoje,
    }
    return render(request, 'cantina/dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(eh_admin, login_url='login')
def categorias_lista(request):
    if request.method == 'POST':
        nome = (request.POST.get('nome') or '').strip()
        descricao = (request.POST.get('descricao') or '').strip()
        if nome:
            _, criada = Categoria.objects.get_or_create(nome=nome, defaults={'descricao': descricao})
            if criada:
                messages.success(request, 'Categoria cadastrada com sucesso.')
            else:
                messages.error(request, 'Ja existe uma categoria com esse nome.')
        else:
            messages.error(request, 'Informe o nome da categoria.')
        return redirect('categorias')
    categorias = Categoria.objects.all()
    return render(request, 'cantina/categorias.html', {'categorias': categorias})


@login_required(login_url='login')
@user_passes_test(eh_admin, login_url='login')
def pessoas_lista(request):
    tipo = request.GET.get('tipo', '')
    pessoas = Pessoa.objects.annotate(
        a_pagar=Sum('contas_mensais__valor', filter=Q(contas_mensais__status='ABERTA'))
    )
    if tipo in dict(Pessoa.TIPO_CHOICES):
        pessoas = pessoas.filter(tipo=tipo)
    return render(request, 'cantina/pessoas.html', {
        'pessoas': pessoas, 'tipo': tipo, 'tipos': Pessoa.TIPO_CHOICES,
    })


@login_required(login_url='login')
@user_passes_test(eh_admin, login_url='login')
def pessoa_novo(request):
    form = PessoaForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Pessoa cadastrada com sucesso.')
        return redirect('pessoas')
    return render(request, 'cantina/pessoa_form.html', {'form': form, 'titulo': 'Nova Pessoa'})


@login_required(login_url='login')
@user_passes_test(eh_admin, login_url='login')
def pessoa_editar(request, pk):
    pessoa = get_object_or_404(Pessoa, pk=pk)
    form = PessoaForm(request.POST or None, instance=pessoa)
    if form.is_valid():
        form.save()
        messages.success(request, 'Pessoa atualizada com sucesso.')
        return redirect('pessoas')
    return render(request, 'cantina/pessoa_form.html', {'form': form, 'titulo': 'Editar Pessoa'})


@login_required(login_url='login')
@user_passes_test(eh_admin, login_url='login')
def produtos_lista(request):
    produtos = Produto.objects.select_related('categoria').all()
    return render(request, 'cantina/produtos.html', {'produtos': produtos})


@login_required(login_url='login')
@user_passes_test(eh_admin, login_url='login')
def produto_novo(request):
    form = ProdutoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Produto cadastrado com sucesso.')
        return redirect('produtos')
    return render(request, 'cantina/produto_form.html', {'form': form, 'titulo': 'Novo Produto'})


@login_required(login_url='login')
@user_passes_test(eh_admin, login_url='login')
def produto_editar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    form = ProdutoForm(request.POST or None, request.FILES or None, instance=produto)
    if form.is_valid():
        form.save()
        messages.success(request, 'Produto atualizado com sucesso.')
        return redirect('produtos')
    return render(request, 'cantina/produto_form.html', {'form': form, 'titulo': 'Editar Produto'})


@login_required(login_url='login')
@user_passes_test(eh_admin, login_url='login')
def produtos_tela(request):
    categorias = Categoria.objects.filter(ativa=True)
    produtos = Produto.objects.filter(ativo=True, quantidade__gt=0).select_related('categoria')
    return render(request, 'cantina/produtos_tela.html', {'categorias': categorias, 'produtos': produtos})


@login_required(login_url='login')
@user_passes_test(eh_admin, login_url='login')
def venda_nova(request):
    pessoas = Pessoa.objects.filter(ativo=True).order_by('tipo', 'nome')
    produtos = Produto.objects.filter(ativo=True, quantidade__gt=0).select_related('categoria')

    if request.method == 'POST':
        pessoa_id = request.POST.get('pessoa_id') or None
        forma_pagamento = request.POST.get('forma_pagamento')
        itens_ids = request.POST.getlist('itens')

        formas_validas = [f[0] for f in Venda.FORMA_PAGAMENTO]
        if forma_pagamento not in formas_validas:
            messages.error(request, 'Selecione a forma de pagamento.')
            return redirect('venda_nova')

        if not itens_ids:
            messages.error(request, 'Selecione pelo menos um produto.')
            return redirect('venda_nova')

        pessoa = None
        if pessoa_id:
            try:
                pessoa = Pessoa.objects.filter(id=int(pessoa_id), ativo=True).first()
            except ValueError:
                pessoa = None

        # pedidos[produto_id] = quantidade (agrupa ids repetidos)
        pedidos = {}
        for pid in itens_ids:
            try:
                pid_int = int(pid)
                qtd = int(request.POST.get(f'qtd_{pid}', '0'))
            except (TypeError, ValueError):
                continue
            if qtd > 0:
                pedidos[pid_int] = pedidos.get(pid_int, 0) + qtd

        if not pedidos:
            messages.error(request, 'Informe a quantidade dos produtos selecionados.')
            return redirect('venda_nova')

        tipo_pagamento = 'HORA'
        vencimento = None
        status_venda = 'PAGO'

        if (pessoa and pessoa.pode_pagar_mensalmente
                and forma_pagamento in ['CREDITO', 'DEBITO']
                and request.POST.get('pagar_mensal') == 'sim'):
            vencimento_str = request.POST.get('vencimento')
            try:
                vencimento = datetime.strptime(vencimento_str, '%Y-%m-%d').date()
            except (TypeError, ValueError):
                messages.error(request, 'Informe um vencimento valido para pagamento mensal.')
                return redirect('venda_nova')
            tipo_pagamento = 'MENSAL'
            status_venda = 'ABERTA'

        try:
            with transaction.atomic():
                # trava os produtos para evitar estoque negativo em vendas simultaneas
                prods = {
                    p.id: p for p in
                    Produto.objects.select_for_update().filter(id__in=pedidos.keys(), ativo=True)
                }
                carrinho = []
                total = Decimal('0.00')
                for pid, qtd in pedidos.items():
                    prod = prods.get(pid)
                    if prod is None:
                        raise ValueError('Produto indisponivel.')
                    if prod.quantidade < qtd:
                        raise ValueError(f'Estoque insuficiente para {prod.nome} (restam {prod.quantidade}).')
                    subtotal = prod.preco * qtd
                    carrinho.append((prod, qtd, subtotal))
                    total += subtotal

                venda = Venda.objects.create(
                    pessoa=pessoa,
                    usuario=request.user,
                    forma_pagamento=forma_pagamento,
                    tipo_pagamento=tipo_pagamento,
                    total=total,
                    vencimento=vencimento,
                    status=status_venda,
                    observacoes=request.POST.get('observacoes') or None,
                )
                for prod, qtd, subtotal in carrinho:
                    ItemVenda.objects.create(
                        venda=venda,
                        produto=prod,
                        quantidade=qtd,
                        preco_unitario=prod.preco,
                        subtotal=subtotal,
                    )
                    prod.quantidade -= qtd
                    prod.save(update_fields=['quantidade'])
                if tipo_pagamento == 'MENSAL':
                    ContaMensal.objects.create(
                        pessoa=pessoa,
                        venda=venda,
                        valor=total,
                        vencimento=vencimento,
                        status='ABERTA',
                    )
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('venda_nova')

        messages.success(request, f'Venda #{venda.id} registrada com sucesso!')
        return redirect('venda_detalhe', pk=venda.id)

    return render(request, 'cantina/venda_nova.html', {
        'pessoas': pessoas,
        'produtos': produtos,
        'hoje': timezone.localdate(),
    })


@login_required(login_url='login')
@user_passes_test(eh_admin, login_url='login')
def vendas_lista(request):
    vendas = Venda.objects.select_related('pessoa', 'usuario').all()
    return render(request, 'cantina/vendas.html', {'vendas': vendas})


@login_required(login_url='login')
@user_passes_test(eh_admin, login_url='login')
def venda_detalhe(request, pk):
    venda = get_object_or_404(Venda.objects.select_related('pessoa', 'usuario'), pk=pk)
    itens = venda.itens.select_related('produto')
    return render(request, 'cantina/venda_detalhe.html', {'venda': venda, 'itens': itens})


@login_required(login_url='login')
@user_passes_test(eh_admin, login_url='login')
def contas_mensais(request):
    contas = ContaMensal.objects.select_related('pessoa', 'venda').all()
    return render(request, 'cantina/contas_mensais.html', {'contas': contas})


@login_required(login_url='login')
@user_passes_test(eh_admin, login_url='login')
def conta_pagar(request, pk):
    if request.method == 'POST':
        conta = get_object_or_404(ContaMensal, pk=pk)
        if conta.status == 'ABERTA':
            with transaction.atomic():
                conta.status = 'PAGA'
                conta.data_pagamento = timezone.now()
                conta.save()
                conta.venda.status = 'PAGO'
                conta.venda.save()
            messages.success(request, f'Conta #{conta.id} marcada como paga.')
    return redirect('contas_mensais')

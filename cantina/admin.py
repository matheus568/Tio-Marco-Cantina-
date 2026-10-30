from django.contrib import admin
from .models import Categoria, Pessoa, Produto, Venda, ItemVenda, ContaMensal

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativa')
    search_fields = ('nome',)

@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sobrenome', 'tipo', 'pode_pagar_mensalmente', 'ativo')
    list_filter = ('tipo', 'pode_pagar_mensalmente', 'ativo')
    search_fields = ('nome', 'sobrenome', 'matricula')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco', 'quantidade', 'ativo')
    list_filter = ('categoria', 'ativo')
    search_fields = ('nome',)

class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 0
    readonly_fields = ('produto', 'quantidade', 'preco_unitario', 'subtotal')

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pessoa', 'forma_pagamento', 'tipo_pagamento', 'total', 'status', 'data_venda')
    list_filter = ('forma_pagamento', 'tipo_pagamento', 'status')
    search_fields = ('id', 'pessoa__nome', 'pessoa__sobrenome')
    inlines = [ItemVendaInline]
    readonly_fields = ('usuario', 'total', 'data_venda')

    def has_add_permission(self, request):
        return False  # vendas sao criadas pela tela de Nova Venda

@admin.register(ContaMensal)
class ContaMensalAdmin(admin.ModelAdmin):
    list_display = ('id', 'pessoa', 'valor', 'vencimento', 'status', 'data_pagamento')
    list_filter = ('status',)
    search_fields = ('pessoa__nome', 'pessoa__sobrenome')

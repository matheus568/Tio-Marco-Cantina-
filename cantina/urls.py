from django.urls import path
from . import views

urlpatterns = [
    # Area publica (todos podem ver)
    path('', views.home, name='home'),
    path('login/', views.home, name='inicio'),

    # Area restrita (somente administrador com usuario e senha)
    path('login/admin/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('categorias/', views.categorias_lista, name='categorias'),

    path('pessoas/', views.pessoas_lista, name='pessoas'),
    path('pessoas/novo/', views.pessoa_novo, name='pessoa_novo'),
    path('pessoas/editar/<int:pk>/', views.pessoa_editar, name='pessoa_editar'),

    path('produtos/', views.produtos_lista, name='produtos'),
    path('produtos/novo/', views.produto_novo, name='produto_novo'),
    path('produtos/editar/<int:pk>/', views.produto_editar, name='produto_editar'),
    path('produtos/tela/', views.produtos_tela, name='produtos_tela'),

    path('vendas/nova/', views.venda_nova, name='venda_nova'),
    path('vendas/', views.vendas_lista, name='vendas'),
    path('vendas/detalhe/<int:pk>/', views.venda_detalhe, name='venda_detalhe'),

    path('contas-mensais/', views.contas_mensais, name='contas_mensais'),
    path('contas-mensais/pagar/<int:pk>/', views.conta_pagar, name='conta_pagar'),
]

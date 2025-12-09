from django.urls import path
from . import views # Importa o arquivo views.py do app

urlpatterns = [
    # Caminho 1: A página inicial ('') chama a view 'home_page'.
    path('', views.home_page, name='home'),
    path('bandeiras/', views.colecao_bandeiras, name='colecao_bandeiras'),
    # Caminho 2: A página de sugestão chama a view 'sugerir_leitura'.
    path('sugestao/<int:artigo_id>/', views.sugerir_leitura, name='sugestao'),
    path('bullets/<int:artigo_id>/', views.bullets, name='bullets'),
    path('artigo/<int:artigo_id>/audio/', views.artigo_audio, name='artigo_audio'),
    path('politica/', views.topico_politica, name='topico_politica'),
    path('pernambuco/', views.topico_pernambuco, name='topico_pernambuco'),
    path('esportes/', views.topico_esportes, name='topico_esportes'),
    path('cultura/', views.topico_cultura, name='topico_cultura'),
    path('ao-vivo/', views.ao_vivo, name='ao_vivo'),
    path('artigo/<int:artigo_id>/',views.exibir_artigo, name='exibir_artigo'),
    path('artigo/<int:id_artigo>/contexto/', views.conteudo_de_contexto, name='conteudo_de_contexto'),
    path('login/', views.login_view, name='login'),
    path('login_existente/', views.login_existente, name='login_existente'),
    path('meus-favoritos/', views.meus_favoritos, name='meus_favoritos'), 
    path('cadastro/', views.cadastro, name='cadastro'),
    path('logout/',views.logout_view,name='logout'),
    path('artigo/<int:artigo_id>/favoritar/', views.favoritar_artigo, name='favoritar_artigo'),
    path('enviar_sugestoes/', views.enviar_sugestoes_view, name='enviar_sugestoes'),
    path('newsletter_signup/', views.newsletter_signup, name='newsletter'),
    path('conteudos_com_Base_favoritos/', views.conteudos_com_Base_favoritos, name='conteudos_com_Base_favoritos'),
    path('categorias/', views.categorias, name='categorias'),
    path('notificacoes/', views.notificacoes, name='notificacoes'),
]

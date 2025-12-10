from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Artigos, Comentario, Progresso_diario, Progresso, Notificacao
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from gtts import gTTS  # tem que baixar essa biblioteca do google
import io  # manipulação de arquivos em memoria ram
from django.utils import timezone
from app1.utils.ai import gerar_contexto
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError, transaction
from .utils.progress import montar_progresso_bandeiras


def sugerir_leitura(request, artigo_id):
    artigo_atual_id = artigo_id
    artigo_atual = Artigos.objects.get(id=artigo_atual_id)
    categoria = artigo_atual.categoria
    sugestoes = (
        Artigos.objects.order_by("-data_publicacao")
        .filter(categoria=categoria)
        .exclude(id=artigo_atual_id)[:5]
    )
    context = {"artigo_atual": artigo_atual, "sugestoes": sugestoes}
    return render(request, "app1/sugestao.html", context)


def home_page(request):
    manchete_principal = Artigos.objects.order_by("-data_publicacao").first()
    mais_recentes = []
    if manchete_principal:
        mais_recentes = (
            Artigos.objects.order_by("-data_publicacao")
            .exclude(id=manchete_principal.id)[:6]
        )
    else:
        mais_recentes = Artigos.objects.order_by("-data_publicacao")[:6]

    artigos_opiniao = Artigos.objects.filter(categoria="Opinião").order_by(
        "-data_publicacao"
    )[:4]
    artigos_politica = Artigos.objects.filter(categoria="Política").order_by(
        "-data_publicacao"
    )[:4]

    # Carrossel "De seu interesse"
    artigos_interesse = []
    if request.user.is_authenticated:
        # Pega favoritos do usuário
        favoritos = request.user.artigos_favoritos.all()

        # Pega artigos lidos pelo usuário
        artigos_lidos_ids = Progresso.objects.filter(
            user=request.user, completado=True
        ).values_list("artigo_id", flat=True)

        # Conta categorias dos favoritos e lidos
        categorias_count = {}
        for artigo in favoritos:
            categorias_count[artigo.categoria] = categorias_count.get(
                artigo.categoria, 0
            ) + 1

        artigos_lidos = Artigos.objects.filter(id__in=artigos_lidos_ids)
        for artigo in artigos_lidos:
            categorias_count[artigo.categoria] = categorias_count.get(
                artigo.categoria, 0
            ) + 1

        # Se tem categorias preferidas, busca artigos dessas categorias
        if categorias_count:
            # Ordena categorias por quantidade (mais lida/favoritada primeiro)
            categorias_ordenadas = sorted(
                categorias_count.items(), key=lambda x: x[1], reverse=True
            )
            categoria_favorita = categorias_ordenadas[0][0]

            # Busca 4 artigos da categoria favorita (excluindo os já favoritados/lidos)
            ids_excluir = list(favoritos.values_list("id", flat=True)) + list(
                artigos_lidos_ids
            )
            artigos_interesse = (
                Artigos.objects.filter(categoria=categoria_favorita)
                .exclude(id__in=ids_excluir)
                .order_by("-data_publicacao")[:4]
            )

    # Se não tem artigos de interesse (usuário não logado ou sem histórico),
    # mostra artigos recentes variados
    if not artigos_interesse:
        artigos_interesse = Artigos.objects.order_by("-data_publicacao")[:4]

    context = {
        "manchete_principal": manchete_principal,
        "mais_recentes": mais_recentes,
        "artigos_opiniao": artigos_opiniao,
        "artigos_politica": artigos_politica,
        "artigos_interesse": artigos_interesse,
    }
    return render(request, "app1/home.html", context)


def colecao_bandeiras(request):
    progresso_flags = montar_progresso_bandeiras(request)
    return render(request, "app1/colecao_bandeiras.html", progresso_flags)


def bullets(request, artigo_id):
    bullets = Artigos.objects.get(id=artigo_id).bullets.all()
    context = {"bullets": bullets}
    return render(request, "app1/bullets.html", context)


def artigo_audio(request, artigo_id):
    artigo = get_object_or_404(Artigos, id=artigo_id)
    texto = artigo.conteudo
    tts = gTTS(text=texto, lang="pt", slow=False)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return FileResponse(buffer, content_type="audio/mpeg")
    # não salva o audio no banco de dados, gera na hora e manda pro usuario,
    # salvando no buffer, que é um arquivo em memoria ram (memoria volátil).
    # quando o usuario fecha a pagina, o audio some, n fica salvo no servidor


def topico_politica(request):
    artigos_politica = Artigos.objects.filter(categoria="Política").order_by(
        "-data_publicacao"
    )
    context = {"artigos_politica": artigos_politica}
    return render(request, "app1/topico_politica.html", context)


def topico_pernambuco(request):
    artigos_pernambuco = Artigos.objects.filter(categoria="Pernambuco").order_by(
        "-data_publicacao"
    )
    context = {"artigos_pernambuco": artigos_pernambuco}
    return render(request, "app1/topico_pernambuco.html", context)


def topico_esportes(request):
    artigos_esportes = Artigos.objects.filter(categoria="Esportes").order_by(
        "-data_publicacao"
    )
    context = {"artigos_esportes": artigos_esportes}
    return render(request, "app1/topico_esportes.html", context)


def topico_cultura(request):
    artigos_cultura = Artigos.objects.filter(categoria="Cultura").order_by(
        "-data_publicacao"
    )
    context = {"artigos_cultura": artigos_cultura}
    return render(request, "app1/topico_cultura.html", context)






def categorias(request):
    categorias_qs = (
        Artigos.objects.order_by("categoria")
        .values_list("categoria", flat=True)
        .distinct()
    )
    blocos = []
    for cat in categorias_qs:
        artigos = list(
            Artigos.objects.filter(categoria=cat).order_by("-data_publicacao")[:4]
        )
        blocos.append({"nome": cat, "artigos": artigos})

    context = {"categorias": blocos}
    return render(request, "app1/categorias.html", context)


def notificacoes(request):
    notificacoes_qs = Notificacao.objects.order_by("-created_at")
    hoje = timezone.now().date()
    novas = notificacoes_qs.filter(created_at__date=hoje)
    antigas = notificacoes_qs.exclude(created_at__date=hoje)

    context = {
        "novas": novas,
        "antigas": antigas,
        "total": notificacoes_qs.count(),
        "novas_count": novas.count(),
    }
    return render(request, "app1/notificacoes.html", context)


def exibir_artigo(request, artigo_id):
    flag = False
    artigo = get_object_or_404(Artigos, id=artigo_id)
    hoje = timezone.now().date()

    if request.user.is_authenticated:
        visitante = f"user_{request.user.id}"
    else:
        visitante = f"ip_{request.META.get('REMOTE_ADDR', 'anonimo')}"

    diario = None
    for _ in range(3):
        try:
            with transaction.atomic():
                diario, _ = Progresso_diario.objects.get_or_create(
                    data=hoje,
                    visitante=visitante,
                    defaults={"artigos_lidos": 0},
                )
            break
        except IntegrityError:
            diario = Progresso_diario.objects.filter(
                data=hoje, visitante=visitante
            ).first()
            if diario:
                break

    if diario is None:
        # Último recurso: evita quebrar a página caso o índice único esteja inconsistente.
        diario = Progresso_diario.objects.filter(data=hoje).first()
        if diario is None:
            diario = Progresso_diario.objects.create(
                data=hoje,
                visitante=visitante,
                artigos_lidos=0,
            )

    if "artigos_lidos" not in request.session:
        request.session["artigos_lidos"] = []

    if artigo_id not in request.session["artigos_lidos"]:
        diario.artigos_lidos += 1
        diario.save()
        request.session["artigos_lidos"].append(artigo_id)
        request.session.modified = True

    mensagem = ""

    if request.user.is_authenticated:
        progresso, created = Progresso.objects.get_or_create(
            user=request.user,
            artigo=artigo,
        )
        if not progresso.completado:
            progresso.completado = True
            progresso.save()

    quantidade_de_artigos_lidos = diario.artigos_lidos
    if quantidade_de_artigos_lidos == 3:
        flag = True

    artigos_lidos_na_sessao = len(request.session["artigos_lidos"])
    if artigos_lidos_na_sessao >= 1:
        mensagem = f"Você leu {artigos_lidos_na_sessao} artigos nesta sessão."

    # ComentÇ¸rios
    if request.method == "POST":
        nome_form = request.POST.get("nome", "").strip()
        texto_form = request.POST.get("comentario", "").strip()
        avatar_form = request.POST.get("avatar", "").strip()

        nome_final = nome_form or (
            request.user.get_full_name()
            if request.user.is_authenticated and request.user.get_full_name()
            else (request.user.username if request.user.is_authenticated else "Leitor")
        )

        if texto_form:
            Comentario.objects.create(
                artigo=artigo,
                nome=nome_final,
                texto=texto_form,
                avatar=avatar_form,
            )
            messages.success(request, "Comentário publicado!")
            return redirect("exibir_artigo", artigo_id=artigo.id)
        else:
            messages.error(request, "Digite um comentário antes de enviar.")

    relacionados = (
        Artigos.objects.filter(categoria=artigo.categoria)
        .exclude(id=artigo.id)
        .order_by("-data_publicacao")[:3]
    )

    context = {
        "artigo": artigo,
        "mensagem": mensagem,
        "flag": flag,
        "relacionados": relacionados,
        "comentarios": artigo.comentarios.all(),
    }
    return render(request, "app1/exibir_artigo.html", context)
def conteudo_de_contexto(request, id_artigo):
    artigo = Artigos.objects.get(id=id_artigo)
    contexto_gerado = gerar_contexto(artigo.conteudo)
    context = {"artigo": artigo, "contexto_gerado": contexto_gerado}
    return render(request, "app1/conteudo_de_contexto.html", context)


def cadastro(request):
    errors = []
    username = ""
    password1 = ""
    password2 = ""
    email = ""

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "").strip()
        password2 = request.POST.get("password2", "").strip()

        if not username:
            errors.append("O nome de usuário é obrigatório.")
        if not password1 or not password2:
            errors.append("A senha e a confirmação são obrigatórias.")
        elif password1 != password2:
            errors.append("As senhas não coincidem.")
        elif User.objects.filter(username=username).exists():
            errors.append("Esse nome de usuário já está em uso.")

        if not errors:
            user = User.objects.create_user(username=username, password=password1)
            authenticated_user = authenticate(username=username, password=password1)

            if authenticated_user:
                login(request, authenticated_user)
                return redirect("home")

    context = {"errors": errors, "username": username}
    return render(request, "app1/cadastro.html", context)


def login_view(request):
    return render(request, "app1/login.html", {})


def ao_vivo(request):
    live_items = [
        {
            "titulo": "Radio Jornal - FM 90.3",
            "origem": "Radio Jornal (interior)",
            "embed_url": "https://www.youtube.com/embed/live_stream?channel=UC8u0NiyHh6ZzqbmS_MyF6mA",
        },
        {
            "titulo": "Radio Jornal (Recife)",
            "origem": "Radio Jornal (Recife)",
            "embed_url": "https://www.youtube.com/embed/live_stream?channel=UCV1b-38tvz3rVln1zC_gJiw",
        },
        {
            "titulo": "TV Jornal (Recife)",
            "origem": "TV Jornal (Recife)",
            "embed_url": "https://www.youtube.com/embed/live_stream?channel=UCo4KAd86PX3cKWf0E0V2GxQ",
        },
        {
            "titulo": "TV Jornal (interior)",
            "origem": "TV Jornal (interior)",
            "embed_url": "https://www.youtube.com/embed/live_stream?channel=UCYKPNC7kwh28ykVfoCkbHgQ",
        },
    ]

    hero = live_items[0] if live_items else None
    playlist = live_items[1:] if hero else live_items

    context = {
        "hero": hero,
        "live_items": playlist,
    }
    return render(request, "app1/ao_vivo.html", context)


def login_existente(request):
    errors = None

    if request.method != "POST":
        usuario = ""
        email = ""
        senha = ""
    else:
        usuario = request.POST.get("login")
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        if usuario and senha:
            user = authenticate(username=usuario, password=senha, email=email)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("home"))
            else:
                errors = "Usuário ou senha inválidos."
        else:
            errors = "Preencha todos os campos."

    context = {
        "usuario": usuario,
        "senha": senha,
        "errors": errors,
    }
    return render(request, "app1/login_existente.html", context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))


# --------------
# Favoritar artigos
# --------------


@login_required
def favoritar_artigo(request, artigo_id):
    artigo = get_object_or_404(Artigos, id=artigo_id)
    # Verifica se o usu?rio j? favoritou este artigo
    if artigo.favoritos.filter(id=request.user.id).exists():
        artigo.favoritos.remove(request.user)
        messages.info(request, "Not?cia removida dos salvos.")
    else:
        artigo.favoritos.add(request.user)
        messages.success(request, "Not?cia salva em 'Salvos'.")
    return redirect("exibir_artigo", artigo_id=artigo.id)


@login_required
def meus_favoritos(request):
    lista_favoritos = request.user.artigos_favoritos.all().order_by("-data_publicacao")
    context = {
        "lista_favoritos": lista_favoritos,
    }
    return render(request, "app1/meus_favoritos.html", context)


@login_required
def conteudos_com_Base_favoritos(request):
    favoritos = request.user.artigos_favoritos.all()
    if not favoritos.exists():
        return None

    categorias = ["Esportes", "Política", "Cultura", "Pernambuco"]
    contagens = [favoritos.filter(categoria=c).count() for c in categorias]
    indice_maior = contagens.index(max(contagens))
    categoria_sugerida = categorias[indice_maior]

    sugestoes = (
        Artigos.objects.filter(categoria=categoria_sugerida)
        .order_by("-data_publicacao")[:5]
    )

    context = {"sugestoes": sugestoes, "categoria": categoria_sugerida}
    return render(request, "app1/conteudos_com_Base_favoritos.html", context)


# Função para obter artigos novos sugeridos com base nos favoritos do usuário + gmail
def enviar_email_sugestoes_html(user, artigos):
    if not artigos:
        return False

    categoria = artigos[0].categoria

    html_content = render_to_string(
        "emails/sugestoes.html",
        {
            "user": user,
            "categoria": categoria,
            "artigos": artigos[:5],  # envia até 5 artigos
            "artigo_url_base": "https://seusite.com/artigo/",  # ajuste para seu domínio
        },
    )

    text_content = (
        f"Olá {user.first_name or user.username}! "
        f"Você tem novas notícias na categoria {categoria}."
    )

    email = EmailMultiAlternatives(
        subject=f"Novas notícias em {categoria} para você!",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()
    return True


def artigos_novos_sugeridos(user):
    favoritos = user.artigos_favoritos.all()
    if not favoritos.exists():
        return []

    categorias = ["Esportes", "Política", "Cultura", "Pernambuco"]
    contagens = [favoritos.filter(categoria=c).count() for c in categorias]
    categoria_favorita = categorias[contagens.index(max(contagens))]

    artigos = Artigos.objects.filter(categoria=categoria_favorita).order_by(
        "-data_publicacao"
    )[:10]

    return [artigo for artigo in artigos if artigo not in favoritos]


@login_required
def enviar_sugestoes_view(request):
    artigos = artigos_novos_sugeridos(request.user)
    enviado = enviar_email_sugestoes_html(request.user, artigos)

    if enviado:
        messages.success(request, "E-mail enviado com suas sugestões personalizadas!")
    else:
        messages.info(request, "Não há novidades para enviar no momento.")

    return redirect("home")


@login_required
def newsletter_signup(request):
    return render(request, "app1/newsletter_signup.html", {})

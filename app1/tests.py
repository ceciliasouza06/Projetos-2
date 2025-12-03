import os
import shutil
import tempfile
import time

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from django.core import mail
from django.template.context import BaseContext
from app1 import views as app_views
from app1.models import Artigos, Bullets
from django.test import signals as test_signals
from unittest.mock import patch
from django.test import RequestFactory

# --- Ajustes para ignorar WhiteNoise nos testes ---
middleware = list(getattr(settings, "MIDDLEWARE", []))
settings.MIDDLEWARE = [
    m for m in middleware if "whitenoise.middleware.WhiteNoiseMiddleware" not in m
]

if getattr(settings, "STATICFILES_STORAGE", "") == (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
):
    settings.STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Corrige __copy__ quebrado do BaseContext em Python 3.14 (Django 4.2 nao suporta oficialmente).
def _safe_basecontext_copy(self):
    dup = object.__new__(self.__class__)
    dup.dicts = list(getattr(self, "dicts", []))
    return dup


BaseContext.__copy__ = _safe_basecontext_copy

# Django 4.2 em Python 3.14 estoura copy(Context). Removemos o listener que clona
# contextos ao renderizar templates em testes.
test_signals.template_rendered.disconnect(
    dispatch_uid="django.test.client.store_rendered_templates"
)

# --- Evita chamadas externas do gTTS nos testes ---
class _DummyTTS:
    def __init__(self, *args, **kwargs):
        pass

    def write_to_fp(self, fp):
        fp.write(b"fake-audio")


app_views.gTTS = _DummyTTS


def criar_artigo(titulo: str, categoria: str = "Esportes") -> Artigos:
    return Artigos.objects.create(
        titulo=titulo,
        categoria=categoria,
        resumo=f"Resumo de {titulo}",
        conteudo=f"Conteudo completo de {titulo}",
        imagem="",
        data_publicacao=timezone.now(),
    )


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class SmokeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.artigo = criar_artigo("Artigo para smoke", "Politica")

    def test_home_responde(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jornal do Commercio")

    def test_topicos_respondem(self):
        for url_name in [
            "topico_politica",
            "topico_pernambuco",
            "topico_esportes",
            "topico_cultura",
        ]:
            response = self.client.get(reverse(url_name))
            self.assertEqual(
                response.status_code,
                200,
                msg=f"Falhou em {url_name}",
            )

    def test_sugestao_view_responde(self):
        url = reverse("sugestao", args=[self.artigo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_bullets_view_responde_sem_registros(self):
        url = reverse("bullets", args=[self.artigo.id])
        response = self.client.get(url)
        self.assertContains(response, "Nenhum Ponto Chave Encontrado")

    def test_bullets_view_responde_com_registros(self):
        Bullets.objects.create(artigo=self.artigo, bullets="Primeiro ponto")
        response = self.client.get(reverse("bullets", args=[self.artigo.id]))
        self.assertContains(response, "Primeiro ponto")

    def test_cadastro_cria_usuario(self):
        payload = {
            "username": "novo_user",
            "email": "novo@example.com",
            "password1": "Senha123!",
            "password2": "Senha123!",
        }
        response = self.client.post(reverse("cadastro"), payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="novo_user").exists())
        self.assertContains(response, "novo_user")


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class ReadingProgressTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.articles = [
            criar_artigo("Primeira materia", "Cultura"),
            criar_artigo("Segunda materia", "Cultura"),
            criar_artigo("Terceira materia", "Cultura"),
        ]

    def test_banner_newsletter_apos_tres_leituras(self):
        for artigo in self.articles[:-1]:
            self.client.get(reverse("exibir_artigo", args=[artigo.id]))

        response = self.client.get(reverse("exibir_artigo", args=[self.articles[-1].id]))
        self.assertContains(response, "Assine nossa newsletter")
        self.assertIn("leu 3 artigos", response.content.decode())


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class ViewBehaviorTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="Senha123!",
        )
        self.artigo = criar_artigo("Artigo de teste", "Cultura")

    def test_login_page_get(self):
        r = self.client.get(reverse("login"))
        self.assertEqual(r.status_code, 200)

    def test_login_existente_invalido(self):
        r = self.client.post(
            reverse("login_existente"),
            {"login": "tester", "email": self.user.email, "senha": "errada"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("error-messages", r.content.decode().lower())

    def test_login_existente_valido(self):
        r = self.client.post(
            reverse("login_existente"),
            {"login": "tester", "email": self.user.email, "senha": "Senha123!"},
            follow=True,
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("tester", r.content.decode())

    def test_cadastro_campos_obrigatorios(self):
        r = self.client.post(reverse("cadastro"), {})
        self.assertEqual(r.status_code, 200)
        self.assertIn("obrigat", r.content.decode().lower())

    def test_cadastro_username_duplicado(self):
        User.objects.create_user(username="tester2", password="Senha123!")
        r = self.client.post(
            reverse("cadastro"),
            {
                "username": "tester2",
                "email": "dup@example.com",
                "password1": "Senha123!",
                "password2": "Senha123!",
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("uso", r.content.decode().lower())

    def test_cadastro_invalido_senhas_diferentes(self):
        r = self.client.post(
            reverse("cadastro"),
            {
                "username": "novo",
                "email": "novo@example.com",
                "password1": "Senha123!",
                "password2": "OutraSenha!",
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("senhas", r.content.decode().lower())

    def test_logout_limpa_sessao(self):
        self.client.login(username="tester", password="Senha123!")
        r = self.client.get(reverse("logout"))
        self.assertEqual(r.status_code, 302)
        home = self.client.get(reverse("home"))
        self.assertNotIn("tester", home.content.decode())

    def test_favoritar_toggle(self):
        self.client.login(username="tester", password="Senha123!")
        fav_url = reverse("favoritar_artigo", args=[self.artigo.id])
        # adiciona
        self.client.post(fav_url, follow=True)
        self.artigo.refresh_from_db()
        self.assertTrue(self.artigo.favoritos.filter(id=self.user.id).exists())
        # remove
        self.client.post(fav_url, follow=True)
        self.artigo.refresh_from_db()
        self.assertFalse(self.artigo.favoritos.filter(id=self.user.id).exists())

    def test_favoritar_sem_login_redireciona_login(self):
        fav_url = reverse("favoritar_artigo", args=[self.artigo.id])
        r = self.client.post(fav_url)
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("login"), r["Location"])

    def test_meus_favoritos_vazio(self):
        self.client.login(username="tester", password="Senha123!")
        r = self.client.get(reverse("meus_favoritos"))
        self.assertEqual(r.status_code, 200)

    def test_artigo_audio(self):
        r = self.client.get(reverse("artigo_audio", args=[self.artigo.id]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "audio/mpeg")

    def test_conteudo_de_contexto_fallback(self):
        r = self.client.get(
            reverse("conteudo_de_contexto", args=[self.artigo.id])
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("Entenda o Contexto", r.content.decode())

    def test_newsletter_signup(self):
        # sem login redireciona
        r = self.client.get(reverse("newsletter"))
        self.assertEqual(r.status_code, 302)
        # com login
        self.client.login(username="tester", password="Senha123!")
        r2 = self.client.get(reverse("newsletter"))
        self.assertEqual(r2.status_code, 200)

    def test_conteudos_com_base_favoritos(self):
        self.client.login(username="tester", password="Senha123!")
        artigo_cat = criar_artigo("Outro artigo", "Esportes")
        artigo_outro = criar_artigo("Sugestao esporte", "Esportes")
        artigo_cat.favoritos.add(self.user)
        r = self.client.get(reverse("conteudos_com_Base_favoritos"))
        self.assertEqual(r.status_code, 200)
        self.assertIn("Sugestao", r.content.decode())

    def test_enviar_sugestoes_envia_email(self):
        self.client.login(username="tester", password="Senha123!")
        artigo_fav = criar_artigo("Fav esporte", "Esportes")
        artigo_fav.favoritos.add(self.user)
        criar_artigo("Sugestao1", "Esportes")
        with patch("app1.views.render_to_string", return_value="ok-template"):
            r = self.client.get(reverse("enviar_sugestoes"), follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(mail.outbox), 1)

    def test_enviar_email_sugestoes_sem_artigos(self):
        res = app_views.enviar_email_sugestoes_html(self.user, [])
        self.assertFalse(res)

    def test_conteudos_com_base_favoritos_sem_favoritos(self):
        self.client.login(username="tester", password="Senha123!")
        factory = RequestFactory()
        request = factory.get("/conteudos_com_Base_favoritos/")
        request.user = self.user
        response = app_views.conteudos_com_Base_favoritos(request)
        self.assertIsNone(response)

    def test_exibir_artigo_contador_nao_duplica(self):
        # primeira leitura incrementa
        r1 = self.client.get(reverse("exibir_artigo", args=[self.artigo.id]))
        self.assertEqual(r1.status_code, 200)
        # segunda leitura do mesmo artigo nao deve duplicar
        r2 = self.client.get(reverse("exibir_artigo", args=[self.artigo.id]))
        self.assertEqual(r2.status_code, 200)
        diario = app_views.Progresso_diario.objects.first()
        self.assertIsNotNone(diario)
        self.assertEqual(diario.artigos_lidos, 1)

    def test_exibir_artigo_flag_apenas_com_tres(self):
        art2 = criar_artigo("Segundo", "Cultura")
        art3 = criar_artigo("Terceiro", "Cultura")
        self.client.get(reverse("exibir_artigo", args=[self.artigo.id]))
        resp2 = self.client.get(reverse("exibir_artigo", args=[art2.id]))
        self.assertNotIn("leu 3 artigos", resp2.content.decode())
        resp3 = self.client.get(reverse("exibir_artigo", args=[art3.id]))
        self.assertIn("leu 3 artigos", resp3.content.decode())
@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class PortalE2EFlows(StaticLiveServerTestCase):
    """
    Fluxos completos inspirados no E2E do RachAi:
    - Cadastro + login
    - Favoritar materia e conferir nos salvos
    - Login existente + leitura de 3 materias mostra CTA da newsletter
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._tmp_profile = tempfile.mkdtemp(prefix="chrome-prof-")

        opts = Options()
        in_ci = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"
        if in_ci:
            opts.add_argument("--headless=new")
        else:
            opts.add_experimental_option("detach", True)

        opts.add_argument(f"--user-data-dir={cls._tmp_profile}")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1600,900")
        opts.add_argument("--disable-dev-tools")
        opts.add_argument("--disable-extensions")

        try:
            cls.selenium = webdriver.Chrome(options=opts)
            cls.selenium.implicitly_wait(10)
        except Exception:
            shutil.rmtree(cls._tmp_profile, ignore_errors=True)
            raise

    @classmethod
    def tearDownClass(cls):
        try:
            cls.selenium.quit()
        finally:
            if cls.__dict__.get("_tmp_profile"):
                shutil.rmtree(cls._tmp_profile, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.client = Client()
        self.artigo_principal = criar_artigo("Materia principal", "Esportes")
        self.artigo_extra_1 = criar_artigo("Materia secundaria", "Cultura")
        self.artigo_extra_2 = criar_artigo("Materia terciaria", "Pernambuco")

        self.user = User.objects.create_user(
            username="leitor",
            email="leitor@example.com",
            password="SenhaSegura123",
        )

    def _login_existing_user(self, wait, delay=0.5):
        print("[LOGIN EXISTENTE] Abrindo pagina de login existente...")
        login_url = self.live_server_url + reverse("login_existente")
        self.selenium.get(login_url)

        wait.until(EC.presence_of_element_located((By.NAME, "login"))).send_keys(
            self.user.username
        )
        self.selenium.find_element(By.NAME, "email").send_keys(self.user.email)
        self.selenium.find_element(By.NAME, "senha").send_keys("SenhaSegura123")
        login_btn = self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.selenium.execute_script("arguments[0].scrollIntoView(true);", login_btn)
        self.selenium.execute_script("arguments[0].click();", login_btn)

        wait.until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{self.user.username}')]"))
        )
        print("-> Login realizado com sucesso.")
        time.sleep(delay)

    def test_fluxo_cadastro_favoritar_e_meus_favoritos(self):
        print("\n" + "=" * 50)
        print("INICIANDO FLUXO: Cadastro > Favoritar > Meus Favoritos")
        print("=" * 50)

        wait = WebDriverWait(self.selenium, 10)
        delay = 1

        print("[ETAPA 1/4] - Cadastro de novo usuario...")
        signup_url = self.live_server_url + reverse("cadastro")
        self.selenium.get(signup_url)

        username = "novo_leitor"
        password = "SenhaMuitoForte123"
        email = "novo.leitor@example.com"

        wait.until(EC.visibility_of_element_located((By.ID, "id_username"))).send_keys(
            username
        )
        self.selenium.find_element(By.ID, "id_email").send_keys(email)
        self.selenium.find_element(By.ID, "id_password1").send_keys(password)
        self.selenium.find_element(By.ID, "id_password2").send_keys(password)
        submit_btn = self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.selenium.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.selenium.execute_script("arguments[0].click();", submit_btn)

        wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{username}')]")))
        print("-> Cadastro e login automatico realizados.")
        time.sleep(delay)

        print("[ETAPA 2/4] - Abrindo materia e salvando nos favoritos...")
        artigo_url = self.live_server_url + reverse(
            "exibir_artigo", args=[self.artigo_principal.id]
        )
        self.selenium.get(artigo_url)
        wait.until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{self.artigo_principal.titulo}')]"))
        )

        fav_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "form.fav-form button"))
        )
        fav_button.click()
        time.sleep(delay)

        page_source = self.selenium.page_source
        self.assertIn("salva", page_source.lower())
        artigo_db = Artigos.objects.get(id=self.artigo_principal.id)
        self.assertTrue(artigo_db.favoritos.filter(username=username).exists())
        print("-> Materia favoritada com sucesso.")

        print("[ETAPA 3/4] - Navegando ate Meus Favoritos...")
        favoritos_url = self.live_server_url + reverse("meus_favoritos")
        self.selenium.get(favoritos_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2")))

        favoritos_page = self.selenium.page_source
        self.assertIn(self.artigo_principal.titulo, favoritos_page)
        print("-> Materia aparece na lista de favoritos.")
        time.sleep(delay)

        print("\n--> Fluxo de cadastro e favoritos concluido com sucesso!")

    def test_fluxo_login_existente_e_banner_de_leitura(self):
        print("\n" + "=" * 50)
        print("INICIANDO FLUXO: Login existente + leitura de 3 materias")
        print("=" * 50)

        wait = WebDriverWait(self.selenium, 10)
        delay = 1

        self._login_existing_user(wait, delay)

        print("[ETAPA 2/3] - Lendo tres materias para acionar CTA de newsletter...")
        artigos_para_ler = [
            self.artigo_principal,
            self.artigo_extra_1,
            self.artigo_extra_2,
        ]

        for idx, artigo in enumerate(artigos_para_ler, start=1):
            url = self.live_server_url + reverse("exibir_artigo", args=[artigo.id])
            self.selenium.get(url)
            wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//*[contains(text(), '{artigo.titulo}')]")
                )
            )
            print(f"-> Materia {idx}/3 carregada: {artigo.titulo}")
            time.sleep(delay)

        print("[ETAPA 3/3] - Verificando banner de engajamento...")
        page_source = self.selenium.page_source
        self.assertIn("Assine nossa newsletter", page_source)
        self.assertIn("leu 3 artigos", page_source)
        print("-> Banner da newsletter e mensagem de leitura exibidos.")
        print("\n--> Fluxo de leitura concluido com sucesso!")

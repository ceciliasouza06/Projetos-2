from django.test import TestCase, Client, LiveServerTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from app1.models import Artigos, Bullets
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


class TesteBase(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        cls.selenium = webdriver.Chrome(options=chrome_options)
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.client = Client()
        self.home_url = reverse("home")

    def test_template_renderiza(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jornal do Commercio")

    def test_links_menu_existem(self):
        response = self.client.get(self.home_url)
        urls = [
            reverse("topico_pernambuco"),
            reverse("topico_politica"),
            reverse("topico_esportes"),
            reverse("topico_cultura"),
            reverse("newsletter"),
        ]
        for url in urls:
            self.assertContains(response, f'href="{url}"')

    def test_usuario_nao_logado_ve_botao_login(self):
        response = self.client.get(self.home_url)
        self.assertContains(response, reverse("login"))
        self.assertNotContains(response, reverse("meus_favoritos"))

    def test_usuario_logado_ve_favoritos_e_logout(self):
        user = User.objects.create_user(username="teste", password="123")
        self.client.login(username="teste", password="123")
        response = self.client.get(self.home_url)
        self.assertContains(response, "Olá, teste!")
        self.assertContains(response, reverse("logout"))
        self.assertContains(response, reverse("meus_favoritos"))

    def test_menu_hamburguer_abre_e_fecha(self):
        self.selenium.get(self.live_server_url + self.home_url)
        hamburger = self.selenium.find_element(By.ID, "menu-toggle")
        nav = self.selenium.find_element(By.ID, "main-nav")
        self.assertNotIn("is-open", nav.get_attribute("class"))
        hamburger.click()
        time.sleep(0.3)
        self.assertIn("is-open", nav.get_attribute("class"))
        hamburger.click()
        time.sleep(0.3)
        self.assertNotIn("is-open", nav.get_attribute("class"))


class TesteTopicos(TestCase):
    def setUp(self):
        self.client = Client()

    def test_politica(self):
        r = self.client.get(reverse("topico_politica"))
        self.assertEqual(r.status_code, 200)

    def test_pernambuco(self):
        r = self.client.get(reverse("topico_pernambuco"))
        self.assertEqual(r.status_code, 200)

    def test_esportes(self):
        r = self.client.get(reverse("topico_esportes"))
        self.assertEqual(r.status_code, 200)

    def test_cultura(self):
        r = self.client.get(reverse("topico_cultura"))
        self.assertEqual(r.status_code, 200)


class TesteSugestao(TestCase):
    def setUp(self):
        self.client = Client()
        self.artigo = Artigos.objects.create(
            titulo="Teste Artigo",
            conteudo="Conteúdo do artigo",
            categoria="Esportes",
        )

    def test_sugestao_view(self):
        url = reverse("sugestao", args=[self.artigo.id])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)


class TesteBullets(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        cls.selenium = webdriver.Chrome(options=chrome_options)
        cls.selenium.implicitly_wait(4)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.client = Client()
        self.artigo = Artigos.objects.create(titulo="Artigo Teste", categoria="Teste", conteudo="...")
        self.url = reverse("bullets", args=[self.artigo.id])

    def test_renderiza_sem_bullets(self):
        r = self.client.get(self.url)
        self.assertContains(r, "Nenhum Ponto Chave Encontrado")

    def test_renderiza_com_bullets(self):
        Bullets.objects.create(artigo=self.artigo, bullets="Primeiro ponto")
        Bullets.objects.create(artigo=self.artigo, bullets="Segundo ponto")
        r = self.client.get(self.url)
        self.assertContains(r, "Primeiro ponto")
        self.assertContains(r, "Segundo ponto")

    def test_selenium_renderiza_bullets(self):
        Bullets.objects.create(artigo=self.artigo, bullets="Bullet Selenium")
        self.selenium.get(self.live_server_url + self.url)
        body = self.selenium.find_element(By.TAG_NAME, "body").text
        self.assertIn("Bullet Selenium", body)


class TestCadastro(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("cadastro")

    def test_django_get(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)

    def test_django_post_invalido(self):
        r = self.client.post(self.url, {})
        self.assertEqual(r.status_code, 200)

    def test_django_post_valido(self):
        r = self.client.post(self.url, {
            "username": "user1",
            "email": "u1@example.com",
            "password1": "Senha123!",
            "password2": "Senha123!"
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse("home"))


class TesteContexto(TestCase):
    def setUp(self):
        self.client = Client()
        self.artigo = Artigos.objects.create(
            titulo="Titulo Teste",
            conteudo="Conteudo Teste",
            categoria="Teste"
        )

    def test_exibir_artigo(self):
        r = self.client.get(reverse("exibir_artigo", args=[self.artigo.id]))
        self.assertContains(r, "Titulo Teste")

    def test_contexto(self):
        r = self.client.get(reverse("conteudo_de_contexto", args=[self.artigo.id]))
        self.assertEqual(r.status_code, 200)


class TestNewsletter(TestCase):
    def setUp(self):
        self.client = Client()
        Artigos.objects.create(
            titulo="Artigo Teste",
            conteudo="Resumo Teste",
            categoria="Tecnologia"
        )

    def test_django_render(self):
        r = self.client.get(reverse("newsletter"), {"categoria": "Tecnologia"})
        self.assertContains(r, "Artigo Teste")

    def test_newsletter_post(self):
        r = self.client.post(reverse("newsletter"), {"email": "a@b.com"})
        self.assertEqual(r.status_code, 200)


class TesteArtigo(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="u", password="123")
        self.artigo = Artigos.objects.create(
            titulo="Artigo Teste",
            conteudo="Conteudo Teste",
            categoria="Geral"
        )
        self.url = reverse("exibir_artigo", args=[self.artigo.id])

    def test_django_render(self):
        r = self.client.get(self.url)
        self.assertContains(r, "Artigo Teste")


class TesteHome(TestCase):
    def setUp(self):
        self.client = Client()
        Artigos.objects.create(titulo="Artigo Interesse 1", conteudo="Resumo 1", categoria="Tech")
        Artigos.objects.create(titulo="Artigo Recente 1", conteudo="Resumo 2", categoria="News")

    def test_django_render(self):
        r = self.client.get(reverse("home"))
        self.assertContains(r, "Mais Recentes")


class TesteLogin(TestCase):
    def setUp(self):
        self.client = Client()

    def test_login_page_template_django(self):
        r = self.client.get(reverse("login"))
        self.assertContains(r, "Entrar")


class TesteLoginExistente(TestCase):
    def test_login_existente(self):
        r = Client().get(reverse("login_existente"))
        self.assertEqual(r.status_code, 200)


class TesteFavoritos(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="z", password="123")
        self.artigo = Artigos.objects.create(
            titulo="A",
            conteudo="B",
            categoria="C"
        )

    def test_meus_favoritos_sem_login(self):
        r = self.client.get(reverse("meus_favoritos"))
        self.assertEqual(r.status_code, 302)

    def test_meus_favoritos_logado(self):
        self.client.login(username="z", password="123")
        r = self.client.get(reverse("meus_favoritos"))
        self.assertEqual(r.status_code, 200)

    def test_favoritar_artigo(self):
        self.client.login(username="z", password="123")
        url = reverse("favoritar_artigo", args=[self.artigo.id])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 302)


class TestConteudosComBaseFavoritos(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="zz", password="123")

    def test_render(self):
        self.client.login(username="zz", password="123")
        r = self.client.get(reverse("conteudos_com_Base_favoritos"))
        self.assertEqual(r.status_code, 200)


class TestLogout(TestCase):
    def test_logout(self):
        client = Client()
        r = client.get(reverse("logout"))
        self.assertEqual(r.status_code, 302)

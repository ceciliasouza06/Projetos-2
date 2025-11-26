from django.test import TestCase, Client, LiveServerTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from app1.models import Artigo, Bullet
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By  
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class TesteBase(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Configuração do Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        cls.selenium = webdriver.Chrome(options=chrome_options)
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.client = Client()
        self.home_url = reverse("home")

#parte dos testes com TestCase
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

#parte dos testes com Selenium
    def test_menu_hamburguer_abre_e_fecha(self):
        self.selenium.get(self.live_server_url + self.home_url)

        hamburger = self.selenium.find_element(By.ID, "menu-toggle")
        nav = self.selenium.find_element(By.ID, "main-nav")

        # Começa fechado
        self.assertNotIn("is-open", nav.get_attribute("class"))

        # Abre
        hamburger.click()
        time.sleep(0.3)
        self.assertIn("is-open", nav.get_attribute("class"))

        # Fecha
        hamburger.click()
        time.sleep(0.3)
        self.assertNotIn("is-open", nav.get_attribute("class"))

class teste_bullets(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Configurar Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        cls.selenium = webdriver.Chrome(options=chrome_options)
        cls.selenium.implicitly_wait(4)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.client = Client()
        self.artigo = Artigo.objects.create(titulo="Artigo de Teste")
        self.url = reverse("bullets_view", args=[self.artigo.id])
#teste django
    def test_renderiza_sem_bullets(self):
        response = self.client.get(self.url)

        self.assertContains(response, "Nenhum Ponto Chave Encontrado")
        self.assertContains(response, "ainda não possui pontos chave")

    def test_renderiza_com_bullets(self):
        Bullet.objects.create(artigo=self.artigo, bullets="Primeiro ponto")
        Bullet.objects.create(artigo=self.artigo, bullets="Segundo ponto")

        response = self.client.get(self.url)

        # título dinâmico
        self.assertContains(response, 'Pontos Chave do Artigo: "Artigo de Teste"')

        # bullets
        self.assertContains(response, "Primeiro ponto")
        self.assertContains(response, "Segundo ponto")
#teste selenium
    def test_selenium_renderiza_bullets(self):
        Bullet.objects.create(artigo=self.artigo, bullets="Bullet Selenium")

        self.selenium.get(self.live_server_url + self.url)
        time.sleep(0.3)

        # Pega o texto da página
        body = self.selenium.find_element(By.TAG_NAME, "body").text

        self.assertIn("Pontos Chave do Artigo", body)
        self.assertIn("Bullet Selenium", body)

    def test_selenium_sem_bullets(self):
        self.selenium.get(self.live_server_url + self.url)
        time.sleep(0.3)

        body = self.selenium.find_element(By.TAG_NAME, "body").text

        self.assertIn("Nenhum Ponto Chave Encontrado", body)
        self.assertIn("ainda não possui pontos chave", body)

class cadastro_teste(TestCase, LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.url = reverse("cadastro")
        try:
            cls.browser = webdriver.Chrome()
            cls.selenium_enabled = True
        except:
            cls.selenium_enabled = False

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "selenium_enabled", False):
            cls.browser.quit()
        super().tearDownClass()

    def test_django_get(self):
        r=self.client.get(self.url)
        self.assertEqual(r.status_code,200)
        self.assertContains(r,"Crie sua conta")

    def test_django_post_invalido(self):
        r=self.client.post(self.url,{})
        self.assertEqual(r.status_code,200)
        self.assertIn("errorlist",r.content.decode())

    def test_django_post_valido(self):
        r=self.client.post(self.url,{
            "username":"user1",
            "email":"u1@example.com",
            "password1":"Senha123!",
            "password2":"Senha123!"
        })
        self.assertEqual(r.status_code,302)
        self.assertEqual(r.url,reverse("home"))

    @pytest.mark.django_db
    def test_pytest_post(self):
        c=Client()
        r=c.post(self.url,{
            "username":"user2",
            "email":"u2@example.com",
            "password1":"Senha123!",
            "password2":"Senha123!"
        })
        assert r.status_code==302
        assert r.url==reverse("home")

    def test_selenium_fluxo(self):
        if not getattr(self,"selenium_enabled",False):
            self.skipTest("Selenium não disponível")
        self.browser.get(self.live_server_url+self.url)
        self.browser.find_element(By.ID,"id_username").send_keys("user3")
        self.browser.find_element(By.ID,"id_email").send_keys("u3@example.com")
        self.browser.find_element(By.ID,"id_password1").send_keys("Senha123!")
        self.browser.find_element(By.ID,"id_password2").send_keys("Senha123!")
        self.browser.find_element(By.CSS_SELECTOR,"button[type='submit']").click()
        self.assertIn(reverse("home"),self.browser.current_url)

class contexto_teste(TestCase, LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client=Client()
        cls.url=reverse("exibir_artigo",args=[1])
        try:
            cls.browser=webdriver.Chrome()
            cls.selenium_enabled=True
        except:
            cls.selenium_enabled=False

    @classmethod
    def tearDownClass(cls):
        if getattr(cls,"selenium_enabled",False):
            cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        from app1.models import Artigo
        self.artigo=Artigo.objects.create(
            id=1,
            titulo="Titulo Teste",
            conteudo="Conteudo Teste"
        )

    def test_django_get(self):
        r=self.client.get(self.url)
        self.assertEqual(r.status_code,200)
        self.assertContains(r,"Titulo Teste")
        self.assertContains(r,"Conteudo Teste")

    def test_django_sem_links(self):
        r=self.client.get(self.url)
        self.assertContains(r,"Nenhum contexto adicional encontrado")

    @pytest.mark.django_db
    def test_pytest_render(self):
        c=Client()
        r=c.get(self.url)
        assert r.status_code==200
        assert "Titulo Teste" in r.content.decode()

    def test_selenium_render(self):
        if not getattr(self,"selenium_enabled",False):
            self.skipTest("Selenium não disponível")
        self.browser.get(self.live_server_url+self.url)
        h=self.browser.find_element(By.TAG_NAME,"h1").text
        self.assertEqual(h,"Titulo Teste")

class newsletter_teste(TestCase, LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client=Client()
        cls.url=reverse("newsletter")
        try:
            cls.browser=webdriver.Chrome()
            cls.selenium_enabled=True
        except:
            cls.selenium_enabled=False

    @classmethod
    def tearDownClass(cls):
        if getattr(cls,"selenium_enabled",False):
            cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        from app1.models import Artigo
        self.artigo=Artigo.objects.create(
            titulo="Artigo Teste",
            subtitulo="Resumo Teste",
            imagem_url="https://placehold.co/150x150",
            categoria="Tecnologia"
        )

    def test_django_render(self):
        r=self.client.get(self.url,{"categoria":"Tecnologia"})
        self.assertEqual(r.status_code,200)
        self.assertContains(r,"Jornal do Commercio")
        self.assertContains(r,"Novidades na categoria")
        self.assertContains(r,"Artigo Teste")

    @pytest.mark.django_db
    def test_pytest_render(self):
        c=Client()
        r=c.get(self.url,{"categoria":"Tecnologia"})
        assert r.status_code==200
        t=r.content.decode()
        assert "Jornal do Commercio" in t
        assert "Artigo Teste" in t

    def test_selenium_render(self):
        if not getattr(self,"selenium_enabled",False):
            self.skipTest("Selenium não disponível")
        self.browser.get(self.live_server_url+self.url+"?categoria=Tecnologia")
        h=self.browser.find_element(By.TAG_NAME,"h1").text
        self.assertEqual(h,"Jornal do Commercio")

class artigo_teste(TestCase, LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client=Client()
        try:
            cls.browser=webdriver.Chrome()
            cls.selenium_enabled=True
        except:
            cls.selenium_enabled=False

    @classmethod
    def tearDownClass(cls):
        if getattr(cls,"selenium_enabled",False):
            cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        from app1.models import Artigo
        self.user=User.objects.create_user(username="u",password="123")
        self.artigo=Artigo.objects.create(
            titulo="Artigo Teste",
            conteudo="Conteudo Teste",
        )
        self.url=reverse("exibir_artigo",args=[self.artigo.id])

    def test_django_render(self):
        r=self.client.get(self.url)
        self.assertEqual(r.status_code,200)
        self.assertContains(r,"Artigo Teste")
        self.assertContains(r,"Sugestões de Leitura")
        self.assertContains(r,"Ver Pontos Chave")
        self.assertContains(r,"Ver conteudo de contexto")

    def test_banner(self):
        r=self.client.get(self.url,{"mensagem":"Sucesso"})
        self.assertContains(r,"Sucesso")

    def test_favoritar_deslogado(self):
        r=self.client.get(self.url)
        self.assertContains(r,"fazer login")

    def test_favoritar_logado(self):
        self.client.login(username="u",password="123")
        r=self.client.get(self.url)
        self.assertContains(r,"Favoritar")

    @pytest.mark.django_db
    def test_pytest_render(self):
        c=Client()
        r=c.get(self.url)
        assert r.status_code==200
        html=r.content.decode()
        assert "Artigo Teste" in html

    def test_selenium_render(self):
        if not getattr(self,"selenium_enabled",False):
            self.skipTest("Selenium não disponível")
        self.browser.get(self.live_server_url+self.url)
        h1=self.browser.find_element(By.TAG_NAME,"h1").text
        self.assertEqual(h1,"Artigo Teste")

class home_teste(TestCase, LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client=Client()
        cls.url=reverse("home")
        try:
            cls.browser=webdriver.Chrome()
            cls.selenium_enabled=True
        except:
            cls.selenium_enabled=False

    @classmethod
    def tearDownClass(cls):
        if getattr(cls,"selenium_enabled",False):
            cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        from app1.models import Artigo
        self.a1=Artigo.objects.create(
            titulo="Artigo Interesse 1",
            resumo="Resumo 1",
            categoria="Tech"
        )
        self.a2=Artigo.objects.create(
            titulo="Artigo Recente 1",
            resumo="Resumo 2",
            categoria="News"
        )

    def test_django_render(self):
        r=self.client.get(self.url)
        self.assertEqual(r.status_code,200)
        self.assertContains(r,"Mais Recentes")
        self.assertContains(r,"Artigo Interesse 1")
        self.assertContains(r,"Artigo Recente 1")

    @pytest.mark.django_db
    def test_pytest_render(self):
        c=Client()
        r=c.get(self.url)
        assert r.status_code==200
        html=r.content.decode()
        assert "Mais Recentes" in html
        assert "Artigo Interesse 1" in html

    def test_selenium_render(self):
        if not getattr(self,"selenium_enabled",False):
            self.skipTest("Selenium não disponível")
        self.browser.get(self.live_server_url+self.url)
        h=self.browser.find_element(By.TAG_NAME,"h3").text
        self.assertEqual(h,"Mais Recentes")

class login_teste(TestCase):
    def setUp(self):
        self.client=Client()

    def test_login_existente_template_django(self):
        url=reverse('login_existente')
        response=self.client.get(url)
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'Entrar na Conta')
        self.assertContains(response,'id_login')
        self.assertContains(response,'id_email')
        self.assertContains(response,'id_senha')

    @pytest.mark.django_db
    def test_login_existente_template_pytest(self,client):
        url=reverse('login_existente')
        r=client.get(url)
        assert r.status_code==200
        assert 'Entrar na Conta' in r.content.decode()
        assert 'id_login' in r.content.decode()
        assert 'id_email' in r.content.decode()
        assert 'id_senha' in r.content.decode()

    def test_login_existente_template_selenium(self,live_server,selenium):
        selenium.get(live_server.url+reverse('login_existente'))
        selenium.find_element(By.ID,'id_login')
        selenium.find_element(By.ID,'id_email')
        selenium.find_element(By.ID,'id_senha')
        selenium.find_element(By.CSS_SELECTOR,'button[type="submit"]')

    def test_login_page_template_django(self):
        url=reverse('login')
        response=self.client.get(url)
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'Entrar')
        self.assertContains(response,'Criar conta')
        self.assertContains(response,'Condições de uso')
        self.assertContains(response,'Conteúdos Personalizados')

    @pytest.mark.django_db
    def test_login_page_template_pytest(self,client):
        url=reverse('login')
        r=client.get(url)
        text=r.content.decode()
        assert r.status_code==200
        assert 'Entrar' in text
        assert 'Criar conta' in text
        assert 'Conteúdos Personalizados' in text

    def test_login_page_template_selenium(self,live_server,selenium):
        selenium.get(live_server.url+reverse('login'))
        selenium.find_element(By.CLASS_NAME,'login-main-title')
        selenium.find_element(By.CLASS_NAME,'login-btn-primary')
        selenium.find_element(By.CLASS_NAME,'login-btn-secondary')
        selenium.find_element(By.CLASS_NAME,'benefit-list')

class meusfav_teste(TestCase):
    def setUp(self):
        self.client=Client()

    def test_favoritos_template_django(self):
        url=reverse('favoritos')
        response=self.client.get(url)
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'Meus Artigos Favoritos')

    @pytest.mark.django_db
    def test_favoritos_template_pytest(self,client):
        url=reverse('favoritos')
        r=client.get(url)
        assert r.status_code==200
        assert 'Meus Artigos Favoritos' in r.content.decode()

    def test_favoritos_template_selenium(self,live_server,selenium):
        selenium.get(live_server.url+reverse('favoritos'))
        selenium.find_element(By.TAG_NAME,'h2')
        selenium.find_element(By.CLASS_NAME,'articles-list')

class Teste_newsletter(TestCase):
    def setUp(self):
        self.client=Client()

    def test_newsletter_template_django(self):
        url=reverse('newsletter')
        response=self.client.get(url)
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'Jornal do Commercio')
        self.assertContains(response,'ATIVAR!')

    @pytest.mark.django_db
    def test_newsletter_template_pytest(self,client):
        url=reverse('newsletter')
        r=client.get(url)
        assert r.status_code==200
        content=r.content.decode()
        assert 'Jornal do Commercio' in content
        assert 'ATIVAR!' in content

    def test_newsletter_template_selenium(self,live_server,selenium):
        selenium.get(live_server.url+reverse('newsletter'))
        selenium.find_element(By.CLASS_NAME,'header')
        selenium.find_element(By.CLASS_NAME,'btn')

class Teste_sugestão(TestCase):
    def setUp(self):
        self.client = Client()
        self.artigo = Artigo.objects.create(
            titulo="Teste Artigo",
            conteudo="Conteúdo do artigo",
            categoria="Esportes",
            data_publicacao=timezone.now()
        )

    def test_artigo_template_django(self):
        url = reverse('exibir_artigo', args=[self.artigo.pk])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, self.artigo.titulo)
        self.assertContains(r, self.artigo.categoria)
        self.assertContains(r, "Sugestões de Leitura")

    @pytest.mark.django_db
    def test_artigo_template_pytest(self, client):
        artigo = Artigo.objects.create(
            titulo="Teste Pytest",
            conteudo="abc",
            categoria="Cultura",
            data_publicacao=timezone.now()
        )
        url = reverse('exibir_artigo', args=[artigo.pk])
        r = client.get(url)
        assert r.status_code == 200
        c = r.content.decode()
        assert artigo.titulo in c
        assert "Sugestões de Leitura" in c

    def test_artigo_template_selenium(self, live_server, selenium):
        url = live_server.url + reverse('exibir_artigo', args=[self.artigo.pk])
        selenium.get(url)
        selenium.find_element(By.TAG_NAME, "h1")
        selenium.find_element(By.CLASS_NAME, "conteudo")
        selenium.find_element(By.CLASS_NAME, "sugestoes-box") 
    
class TesteCultura(TestCase):
    def setUp(self):
        self.client = Client()
        self.artigo = Artigo.objects.create(
            titulo="Artigo Cultura",
            conteudo="Conteúdo",
            categoria="Cultura",
            data_publicacao=timezone.now()
        )

    def test_template_django(self):
        r = self.client.get(reverse("topico_cultura"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Arte, Tradição e o Panorama Cultural")

    @pytest.mark.django_db
    def test_template_pytest(self, client):
        Artigo.objects.create(
            titulo="Teste Pytest Cultura",
            conteudo="aaa",
            categoria="Cultura",
            data_publicacao=timezone.now()
        )
        r = client.get(reverse("topico_cultura"))
        assert r.status_code == 200
        assert "CULTURA" in r.content.decode()

    def test_template_selenium(self, live_server, selenium):
        selenium.get(live_server.url + reverse("topico_cultura"))
        selenium.find_element(By.CLASS_NAME, "section-title")

class TesteEsportes(TestCase):
    def setUp(self):
        self.client = Client()
        self.artigo = Artigo.objects.create(
            titulo="Artigo Esportes",
            conteudo="Conteúdo",
            categoria="Esportes",
            data_publicacao=timezone.now()
        )

    def test_template_django(self):
        r = self.client.get(reverse("topico_esportes"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Resultados e Novidades Esportivas")

    @pytest.mark.django_db
    def test_template_pytest(self, client):
        Artigo.objects.create(
            titulo="Teste Pytest Esportes",
            conteudo="aaa",
            categoria="Esportes",
            data_publicacao=timezone.now()
        )
        r = client.get(reverse("topico_esportes"))
        assert r.status_code == 200
        assert "ESPORTES" in r.content.decode()

    def test_template_selenium(self, live_server, selenium):
        selenium.get(live_server.url + reverse("topico_esportes"))
        selenium.find_element(By.CLASS_NAME, "section-title") 

class TestePernambuco(TestCase):
    def setUp(self):
        self.client = Client()
        self.artigo = Artigo.objects.create(
            titulo="Artigo Pernambuco",
            conteudo="Conteúdo",
            categoria="Pernambuco",
            data_publicacao=timezone.now()
        )

    def test_template_django(self):
        r = self.client.get(reverse("topico_pernambuco"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Notícias e Fatos de Pernambuco")

    @pytest.mark.django_db
    def test_template_pytest(self, client):
        Artigo.objects.create(
            titulo="Teste Pytest Pernambuco",
            conteudo="aaa",
            categoria="Pernambuco",
            data_publicacao=timezone.now()
        )
        r = client.get(reverse("topico_pernambuco"))
        assert r.status_code == 200
        assert "PERNAMBUCO" in r.content.decode()

    def test_template_selenium(self, live_server, selenium):
        selenium.get(live_server.url + reverse("topico_pernambuco"))
        selenium.find_element(By.CLASS_NAME, "section-title")

class TestePolitica(TestCase):
    def setUp(self):
        self.client = Client()
        self.artigo = Artigo.objects.create(
            titulo="Artigo Política",
            conteudo="Conteúdo",
            categoria="Política",
            data_publicacao=timezone.now()
        )

    def test_template_django(self):
        r = self.client.get(reverse("topico_politica"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Análises e Notícias de Política")

    @pytest.mark.django_db
    def test_template_pytest(self, client):
        Artigo.objects.create(
            titulo="Teste Pytest Política",
            conteudo="aaa",
            categoria="Política",
            data_publicacao=timezone.now()
        )
        r = client.get(reverse("topico_politica"))
        assert r.status_code == 200
        assert "POLÍTICA" in r.content.decode()

    def test_template_selenium(self, live_server, selenium):
        selenium.get(live_server.url + reverse("topico_politica"))
        selenium.find_element(By.CLASS_NAME, "section-title")







    

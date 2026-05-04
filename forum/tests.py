from django.test import TestCase
from django.test import override_settings
from django.utils import timezone
from os import link

from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

import time

from forum.models import Pergunta




class BaseTestCase(LiveServerTestCase):
    """
    Classe-base que inicializa e encerra o Chrome em modo headless
    (sem interface gráfica) antes e depois de cada teste.

    LiveServerTestCase sobe um servidor HTTP temporário em uma 
    porta aleatória na própria máquina que está rodando os testes, usando 
    um banco de dados de teste isolado, e disponibiliza self.live_server_url 
    para que o Selenium possa acessá-lo.

    live_server_url aponta sempre para localhost. Ex: http://127.0.0.1:54321
    Esse servidor existe apenas durante a execução dos testes e é destruído 
    logo depois. 

    """
     
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        opts = Options()
        # opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1280,800")

        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=opts)

        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "driver"):
            cls.driver.quit()
        super().tearDownClass()

    # -------------------------------------------------------------------------
    # Métodos utilitários reutilizados pelos testes
    # -------------------------------------------------------------------------

    def abrir_pagina(self, caminho="/forum/"):
        """Navega para uma URL relativa ao servidor de teste."""
        self.driver.get(self.live_server_url + caminho)

    def criar_pergunta_via_model(
        self,
        titulo="Título de teste",
        detalhe="Detalhe da pergunta de teste.",
        tentativa="Tentativa de solução.",
        usuario="Equipe de engenheiros de testes",
    ):
        """Cria uma Pergunta diretamente no banco — útil para preparar o estado
        do sistema antes de um teste, sem depender da UI de inserção."""
        return Pergunta.objects.create(
            titulo=titulo,
            detalhe=detalhe,
            tentativa=tentativa,
            data_criacao=timezone.now(),
            usuario=usuario,
        )

    def criar_resposta_via_model(self, pergunta, texto="Resposta de teste.", usuario="respondedor"):
        """Cria uma Resposta diretamente no banco."""
        return pergunta.resposta_set.create(
            texto=texto,
            data_criacao=timezone.now(),
            usuario=usuario,
        )

class Teste_04_Votacao_Resposta(BaseTestCase):

    def test_07_resposta_deve_iniciar_com_zero_votos(self):
       
        # Criar pergunta e resposta direto no banco.
        pergunta = self.criar_pergunta_via_model(titulo="Pergunta para testar qtd de votos zero")
        self.criar_resposta_via_model(pergunta, "Resposta com zero votos.")

        # abre a página de detalhes da pergunta criada
        self.abrir_pagina(f"/forum/{pergunta.id}/")
      
        body = self.driver.find_element(By.TAG_NAME, "body").text
      
        # verifica se a contagem de votos inicial é 0
        self.assertIn("0 votos", body, "Contagem inicial de votos deveria ser 0.")


# Create your tests here.

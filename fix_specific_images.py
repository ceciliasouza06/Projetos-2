"""Atualiza imagens específicas para artigos existentes a partir de um dicionário fixo."""
import os
import sys
from pathlib import Path

import django
import requests
from django.core.files.base import ContentFile
from django.core.exceptions import MultipleObjectsReturned

# Configura o Django para scripts standalone.
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumen.settings")
django.setup()

from app1.models import Artigos  # noqa: E402


MAPPING = {
    # --- Lote 1 (Já mapeado anteriormente) ---
    "Mercado imobiliário do Recife cresce com novos empreendimentos": {
        "url": "https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=1000&q=80",
        "filename": "mercado_imob.jpg",
    },
    "Avanço da IA generativa transforma o mercado web": {
        "url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1000&q=80",
        "filename": "ia_tech_1.jpg",
    },
    "Grammy Latino 2025 terá cinco pernambucanos indicados": {
        "url": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?auto=format&fit=crop&w=1000&q=80",
        "filename": "grammy_latino.jpg",
    },
    "Megasena acumula e prêmio pode chegar a R$ 120 milhões": {
        "url": "https://images.unsplash.com/photo-1504275107627-0c2ba7a43dba?auto=format&fit=crop&w=1000&q=80",
        "filename": "megasena.jpg",
    },
    "Nova rota aérea liga Nordeste à Europa três vezes por semana": {
        "url": "https://images.unsplash.com/photo-1473186578172-c141e6798cf4?auto=format&fit=crop&w=1000&q=80",
        "filename": "rota_aerea.jpg",
    },
    "Porto de Suape bate recorde de movimentação no ano": {
        "url": "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1000&q=80",
        "filename": "porto_suape.jpg",
    },
    "Frente fria traz chuva forte e maré alta para o litoral de Pernambuco": {
        "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80",
        "filename": "frente_fria.jpg",
    },
    "Startup pernambucana cria app de telemedicina para idosos": {
        "url": "https://images.unsplash.com/photo-1527613426441-4da17471b66d?auto=format&fit=crop&w=1000&q=80",
        "filename": "telemedicina.jpg",
    },
    "Sport e Náutico empatam em clássico decisivo pelo estadual": {
        "url": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=1000&q=80",
        "filename": "classico_empate.jpg",
    },
    "Recife recebe festival de inovação e economia criativa": {
        "url": "https://images.unsplash.com/photo-1523580846011-d3a5bc25702b?auto=format&fit=crop&w=1000&q=80",
        "filename": "festival_inovacao.jpg",
    },
    # --- Lote 2 (Novos do Admin) ---
    "Adolescente é detido com 19 quilos de haxixe em aeroporto do Recife": {
        "url": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=1000&q=80",
        "filename": "aeroporto_apreensao.jpg",
    },
    "Nova PEC que aumenta valor das emendas parlamentares avança na Alepe": {
        "url": "https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=1000&q=80",
        "filename": "pec_alepe.jpg",
    },
    "Paço do Frevo cria selo musical para novos artistas do ritmo": {
        "url": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?auto=format&fit=crop&w=1000&q=80",
        "filename": "paco_frevo.jpg",
    },
    "Cães e gatos veem menos cores que humanos, revela estudo": {
        "url": "https://images.unsplash.com/photo-1517849845537-4d257902454a?auto=format&fit=crop&w=1000&q=80",
        "filename": "caes_gatos.jpg",
    },
    "ONU aprova plano para força internacional em Gaza": {
        "url": "https://images.unsplash.com/photo-1444084316824-dc26d6657664?auto=format&fit=crop&w=1000&q=80",
        "filename": "onu_gaza.jpg",
    },
    # --- Lote 3 (Estavam sem imagem, adicionei novas) ---
    "Dólar fecha em leve queda com otimismo sobre inflação": {
        "url": "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?auto=format&fit=crop&w=1000&q=80",
        "filename": "dolar_queda.jpg",
    },
    "Novo filme de ficção bate recorde de bilheteria": {
        "url": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1000&q=80",
        "filename": "filme_bilheteria.jpg",
    },
    "Sport e Náutico preparam clássico decisivo": {
        "url": "https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?auto=format&fit=crop&w=1000&q=80",
        "filename": "classico_preparo.jpg",
    },
    "Obras na Agamenon Magalhães alteram trânsito": {
        "url": "https://images.unsplash.com/photo-1508898578281-774ac4893c0c?auto=format&fit=crop&w=1000&q=80",
        "filename": "obras_agamenon.jpg",
    },
    # --- Atenção: Duplicata de título com 'G' maiúsculo ---
    "Avanço da IA Generativa transforma o mercado web": {
        "url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=1000&q=80",
        "filename": "ia_tech_2.jpg",
    },
}


def save_image_to_field(instance: Artigos, filename: str, content: ContentFile, image_url: str) -> None:
    """Salva imagem tanto para ImageField/FileField quanto para URLField de forma segura."""
    # Se for FileField/ImageField, usamos o método save para gravar o arquivo.
    if hasattr(instance.imagem, "save"):
        instance.imagem.save(filename, content, save=True)
    else:
        # Fallback para campos não-arquivo (ex.: URLField) mantém a URL original.
        instance.imagem = image_url
        instance.save(update_fields=["imagem"])


def main() -> None:
    for title, data in MAPPING.items():
        url = data["url"]
        filename = data["filename"]

        try:
            artigo = Artigos.objects.get(titulo=title)
        except Artigos.DoesNotExist:
            print(f"[NOT FOUND] Artigo não localizado: '{title}'")
            continue
        except MultipleObjectsReturned:
            artigo = (
                Artigos.objects.filter(titulo=title).order_by("-id").first()
            )
            if artigo is None:
                print(f"[ERROR] Duplicata sem registros retornados para '{title}'")
                continue
            print(f"[DUPLICATE] Usando artigo mais recente id={artigo.id} para título '{title}'")

        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            print(f"[DOWNLOAD FAIL] Não foi possível baixar '{title}' ({url}): {exc}")
            continue

        content_file = ContentFile(response.content)

        try:
            save_image_to_field(artigo, filename, content_file, url)
        except Exception as exc:  # noqa: BLE001
            print(f"[SAVE FAIL] Erro ao salvar imagem para '{title}': {exc}")
            continue

        print(f"[OK] Imagem atualizada para '{title}' com arquivo '{filename}'")


if __name__ == "__main__":
    main()

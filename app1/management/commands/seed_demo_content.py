from django.core.management.base import BaseCommand
from django.utils import timezone
from app1.models import Artigos


SAMPLE_ARTICLES = [
    {
        "titulo": "Paço do Frevo cria selo musical para novos artistas do ritmo",
        "categoria": "Cultura",
        "resumo": "Selo Paço do Frevo & Muzak Music lança produções musicais com foco no ritmo pernambucano.",
        "imagem": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Nova PEC que aumenta valor das emendas parlamentares avança na Alepe",
        "categoria": "Política",
        "resumo": "Proposta segue para plenário e pode destravar verbas de infraestrutura no estado.",
        "imagem": "https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Adolescente é detido com 19 quilos de haxixe em aeroporto do Recife",
        "categoria": "Brasil",
        "resumo": "Operação da PF apreende drogas escondidas em bagagem despachada, com destino internacional.",
        "imagem": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "ONU aprova plano para força internacional em Gaza",
        "categoria": "Mundo",
        "resumo": "Resolução autoriza estabilização humanitária e monitoramento de cessar-fogo.",
        "imagem": "https://images.unsplash.com/photo-1444084316824-dc26d6657664?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Cães e gatos veem menos cores que humanos, revela estudo",
        "categoria": "Entretenimento",
        "resumo": "Pesquisa mostra paleta reduzida de cores para pets e impactos no comportamento.",
        "imagem": "https://images.unsplash.com/photo-1517849845537-4d257902454a?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Grammy Latino 2025 terá cinco pernambucanos indicados",
        "categoria": "Cultura",
        "resumo": "Artistas locais concorrem em categorias de música regional e contemporânea.",
        "imagem": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Porto de Suape bate recorde de movimentação no ano",
        "categoria": "Economia",
        "resumo": "Crescimento impulsionado por cabotagem e novos contratos de logística.",
        "imagem": "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Sport e Náutico empatam em clássico decisivo pelo estadual",
        "categoria": "Esportes",
        "resumo": "Partida termina sem gols, mas com grande atuação dos goleiros.",
        "imagem": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Avanço da IA generativa transforma o mercado web",
        "categoria": "Tecnologia",
        "resumo": "Ferramentas aceleram criação de produtos digitais e desafiam modelos tradicionais.",
        "imagem": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Megasena acumula e prêmio pode chegar a R$ 120 milhões",
        "categoria": "Loterias",
        "resumo": "Nenhuma aposta acerta as seis dezenas e expectativa atrai filas nas casas lotéricas.",
        "imagem": "https://images.unsplash.com/photo-1504275107627-0c2ba7a43dba?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Frente fria traz chuva forte e maré alta para o litoral de Pernambuco",
        "categoria": "Tempo",
        "resumo": "Defesa Civil em alerta para pontos de alagamento e ventos moderados.",
        "imagem": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Mercado imobiliário do Recife cresce com novos empreendimentos",
        "categoria": "Brasil",
        "resumo": "Lançamentos em Boa Viagem e Cais José Estelita lideram o volume de vendas.",
        "imagem": "https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Startup pernambucana cria app de telemedicina para idosos",
        "categoria": "Saúde",
        "resumo": "Plataforma conecta pacientes e especialistas em poucos cliques com prontuário digital.",
        "imagem": "https://images.unsplash.com/photo-1582719478145-3b1aecea0bdf?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Recife recebe festival de inovação e economia criativa",
        "categoria": "Eventos",
        "resumo": "Programação inclui trilha de IA, cidades inteligentes e negócios de impacto.",
        "imagem": "https://images.unsplash.com/photo-1523580846011-d3a5bc25702b?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Nova rota aérea liga Nordeste à Europa três vezes por semana",
        "categoria": "Turismo",
        "resumo": "Voo direto deve ampliar fluxo de turistas e exportações de frutas e pescados.",
        "imagem": "https://images.unsplash.com/photo-1504198453319-5ce911bafcde?auto=format&fit=crop&w=1000&q=80",
    },
]


class Command(BaseCommand):
    help = "Popula o banco com notícias demo para visualização da home."

    def handle(self, *args, **options):
        created = 0
        now = timezone.now()

        for idx, item in enumerate(SAMPLE_ARTICLES):
            artigo, was_created = Artigos.objects.get_or_create(
                titulo=item["titulo"],
                defaults={
                    "categoria": item["categoria"],
                    "resumo": item.get("resumo", ""),
                    "conteudo": item.get("conteudo", item["resumo"]),
                    "imagem": item.get("imagem", ""),
                    "data_publicacao": now - timezone.timedelta(days=idx),
                },
            )
            if was_created:
                created += 1
            else:
                # Atualiza dados para manter coerência visual.
                artigo.categoria = item["categoria"]
                artigo.resumo = item.get("resumo", artigo.resumo)
                artigo.conteudo = item.get("conteudo", artigo.conteudo)
                artigo.imagem = item.get("imagem", artigo.imagem)
                artigo.save(update_fields=["categoria", "resumo", "conteudo", "imagem"])

        self.stdout.write(self.style.SUCCESS(f"{created} artigos criados; total atual: {Artigos.objects.count()}"))

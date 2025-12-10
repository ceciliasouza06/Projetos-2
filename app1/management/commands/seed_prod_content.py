from django.core.management.base import BaseCommand
from django.utils import timezone

from app1.models import Artigos

# Mesmo conteúdo da seed de demo, mas sem criar comentários nem notificações extras.
ARTICLES = [
    {
        "titulo": "Mercado imobiliário do Recife cresce com novos empreendimentos",
        "categoria": "Economia",
        "resumo": "Novos lançamentos em áreas centrais e no litoral mantêm o mercado aquecido.",
        "conteudo": (
            "<p><strong>Onde estão os lançamentos</strong></p>"
            "<p>Boa Viagem, Cais José Estelita e o eixo Norte lideram a oferta de prédios mistos e studios.</p>"
            "<p><strong>Perfil do comprador</strong></p>"
            "<p>Jovens buscam unidades compactas com coworking e serviços de assinatura; investidores focam em locação por temporada.</p>"
            "<p><strong>Perspectiva de preços</strong></p>"
            "<p>Com juros mais baixos, incorporadoras projetam estabilidade e entregas faseadas até 2026.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Avanço da IA generativa transforma o mercado web",
        "categoria": "Tecnologia",
        "resumo": "Ferramentas aceleram prototipagem, personalização e novos modelos de serviços.",
        "conteudo": (
            "<p><strong>Tendência</strong></p>"
            "<p>Modelos de texto e imagem entram no fluxo de UX, atendimento e marketing das agências digitais.</p>"
            "<p><strong>Novos times</strong></p>"
            "<p>Squads de IA combinam design, dados e engenharia para entregar provas de conceito em dias.</p>"
            "<p><strong>Governança</strong></p>"
            "<p>Especialistas pedem política clara de dados, direitos autorais e transparência nos prompts.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Grammy Latino 2025 terá cinco pernambucanos indicados",
        "categoria": "Cultura",
        "resumo": "Cena local emplaca artistas em categorias de música regional e contemporânea.",
        "conteudo": (
            "<p><strong>Quem está na lista</strong></p>"
            "<p>Bandas de manguebeat, frevo e pop eletrônico aparecem em cinco categorias diferentes.</p>"
            "<p><strong>Força regional</strong></p>"
            "<p>Produtores celebram a exportação de música independente e parcerias com selos internacionais.</p>"
            "<p><strong>Agenda pré-premiação</strong></p>"
            "<p>Artistas programam showcases em Miami e levam maracatu ao tapete vermelho.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Megasena acumula e prêmio pode chegar a R$ 120 milhões",
        "categoria": "Loterias",
        "resumo": "Sem ganhadores no último sorteio, apostadores correm para bolões.",
        "conteudo": (
            "<p><strong>Acúmulo</strong></p>"
            "<p>O prêmio sobe após nenhum bilhete acertar as seis dezenas, estimulando filas nas lotéricas.</p>"
            "<p><strong>Chances reais</strong></p>"
            "<p>Matemáticos lembram que a probabilidade não muda; o jogo simples permanece a mesma aposta.</p>"
            "<p><strong>Planejamento</strong></p>"
            "<p>Especialistas em finanças sugerem limitar gastos e tratar a aposta como lazer, não investimento.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1504275107627-0c2ba7a43dba?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Nova rota aérea liga Nordeste à Europa três vezes por semana",
        "categoria": "Turismo",
        "resumo": "Voo direto Recife-Lisboa promete aumentar fluxo de turistas e exportações.",
        "conteudo": (
            "<p><strong>Operação</strong></p>"
            "<p>A rota parte três vezes por semana, com conexões rápidas para outras capitais europeias.</p>"
            "<p><strong>Impacto</strong></p>"
            "<p>Hotéis e restaurantes projetam alta na ocupação; setor de frutas e pescados ganha novo corredor logístico.</p>"
            "<p><strong>Lançamento</strong></p>"
            "<p>Primeiro voo decola em janeiro com tarifas promocionais na semana inaugural.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1473186578172-c141e6798cf4?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Porto de Suape bate recorde de movimentação no ano",
        "categoria": "Economia",
        "resumo": "Alta de cargas conteinerizadas e novas rotas de cabotagem puxam resultado.",
        "conteudo": (
            "<p><strong>Números</strong></p>"
            "<p>Movimento cresceu 18% no acumulado, com destaque para celulose e veículos.</p>"
            "<p><strong>Fatores</strong></p>"
            "<p>Cabotagem reforçada e automação de gates ajudaram a reduzir fila de caminhões.</p>"
            "<p><strong>Próximas obras</strong></p>"
            "<p>Autoridade portuária planeja dragagem e ampliação de terminais até o fim de 2026.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Frente fria traz chuva forte e maré alta para o litoral de Pernambuco",
        "categoria": "Tempo",
        "resumo": "Defesa Civil alerta para alagamentos e reforça equipes de drenagem.",
        "conteudo": (
            "<p><strong>Previsão</strong></p>"
            "<p>Pancadas intensas são esperadas à noite, com maré elevada na manhã seguinte.</p>"
            "<p><strong>Cuidados</strong></p>"
            "<p>Moradores devem evitar áreas de risco, monitorar encostas e redobrar atenção no trânsito.</p>"
            "<p><strong>Monitoramento</strong></p>"
            "<p>Prefeituras acompanham volumes de chuva em tempo real e acionam abrigos se necessário.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Startup pernambucana cria app de telemedicina para idosos",
        "categoria": "Saúde",
        "resumo": "Interface simples conecta pacientes, médicos e familiares com prontuário digital.",
        "conteudo": (
            "<p><strong>Como funciona</strong></p>"
            "<p>Botões grandes, lembretes de medicação e videochamadas facilitam consultas remotas.</p>"
            "<p><strong>Benefícios</strong></p>"
            "<p>Familiares acompanham prescrições em tempo real e recebem alertas de exames.</p>"
            "<p><strong>Próximo passo</strong></p>"
            "<p>A empresa testa integração com farmácias para entrega de medicamentos em casa.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1527613426441-4da17471b66d?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Sport e Náutico empatam em clássico decisivo pelo estadual",
        "categoria": "Esportes",
        "resumo": "Goleiros brilham e mantêm o 0 a 0 em jogo truncado nos Aflitos.",
        "conteudo": (
            "<p><strong>O jogo</strong></p>"
            "<p>Chances pelos lados e um travessão para cada time marcaram o primeiro tempo.</p>"
            "<p><strong>Destaques</strong></p>"
            "<p>Defesas difíceis dos goleiros e entrada da base rubro-negra deram fôlego na reta final.</p>"
            "<p><strong>Classificação</strong></p>"
            "<p>Resultado deixa a decisão aberta para o confronto de volta no fim de semana.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Recife recebe festival de inovação e economia criativa",
        "categoria": "Eventos",
        "resumo": "Trilhas de IA, cidades inteligentes e negócios de impacto ocupam o Cais do Sertão.",
        "conteudo": (
            "<p><strong>Programação</strong></p>"
            "<p>Painéis sobre IA em serviços públicos, workshops de prototipagem e feira de startups.</p>"
            "<p><strong>Para quem</strong></p>"
            "<p>Empreendedores, gestores e estudantes encontram mentorias e vagas de estágio.</p>"
            "<p><strong>Até quando</strong></p>"
            "<p>Evento segue até domingo com área de demonstrações e pitches abertos ao público.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1523580846011-d3a5bc25702b?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Adolescente é detido com 19 quilos de haxixe em aeroporto do Recife",
        "categoria": "Brasil",
        "resumo": "Operação da PF intercepta bagagem com droga antes de embarque internacional.",
        "conteudo": (
            "<p><strong>Flagrante</strong></p>"
            "<p>Agentes suspeitaram do peso da mala no raio-x e acionaram a equipe canina.</p>"
            "<p><strong>Investigação</strong></p>"
            "<p>Polícia apura se o jovem integra rede de tráfico que usa o Nordeste como rota.</p>"
            "<p><strong>Impacto no terminal</strong></p>"
            "<p>Voos seguiram dentro do horário enquanto a bagagem era periciada.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Nova PEC que aumenta valor das emendas parlamentares avança na Alepe",
        "categoria": "Política",
        "resumo": "Texto eleva teto das emendas e cria gatilhos de transparência para execução.",
        "conteudo": (
            "<p><strong>O que muda</strong></p>"
            "<p>Parlamentares terão mais verba individual, com regras de publicação de contratos.</p>"
            "<p><strong>Debate</strong></p>"
            "<p>Base defende previsibilidade para obras; oposição cobra controle social sobre gastos.</p>"
            "<p><strong>Calendário</strong></p>"
            "<p>Segunda votação ocorre na próxima semana e pode valer já no próximo orçamento.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Paço do Frevo cria selo musical para novos artistas do ritmo",
        "categoria": "Cultura",
        "resumo": "Iniciativa amplia presença do frevo em plataformas e conecta veteranos a novatos.",
        "conteudo": (
            "<p><strong>Linha editorial</strong></p>"
            "<p>Catálogo mistura arranjos tradicionais e beats eletrônicos sem perder metais e alfaias.</p>"
            "<p><strong>Planos</strong></p>"
            "<p>Primeiras faixas saem ainda em novembro com clipes gravados no Recife Antigo.</p>"
            "<p><strong>Artistas</strong></p>"
            "<p>O selo aposta em jovens compositores e convida mestres do frevo para colaborações.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Cães e gatos veem menos cores que humanos, revela estudo",
        "categoria": "Curiosidades",
        "resumo": "Pesquisa detalha paleta reduzida dos pets e sugere ajustes em brinquedos e ambientes.",
        "conteudo": (
            "<p><strong>Como eles enxergam</strong></p>"
            "<p>Pets distinguem tons de azul e amarelo; vermelho e verde se confundem na visão.</p>"
            "<p><strong>Por que importa</strong></p>"
            "<p>Brinquedos adequados e contrastes ajudam na estimulação e diminuem ansiedade.</p>"
            "<p><strong>Recomendações</strong></p>"
            "<p>Veterinários sugerem variar texturas e cheiros, já que o olfato segue protagonista.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1517849845537-4d257902454a?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "ONU aprova plano para força internacional em Gaza",
        "categoria": "Mundo",
        "resumo": "Mandato prevê apoio humanitário, proteção de corredores e mediação de prisioneiros.",
        "conteudo": (
            "<p><strong>O que foi votado</strong></p>"
            "<p>Resolução autoriza estabilização de áreas civis e supervisão do cessar-fogo.</p>"
            "<p><strong>Desafios</strong></p>"
            "<p>Especialistas lembram que a missão depende de coordenação com atores locais.</p>"
            "<p><strong>Próximos 30 dias</strong></p>"
            "<p>Conselho volta a se reunir para medir entregas de ajuda e ajustar a operação.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1444084316824-dc26d6657664?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Dólar fecha em leve queda com otimismo sobre inflação",
        "categoria": "Economia",
        "resumo": "Moeda recua após dados de preços mais fracos nos EUA e expectativa de juros menores.",
        "conteudo": (
            "<p><strong>Motivo do movimento</strong></p>"
            "<p>Investidores reduziram apostas em alta de juros, favorecendo moedas emergentes.</p>"
            "<p><strong>Impacto local</strong></p>"
            "<p>Importadores aproveitam para fechar contratos; exportadores seguem cautelosos.</p>"
            "<p><strong>Olho no calendário</strong></p>"
            "<p>Próxima divulgação de inflação pode consolidar ou reverter a tendência.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Novo filme de ficção bate recorde de bilheteria",
        "categoria": "Entretenimento",
        "resumo": "Produção espacial soma público histórico no fim de semana de estreia.",
        "conteudo": (
            "<p><strong>Sinopse</strong></p>"
            "<p>A trama acompanha uma missão em lua gelada e mistura suspense com drama familiar.</p>"
            "<p><strong>Números</strong></p>"
            "<p>Filme arrecadou acima das previsões e já prepara sequência confirmada pelo estúdio.</p>"
            "<p><strong>Crítica</strong></p>"
            "<p>Fotografia e trilha sonora foram elogiadas; roteiro dividiu opiniões.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Sport e Náutico preparam clássico decisivo",
        "categoria": "Esportes",
        "resumo": "Times ajustam escalações e estudam rivais antes do duelo pelo estadual.",
        "conteudo": (
            "<p><strong>Preparação</strong></p>"
            "<p>Sport treina bolas paradas; Náutico reforça transição rápida com garotos da base.</p>"
            "<p><strong>Prováveis times</strong></p>"
            "<p>Técnicos devem manter esquemas com três atacantes e laterais ofensivos.</p>"
            "<p><strong>Clima</strong></p>"
            "<p>Ingressos quase esgotados e segurança reforçada para o domingo à tarde.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Obras na Agamenon Magalhães alteram trânsito",
        "categoria": "Pernambuco",
        "resumo": "Intervenções em viadutos exigem desvios e reforço na sinalização.",
        "conteudo": (
            "<p><strong>Interdições</strong></p>"
            "<p>Pistas locais têm bloqueios noturnos para concretagem e ajuste de drenagem.</p>"
            "<p><strong>Rotas alternativas</strong></p>"
            "<p>CTTU indica cruzamento pela Rui Barbosa e avenidas paralelas para evitar congestionamentos.</p>"
            "<p><strong>Prazo</strong></p>"
            "<p>Obras seguem até o fim do mês com monitoramento em tempo real de tráfego.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1508898578281-774ac4893c0c?auto=format&fit=crop&w=1000&q=80",
    },
    {
        "titulo": "Avanço da IA Generativa transforma o mercado web",
        "categoria": "Tecnologia",
        "resumo": "Startups locais testam modelos customizados para sotaque e contexto regional.",
        "conteudo": (
            "<p><strong>Contexto local</strong></p>"
            "<p>Empresas do Porto Digital treinam modelos com dados de serviços públicos e dialetos.</p>"
            "<p><strong>Casos de uso</strong></p>"
            "<p>Chatbots bilíngues, geração de imagens com referências do Recife e automação de relatórios.</p>"
            "<p><strong>Próximos passos</strong></p>"
            "<p>Laboratórios buscam parcerias com universidades para ampliar datasets e reduzir vieses.</p>"
        ),
        "imagem": "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=1000&q=80",
    },
]


class Command(BaseCommand):
    help = "Popula o banco de produção com artigos completos."

    def handle(self, *args, **options):
        if Artigos.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Artigos já existem no banco. Nenhuma ação realizada."
                )
            )
            return

        now = timezone.now()
        artigos = []

        for idx, item in enumerate(ARTICLES):
            artigos.append(
                Artigos(
                    titulo=item["titulo"],
                    categoria=item["categoria"],
                    resumo=item["resumo"],
                    conteudo=item["conteudo"],
                    imagem=item.get("imagem", ""),
                    data_publicacao=now - timezone.timedelta(days=idx),
                )
            )

        created = Artigos.objects.bulk_create(artigos)

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(created)} artigos criados para o ambiente de produção."
            )
        )

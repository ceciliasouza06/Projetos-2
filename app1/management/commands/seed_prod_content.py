from django.core.management.base import BaseCommand
from django.utils import timezone

from app1.models import Artigos


PROD_ARTICLES = [
    {
        "titulo": "Governo lança plano de revitalização do Rio Capibaribe",
        "categoria": "Pernambuco",
        "resumo": "Programa integra dragagem, reflorestamento e ciclovias nas margens do rio.",
        "conteudo": (
            "O governo estadual apresentou um pacote de revitalização do Rio Capibaribe com metas de curto e médio prazo. "
            "A proposta reúne dragagem em trechos críticos, plantio de mata ciliar e criação de ciclovias ligando bairros ribeirinhos. "
            "Prefeituras da Região Metropolitana assinaram um termo de cooperação para acompanhar as obras e fiscalizar a ocupação irregular.\n\n"
            "Além da infraestrutura, o plano prevê ações de educação ambiental em escolas públicas e monitoramento constante da qualidade da água. "
            "A previsão é que os primeiros trechos sejam entregues ainda neste semestre, reduzindo enchentes e devolvendo o rio à população."
        ),
        "imagem": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "titulo": "Assembleia aprova pacote anticorrupção para prefeituras",
        "categoria": "Política",
        "resumo": "Projeto cria metas de transparência, exige compras digitais e reforça controle social.",
        "conteudo": (
            "Deputados estaduais aprovaram, por ampla maioria, um pacote de medidas anticorrupção voltado às prefeituras. "
            "O texto obriga a publicação de todos os contratos em portais unificados, amplia a atuação dos conselhos municipais "
            "e estabelece punições mais rápidas para gestores que descumprirem a lei de acesso à informação.\n\n"
            "A bancada de oposição tentou incluir emendas para limitar gastos com publicidade institucional, mas a base do governo "
            "manteve o texto original. Prefeitos terão seis meses para adequar os sistemas e treinar as equipes."
        ),
        "imagem": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "titulo": "Sport confirma novo técnico e pré-temporada no interior",
        "categoria": "Esportes",
        "resumo": "Clube aposta em calendário enxuto e treinos fechados para arrancar bem na Série B.",
        "conteudo": (
            "O Sport anunciou o treinador que comandará o time na próxima temporada e confirmou que a pré-temporada será realizada em Caruaru. "
            "O elenco deve se apresentar na primeira semana de janeiro para testes físicos, jogos-treino com equipes do interior e ajustes táticos. "
            "A diretoria disse que manterá a base do ano anterior e busca reforços pontuais para o meio-campo.\n\n"
            "O novo comandante destacou que quer um time mais intenso e com variações de esquema. "
            "A torcida prepara caravanas para acompanhar os primeiros amistosos e observar a evolução do grupo."
        ),
        "imagem": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "titulo": "Festival de Inverno de Garanhuns traz programação híbrida",
        "categoria": "Cultura",
        "resumo": "Edição aposta em shows presenciais, transmissões online e oficinas gratuitas.",
        "conteudo": (
            "A nova edição do Festival de Inverno de Garanhuns terá palcos espalhados pelo centro e transmissões ao vivo para quem acompanha de casa. "
            "A curadoria confirmou artistas locais e nacionais, com espaço para frevo, rock, música instrumental e debates sobre economia criativa. "
            "A rede hoteleira já registra alta ocupação e comerciantes montam estrutura para receber o público.\n\n"
            "Além dos shows, o evento oferece oficinas de dança, audiovisual e empreendedorismo cultural, todas gratuitas e com inscrições antecipadas. "
            "A prefeitura promete reforçar a segurança e os roteiros de transporte para evitar aglomerações em horários de pico."
        ),
        "imagem": "https://images.unsplash.com/photo-1523580846011-d3a5bc25702b?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "titulo": "Opinião: Como recuperar a confiança no transporte público do Recife",
        "categoria": "Opinião",
        "resumo": "Transparência, previsibilidade e novas rotas são pilares para reconquistar o passageiro.",
        "conteudo": (
            "Nos últimos anos, a relação entre usuários e operadores do transporte público no Recife se desgastou por atrasos, superlotação e falhas na comunicação. "
            "Recuperar essa confiança exige publicar dados em tempo real, esclarecer custos e aproximar o planejamento das demandas dos bairros periféricos.\n\n"
            "Sem ouvir quem depende do ônibus diariamente, qualquer solução vira maquiagem. "
            "É preciso abrir as planilhas, testar rotas com participação das comunidades e garantir que as melhorias sejam monitoradas por indicadores claros."
        ),
        "imagem": "https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "titulo": "Porto Digital anuncia laboratório de IA generativa",
        "categoria": "Tecnologia",
        "resumo": "Nova estrutura oferece mentoria para startups e projetos corporativos em Recife.",
        "conteudo": (
            "O Porto Digital lançou um laboratório dedicado a soluções de inteligência artificial generativa, com foco em empresas de serviços e indústria criativa. "
            "O espaço terá squads multidisciplinares, mentores convidados e parcerias com universidades para acelerar provas de conceito. "
            "As primeiras chamadas selecionam projetos de atendimento ao cliente, automação de marketing e análise de dados em linguagem natural.\n\n"
            "Segundo a coordenação, o objetivo é criar casos de uso com sotaque local, evitando dependência total de modelos estrangeiros. "
            "O laboratório também oferecerá workshops abertos para estudantes interessados em IA e ética digital."
        ),
        "imagem": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "titulo": "Economia: Exportações do polo farmacoquímico crescem 12%",
        "categoria": "Economia",
        "resumo": "Empresas relatam novos contratos na América Latina e investimentos em P&D.",
        "conteudo": (
            "O polo farmacoquímico do estado encerrou o trimestre com alta de 12% nas exportações, puxada por medicamentos genéricos e insumos hospitalares. "
            "Empresas instaladas em Goiana e Cabo de Santo Agostinho destacam o câmbio favorável e a retomada de licitações internacionais como motores do crescimento. "
            "O setor prevê contratar mais técnicos e ampliar laboratórios de pesquisa.\n\n"
            "Especialistas alertam, porém, que a competitividade depende de políticas de inovação de longo prazo. "
            "Sem financiamento consistente e desburocratização, a indústria pode perder espaço para gigantes asiáticos."
        ),
        "imagem": "https://images.unsplash.com/photo-1582719478171-2f2df1d935ef?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "titulo": "Náutico aposta na base para reconstrução em 2026",
        "categoria": "Esportes",
        "resumo": "Clube reformula elenco com pratas da casa e metas de acesso no médio prazo.",
        "conteudo": (
            "Depois de uma temporada instável, o Náutico anunciou um plano de reconstrução centrado na categoria de base. "
            "Seis atletas do sub-20 foram promovidos ao time principal, e a comissão técnica prepara intercâmbio com clubes parceiros para dar rodagem ao grupo. "
            "O orçamento será controlado e priorizará infraestrutura e análise de desempenho.\n\n"
            "A diretoria também promete reabrir o diálogo com torcedores sobre o futuro dos Aflitos. "
            "A ideia é modernizar o estádio em fases, sem comprometer as finanças, e tornar o ambiente mais acolhedor para famílias."
        ),
        "imagem": "https://images.unsplash.com/photo-1521417531039-55a636d4765d?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "titulo": "Reforma tributária: o que muda para os municípios do Agreste",
        "categoria": "Política",
        "resumo": "Especialistas explicam impacto do IVA dual e a redistribuição do Fundo de Participação.",
        "conteudo": (
            "Prefeitos do Agreste participaram de um seminário para entender os efeitos práticos da reforma tributária aprovada no Congresso. "
            "A principal dúvida é como o novo imposto sobre valor agregado será dividido e de que forma os fundos compensatórios vão chegar às cidades menores. "
            "Tributaristas defendem que municípios se organizem em consórcios para ganhar escala na cobrança e na fiscalização.\n\n"
            "Também foi debatida a transição dos benefícios fiscais para indústrias instaladas na região. "
            "Os gestores buscam segurança jurídica para manter empregos sem ferir as novas regras nacionais."
        ),
        "imagem": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "titulo": "Manguebeat faz 30 anos e inspira novas bandas independentes",
        "categoria": "Cultura",
        "resumo": "Coletivos se reúnem no Recife Antigo para homenagear Chico Science e Nação Zumbi.",
        "conteudo": (
            "Três décadas após o lançamento de Da Lama ao Caos, o manguebeat segue influenciando artistas de várias cenas. "
            "Bandas independentes organizaram uma maratona de shows no Recife Antigo, misturando alfaias, riffs pesados e letras sobre a cidade. "
            "Além dos palcos, houve debates sobre sustentabilidade na música e oficinas de produção para jovens músicos.\n\n"
            "Produtores culturais avaliam que o movimento continua vivo porque se reinventa com tecnologia e colaboração. "
            "Para os fãs, é a prova de que identidade regional e inovação podem caminhar juntas."
        ),
        "imagem": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "titulo": "Transnordestina retoma obras em trecho pernambucano",
        "categoria": "Pernambuco",
        "resumo": "Novo cronograma prevê entrega parcial até o final do próximo ano.",
        "conteudo": (
            "Após meses de negociação com a União, a concessionária da Transnordestina retomou as obras no trecho que corta o Sertão pernambucano. "
            "Máquinas voltaram a operar entre Salgueiro e Trindade, com prioridade para pontes e túneis que ficaram parados. "
            "Produtores rurais comemoram a perspectiva de reduzir custos logísticos e ampliar o escoamento de grãos.\n\n"
            "O governo do estado acompanha o cronograma e prometeu montar grupos de trabalho para garantir licenciamento ambiental e segurança dos canteiros. "
            "Comunidades ribeirinhas cobram medidas para evitar impactos nas fontes de água da região."
        ),
        "imagem": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "titulo": "Opinião: A inteligência artificial precisa de sotaque local",
        "categoria": "Opinião",
        "resumo": "Modelos globais ignoram contextos regionais e isso afeta sotaques, gírias e serviços públicos.",
        "conteudo": (
            "Ferramentas de IA generativa costumam ser treinadas em bases de dados que pouco refletem a diversidade linguística brasileira. "
            "Isso aparece em respostas que desconsideram sotaques, gírias e referências culturais de Pernambuco. "
            "Sem customização, sistemas de atendimento automatizado acabam reforçando desigualdades de acesso.\n\n"
            "A solução passa por incentivar datasets locais e parcerias entre governo, universidades e empresas. "
            "Quando a tecnologia respeita o contexto, ela se torna mais inclusiva e útil para serviços públicos e privados."
        ),
        "imagem": "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "titulo": "Surfistas disputam etapa histórica em Fernando de Noronha",
        "categoria": "Esportes",
        "resumo": "Ondas de mais de dois metros atraem atletas do circuito brasileiro e internacional.",
        "conteudo": (
            "Fernando de Noronha recebe uma etapa especial do circuito brasileiro de surfe com presença de atletas internacionais. "
            "O swell previsto para a semana promete ondas de mais de dois metros, cenário perfeito para manobras de alto nível. "
            "A organização montou estrutura reduzida para preservar o parque marinho e incentivar práticas sustentáveis.\n\n"
            "Moradores participam como voluntários e ofereceram trilhas guiadas para visitantes. "
            "Além do esporte, o evento busca reforçar a importância de manter a ilha protegida do turismo predatório."
        ),
        "imagem": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "titulo": "Rede estadual de saúde expande atendimento por telemedicina",
        "categoria": "Pernambuco",
        "resumo": "Hospitais regionais ganham salas equipadas e agenda para especialidades de alta demanda.",
        "conteudo": (
            "A Secretaria de Saúde inaugurou novas salas de telemedicina em hospitais do Agreste e do Sertão. "
            "Com câmeras de alta definição e conectividade dedicada, pacientes conseguem consultas com especialistas do Recife sem precisar viajar. "
            "A meta é reduzir filas de cardiologia, neurologia e pediatria nos próximos meses.\n\n"
            "Gestores informaram que os dados serão integrados ao prontuário eletrônico estadual, permitindo acompanhamento contínuo. "
            "Profissionais receberam treinamento para lidar com a tecnologia e garantir privacidade nas videochamadas."
        ),
        "imagem": "https://images.unsplash.com/photo-1582719478145-3b1aecea0bdf?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "titulo": "Mostra literária do Sertão celebra escritoras nordestinas",
        "categoria": "Cultura",
        "resumo": "Evento reúne clubes de leitura, oficinas de cordel e debates sobre representatividade.",
        "conteudo": (
            "A primeira edição da Mostra Literária do Sertão reuniu autoras de vários estados do Nordeste em Petrolina. "
            "Além dos lançamentos de livros, o público participou de rodas de conversa sobre protagonismo feminino e oficinas de literatura de cordel. "
            "Bibliotecas comunitárias montaram estandes para arrecadar livros e incentivar a leitura entre crianças.\n\n"
            "Editoras independentes relataram aumento nas vendas durante a feira e planejam ampliar a circulação das obras em escolas públicas. "
            "Para os organizadores, o evento mostrou que o interior tem público e produção literária vigorosa."
        ),
        "imagem": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "titulo": "Conselho de transparência discute prioridades para 2026",
        "categoria": "Política",
        "resumo": "Reunião definiu cronograma para portal de dados abertos e auditorias cidadãs.",
        "conteudo": (
            "O conselho estadual de transparência realizou a primeira reunião do ano e traçou metas para ampliar o acesso a dados públicos. "
            "Entre as prioridades estão a publicação de contratos de obras em formato aberto, indicadores de educação e relatórios ambientais detalhados. "
            "Organizações da sociedade civil pediram canais claros para denúncias de mau uso de recursos.\n\n"
            "Os conselheiros querem que cada secretaria apresente um plano trimestral de abertura de dados e que a população possa acompanhar a execução. "
            "A ideia é que as auditorias cidadãs sejam incorporadas ao processo de avaliação das políticas públicas."
        ),
        "imagem": "https://images.unsplash.com/photo-1503389152951-9f343605f61e?auto=format&fit=crop&w=1200&q=80",
    },
]


class Command(BaseCommand):
    help = "Popula o banco de produção com artigos de exemplo."

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

        for idx, item in enumerate(PROD_ARTICLES):
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

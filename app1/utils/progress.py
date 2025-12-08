from app1.models import Progresso


FLAG_LIBRARY = [
    {"slug": "usa", "nome": "Estados Unidos", "imagem": "app1/assets/flag-usa.svg"},
    {"slug": "pernambuco", "nome": "Pernambuco", "imagem": "app1/assets/flag-pernambuco.svg"},
    {"slug": "brasil", "nome": "Brasil", "imagem": "app1/assets/flag-brazil.svg"},
]


def _contar_artigos_lidos(request):
    if request.user.is_authenticated:
        return Progresso.objects.filter(user=request.user, completado=True).count()
    return len(request.session.get("artigos_lidos", []))


def montar_progresso_bandeiras(request):
    total_lidos = _contar_artigos_lidos(request)
    total_flags = len(FLAG_LIBRARY)

    if total_flags == 0:
        return {
            "total_lidos": total_lidos,
            "percent": 0,
            "faltam": 10,
            "restante_percent": 100,
            "flag_atual_nome": "",
            "imagem_atual": "",
            "grid": [],
        }

    flag_index = min(total_lidos // 10, total_flags - 1)
    lidos_na_flag = min(total_lidos - flag_index * 10, 10)
    percent_atual = lidos_na_flag * 10
    faltam_atual = max(0, 10 - lidos_na_flag)

    grid = []
    for idx, flag in enumerate(FLAG_LIBRARY):
        if idx < flag_index:
            status = "complete"
            percent = 100
            faltam = 0
        elif idx == flag_index:
            status = "progress"
            percent = percent_atual if total_lidos < (idx + 1) * 10 or idx == total_flags - 1 else 100
            faltam = faltam_atual
        else:
            status = "locked"
            percent = 0
            faltam = 10

        grid.append(
            {
                "nome": flag["nome"],
                "imagem": flag["imagem"],
                "status": status,
                "percent": percent,
                "faltam": faltam,
                "restante_percent": max(0, 100 - percent),
            }
        )

    return {
        "total_lidos": total_lidos,
        "percent": percent_atual,
        "faltam": faltam_atual,
        "restante_percent": max(0, 100 - percent_atual),
        "flag_atual_nome": FLAG_LIBRARY[flag_index]["nome"],
        "imagem_atual": FLAG_LIBRARY[flag_index]["imagem"],
        "grid": grid,
    }

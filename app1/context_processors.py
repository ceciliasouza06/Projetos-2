from .utils.progress import montar_progresso_bandeiras


def flag_progress(request):
    return {"flag_progress_header": montar_progresso_bandeiras(request)}

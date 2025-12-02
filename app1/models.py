from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Artigos(models.Model):
    titulo = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    resumo = models.TextField(blank=True, default="")
    imagem = models.URLField(max_length=500, blank=True, null=True)
    conteudo = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)
    favoritos = models.ManyToManyField(User, related_name='artigos_favoritos', blank=True)

    def __str__(self):
        return self.titulo

class Bullets(models.Model):
    artigo=models.ForeignKey(Artigos, on_delete=models.CASCADE, related_name="bullets")
    bullets=models.TextField()
    def __str__(self):
        return f"Bullets for {self.artigo.titulo}"


class Progresso( models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="reading_progress")
    artigo= models.ForeignKey(Artigos, on_delete=models.CASCADE,related_name="read_by_users")
    completado=models.BooleanField(default=False)
    date=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "artigo")# evita a duplicacao
    
    def __str__(self):
        if self.completado:
            status = "Completo"
        else:
            status = "Em progresso"
        return f"{self.user.username} - {self.artigo.title} ({status})"


class Progresso_diario(models.Model):
    visitante = models.CharField(max_length=100, null=True, blank=True)
    data = models.DateField(auto_now_add=True)
    artigos_lidos = models.IntegerField(default=0)
    class Meta:
        unique_together = ("visitante", "data")
    def __str__(self):
        return f"{self.visitante} - {self.data} - {self.artigos_lidos} artigos lidos"

    
    

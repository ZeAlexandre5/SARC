from .models import Notificacao

def notificacoes_pendentes(request):
    if request.user.is_authenticated:
        usuario = request.user
        
        if usuario.tipo_usuario == 'bolsista':
            # Para o bolsista, a bolinha aparece se existirem mensagens de alunos SEM resposta
            tem_novas = Notificacao.objects.filter(resposta__isnull=True).exists()
        else:
            # Para o aluno/professor, a bolinha aparece APENAS se houver resposta da administração que ele AINDA NÃO LEU
            tem_novas = Notificacao.objects.filter(remetente=usuario, resposta__isnull=False, lida=False).exists()
        
        return {'tem_notificacoes_novas': tem_novas}
        
    return {'tem_notificacoes_novas': False}
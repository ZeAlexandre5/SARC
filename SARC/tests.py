from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Projeto, Usuario


class ProjetosViewsTests(TestCase):
    def setUp(self):
        self.autor = Usuario.objects.create_user(
            matricula='20260001', email='autor@example.com', password='senha-segura', nome='Autor'
        )
        self.participante = Usuario.objects.create_user(
            matricula='20260002', email='participante@example.com', password='senha-segura', nome='Participante'
        )

    def test_cria_projeto_e_inclui_autor_e_participante(self):
        self.client.force_login(self.autor)
        resposta = self.client.post(reverse('novo_projeto'), {
            'titulo': 'Projeto de teste',
            'descricao': 'Descrição do projeto',
            'data_inicio': date.today().isoformat(),
            'data_limite': date.today().isoformat(),
            'participantes': [self.participante.pk],
        })

        projeto = Projeto.objects.get(titulo='Projeto de teste')
        self.assertRedirects(resposta, reverse('detalhe_projeto', args=[projeto.id_projeto]))
        self.assertCountEqual(projeto.participantes.all(), [self.autor, self.participante])
        self.assertContains(self.client.get(reverse('projetos')), 'Projeto de teste')
        self.assertContains(self.client.get(reverse('detalhe_projeto', args=[projeto.id_projeto])), 'Anotações')

    def test_participante_pode_anotar_e_enviar_arquivo(self):
        projeto = Projeto.objects.create(
            titulo='Projeto', descricao='Descrição', data_inicio=date.today(), data_limite=date.today(), criado_por=self.autor
        )
        projeto.participantes.add(self.autor, self.participante)
        self.client.force_login(self.participante)
        url = reverse('detalhe_projeto', args=[projeto.id_projeto])

        resposta_anotacao = self.client.post(url, {'acao': 'anotar', 'conteudo': 'Primeira atualização'})
        resposta_arquivo = self.client.post(url, {
            'acao': 'enviar_arquivo',
            'arquivo': SimpleUploadedFile('rascunho.txt', b'conteudo'),
        })

        self.assertEqual(resposta_anotacao.status_code, 302)
        self.assertEqual(resposta_arquivo.status_code, 302)
        self.assertEqual(projeto.anotacoes.count(), 1)
        self.assertEqual(projeto.arquivos.count(), 1)

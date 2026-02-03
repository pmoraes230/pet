# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notificacao, Consulta, Mensagem

@receiver(post_save, sender=Consulta)
def notificar_nova_consulta(sender, instance, created, **kwargs):
    if not created:
        return

    channel_layer = get_channel_layer()

    # Notificar veterinário
    if instance.veterinario:
        Notificacao.objects.create(
            veterinario=instance.veterinario,
            tipo='nova_consulta',
            mensagem=f"Nova solicitação: {instance.pet.nome} ({instance.pet.tutor.nome_tutor}) para {instance.tipo_de_consulta} em {instance.data_consulta.strftime('%d/%m/%Y às %H:%M')}"
        )

        # Enviar via WebSocket
        async_to_sync(channel_layer.group_send)(
            f"notif_vet_{instance.veterinario.id}",
            {
                "type": "nova.notificacao",
                "mensagem": f"Nova consulta pendente: {instance.pet.nome}",
                "tipo": "consulta",
                "consulta_id": str(instance.id),
            }
        )

@receiver(post_save, sender=Consulta)
def notificar_confirmacao_ou_rejeicao(sender, instance, **kwargs):
    if not kwargs.get('update_fields') or 'status' not in kwargs['update_fields']:
        return

    channel_layer = get_channel_layer()

    if instance.status == 'Confirmado':
        if instance.pet and instance.pet.tutor:
            Notificacao.objects.create(
                tutor=instance.pet.tutor,
                veterinario=instance.veterinario,  # obrigatório pelo seu model
                tipo='consulta_confirmada',
                mensagem=f"Consulta confirmada! {instance.pet.nome} - {instance.data_consulta.strftime('%d/%m/%Y às %H:%M')}"
            )

            async_to_sync(channel_layer.group_send)(
                f"notif_tutor_{instance.pet.tutor.id}",
                {
                    "type": "nova.notificacao",
                    "mensagem": f"Sua consulta foi confirmada!",
                    "tipo": "consulta_confirmada",
                    "consulta_id": str(instance.id),
                }
            )

    elif instance.status == 'Cancelado' and instance.tracker.previous('status') == 'Pendente':
        # Rejeitada
        if instance.pet and instance.pet.tutor:
            Notificacao.objects.create(
                tutor=instance.pet.tutor,
                veterinario=instance.veterinario,
                tipo='consulta_rejeitada',
                mensagem=f"Consulta para {instance.pet.nome} foi rejeitada."
            )

            async_to_sync(channel_layer.group_send)(
                f"notif_tutor_{instance.pet.tutor.id}",
                {
                    "type": "nova.notificacao",
                    "mensagem": f"Consulta rejeitada :(",
                    "tipo": "consulta_rejeitada",
                    "consulta_id": str(instance.id),
                }
            )


# Para mensagens (já estava quase ok)
@receiver(post_save, sender=Mensagem)
def notificar_nova_mensagem(sender, instance, created, **kwargs):
    if not created:
        return

    channel_layer = get_channel_layer()

    if instance.ENVIADO_POR == 'VETERINARIO':
        destinatario_group = f"notif_tutor_{instance.TUTOR_id}"
        mensagem_resumo = "Nova mensagem do veterinário"
    else:
        destinatario_group = f"notif_vet_{instance.VETERINARIO_id}"
        mensagem_resumo = "Nova mensagem do tutor"

    Notificacao.objects.create(
        tutor_id=instance.TUTOR_id if instance.ENVIADO_POR == 'VETERINARIO' else None,
        veterinario_id=instance.VETERINARIO_id if instance.ENVIADO_POR == 'TUTOR' else None,
        tipo='mensagem',
        mensagem=mensagem_resumo
    )

    async_to_sync(channel_layer.group_send)(
        destinatario_group,
        {
            "type": "nova.notificacao",
            "mensagem": mensagem_resumo,
            "tipo": "mensagem",
            "remetente": instance.ENVIADO_POR,
        }
    )
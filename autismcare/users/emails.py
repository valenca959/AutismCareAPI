from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def enviar_email_senha(user):
    """Envia o link para o usuário definir ou redefinir a senha."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    link = f"{settings.FRONTEND_URL}/definir-senha?uid={uid}&token={token}"
    send_mail(
        subject='AutismCare: defina sua senha',
        message=(
            f"Olá, {user.first_name or user.email}.\n\n"
            f"Para definir ou redefinir sua senha, acesse:\n{link}\n\n"
            "Se você não solicitou isso, ignore esta mensagem."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )

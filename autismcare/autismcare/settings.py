import os
import sys
from pathlib import Path
from datetime import timedelta

from cryptography.fernet import Fernet
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega o .env da raiz do repositório. Variáveis já definidas no ambiente têm prioridade.
load_dotenv(BASE_DIR.parent / '.env')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Defina DJANGO_SECRET_KEY no ambiente (nunca commite a chave).
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('Defina a variável de ambiente DJANGO_SECRET_KEY.')

# Chave Fernet para criptografar CPF e notas médicas. Gere com:
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FIELD_ENCRYPTION_KEY = os.environ.get('DJANGO_FIELD_ENCRYPTION_KEY')
if not FIELD_ENCRYPTION_KEY:
    raise ImproperlyConfigured('Defina a variável de ambiente DJANGO_FIELD_ENCRYPTION_KEY.')
try:
    Fernet(FIELD_ENCRYPTION_KEY.encode())
except ValueError:
    raise ImproperlyConfigured(
        'DJANGO_FIELD_ENCRYPTION_KEY não é uma chave Fernet válida (32 bytes em base64 urlsafe). '
        'Gere uma com: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
    )

# SECURITY WARNING: don't run with debug turned on in production!
# Para desenvolvimento local, defina DJANGO_DEBUG=True.
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() in ('1', 'true', 'yes')

# Lista separada por vírgulas, ex.: "api.exemplo.com,localhost"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if h.strip()]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'phonenumber_field',
    'corsheaders',
    'drf_spectacular',

    'users',
    'patients',
    'medical',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # CORS precisa vir antes do CommonMiddleware para responder ao preflight (OPTIONS).
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'autismcare.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'autismcare.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "users.AuthenticationUser"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Padrão seguro: só usuários autenticados. Cada view ainda define suas regras.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # Listagens paginadas: {"count", "next", "previous", "results"}.
    'DEFAULT_PAGINATION_CLASS': 'autismcare.pagination.PaginacaoPadrao',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # Limites das rotas de senha, por IP (cache local: use Redis se houver mais de um processo).
    'DEFAULT_THROTTLE_RATES': {
        'login': '10/minute',
        'password_reset': '5/hour',
        'password_confirm': '20/hour',
    },
}

# Nos testes, um hasher rápido: o PBKDF2 padrão deixa cada criação de usuário lenta.
# Nunca use MD5 fora dos testes.
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
    # A cada /token/refresh/ sai um refresh novo e o antigo vai para a blacklist.
    # No logout (/token/logout/) o refresh também vai para a blacklist e não renova mais.
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}

# Documentação da API: Swagger em /api/docs/ e ReDoc em /api/redoc/.
SPECTACULAR_SETTINGS = {
    'TITLE': 'AutismCare API',
    'DESCRIPTION': (
        'API para gestão de crianças atendidas, responsáveis, funcionários e prontuários. '
        'Faça login em POST /api/token/ e use o access no botão "Authorize" (Bearer).'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# CORS: origens do front-end que podem chamar a API pelo navegador.
# Lista separada por vírgulas, ex.: "http://localhost:3000,http://localhost:5173"
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get('DJANGO_CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    if o.strip()
]

# E-mail (link para definir ou redefinir a senha)
EMAIL_BACKEND = os.environ.get('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.environ.get('DJANGO_DEFAULT_FROM_EMAIL', 'nao-responder@autismcare.local')
# Endereço do front-end onde o usuário define a senha, ex.: https://app.exemplo.com
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

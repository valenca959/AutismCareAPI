# AutismCareAPI

API REST em Django e Django REST Framework para gestão de crianças atendidas, responsáveis, funcionários e registros de acompanhamento (anotações dos terapeutas). Por enquanto é apenas backend.

## Requisitos

- Python 3.10 ou superior

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `DJANGO_SECRET_KEY` | sim | Chave secreta do Django. O projeto não sobe sem ela. |
| `DJANGO_DEBUG` | não | `True` apenas em desenvolvimento. O padrão é `False`. |
| `DJANGO_ALLOWED_HOSTS` | não | Hosts permitidos, separados por vírgula (ex.: `localhost,127.0.0.1`). |
| `DJANGO_EMAIL_BACKEND` | não | Backend de email. O padrão imprime os emails no console. Em produção, use SMTP. |
| `DJANGO_DEFAULT_FROM_EMAIL` | não | Remetente dos emails. |
| `DJANGO_FIELD_ENCRYPTION_KEY` | sim | Chave Fernet que criptografa CPF e notas médicas. Não perca esta chave: sem ela os dados não são recuperados. |
| `FRONTEND_URL` | não | Endereço do front-end, usado no link de definir senha. |

Exemplo para desenvolvimento local (Linux/macOS):

```bash
export DJANGO_SECRET_KEY="troque-pela-sua-chave"
export DJANGO_DEBUG=True
export DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

Gere a chave secreta com: `python -c "import secrets; print(secrets.token_urlsafe(50))"`

Gere a chave de criptografia com: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

## Instalação

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r autismcare/requirements.txt
cd autismcare
python manage.py migrate
python manage.py createsuperuser   # pede email, senha e CPF
python manage.py runserver
```

## Autenticação

O login usa email e senha, com tokens JWT:

- `POST /api/token/` retorna `access` e `refresh`.
- `POST /api/token/refresh/` renova o `access`.
- Nas demais requisições, envie o cabeçalho `Authorization: Bearer <access>`.

Todos os endpoints exigem autenticação, exceto os de senha.

## Endpoints principais

Todos sob o prefixo `/api/`:

- `users/`, `addresses/`, `roles/`, `employees/`
- `parents/`, `children/`, `agendamentos/`
- `allergies/`, `medical-records/`, `medical-histories/`
- `acessos-medicos/` (somente coordenador, leitura)
- `password/reset/` e `password/reset/confirm/` (públicos)

## Papéis e permissões

Os cargos são definidos pelo `Role.name` do funcionário (`Employee`), em minúsculas:

| Quem | Pode ver | Pode alterar |
|---|---|---|
| **Coordenador / gerente** (ou superusuário) | Tudo | Tudo, inclusive funcionários, cargos e exclusões |
| **Recepcionista** | Todos os usuários, responsáveis e crianças. Não vê prontuário nem anotações. | Cria e edita usuários, responsáveis, crianças, endereços e agendamentos |
| **Terapeuta** | Próprio cadastro, crianças agendadas com ele, responsáveis dessas crianças, prontuário e anotações dessas crianças | Cria prontuário e anotações das crianças agendadas com ele. Edita ou apaga só as anotações que ele criou. |
| **Responsável** | Próprio cadastro e próprio endereço. Anotações de evolução dos próprios filhos. | Só o próprio cadastro |

Funcionários com status diferente de `active` não têm acesso especial.

Os agendamentos (`/api/agendamentos/`) definem quais crianças cada terapeuta pode ver. Sem um agendamento, o terapeuta não enxerga a criança.

## Senha

- Ao cadastrar um usuário, a API não aceita senha. O usuário recebe um email com um link para definir a senha.
- `POST /api/password/reset/` com `{"email": "..."}` reenvia o link. A resposta é a mesma existindo ou não o email.
- `POST /api/password/reset/confirm/` com `{"uid", "token", "new_password"}` define a senha. O token vale pelo tempo padrão do Django (3 dias).

## Auditoria de dados médicos

Toda leitura de prontuário e anotações gera um registro em `RegistroAcesso` (usuário, recurso, id, ação e horário). Só o coordenador consulta esse histórico em `/api/acessos-medicos/`.

## Testes

```bash
cd autismcare
python manage.py test users
```

Os testes precisam da variável `DJANGO_SECRET_KEY` definida.

## Dados pessoais (LGPD)

- CPF e notas médicas são criptografados no banco (Fernet). O CPF também tem um hash para unicidade.
- Não é possível apagar um usuário: a exclusão direta retorna 405. Para remover dados pessoais, use `POST /api/users/{id}/anonimizar/` (somente coordenador). A conta é desativada, o e-mail e o CPF são trocados por valores fictícios e o endereço é apagado. O prontuário e os agendamentos são mantidos, porque precisam ser guardados pelo prazo legal.
- Cada leitura de prontuário ou anotação gera um registro de acesso, consultável pelo coordenador em `/api/acessos-medicos/`.
- Os nomes das crianças não são anonimizados, porque identificam o prontuário.

## Limites de tentativas

Os endpoints de senha têm limite por IP: 5 pedidos por hora e 20 confirmações por hora. O limite usa o cache local do Django. Com mais de um processo, configure um cache compartilhado (ex.: Redis).

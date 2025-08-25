# � Connect Sync - Plataforma de Membership Tech

> **Plataforma completa de assinatura para profissionais de tecnologia**

Connect Sync é uma solução inovadora que conecta profissionais de tecnologia através de planos de membership exclusivos, oferecendo networking premium, aprendizado contínuo e oportunidades de crescimento na carreira.

## ✨ Funcionalidades

- 🎯 **Sistema de Planos**: Bronze, Prata e Ouro com benefícios escalonados
- 👤 **Self-Service**: Dashboard completo para membros gerenciarem suas contas
- � **Autenticação Segura**: Login/logout com proteção CSRF
- 📊 **Dashboard Dinâmico**: Estatísticas em tempo real e gestão de assinatura
- 💳 **Gestão de Pagamentos**: Troca de planos e cancelamento simplificado
- 📱 **Design Responsivo**: Interface moderna com Bootstrap 5

## 🛠️ Tecnologias

- **Backend**: Python 3.11+ | Django 5.2.5
- **Frontend**: Bootstrap 5.3.0 | Font Awesome 6.0.0
- **Banco**: SQLite3 (desenvolvimento)
- **Autenticação**: Sistema personalizado com sessões

## � Instalação Rápida

### 1️⃣ Clone o Repositório
```bash
git clone https://github.com/anacpp/projeto_final_senai.git
cd projeto_final_senai
```

### 2️⃣ Ambiente Virtual
```bash
# Linux/MacOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3️⃣ Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar Banco de Dados
```bash
# Executar migrações
python manage.py migrate

# Criar dados iniciais (IMPORTANTE!)
python setup_initial_data.py
```

### 5️⃣ Executar o Servidor
```bash
python manage.py runserver
```

### 6️⃣ Acessar a Aplicação
- **Site**: http://localhost:8000
- **Planos**: http://localhost:8000/planos/
- **Admin**: http://localhost:8000/admin/

## 🎯 Como Usar

### Para Visitantes
1. Acesse a **página inicial** para conhecer a plataforma
2. Navegue em **Planos** para ver as opções disponíveis
3. Clique em **"Escolher Plano"** para se cadastrar

### Para Membros
1. **Cadastre-se** escolhendo um plano
2. Faça **login** com email e senha
3. Acesse seu **dashboard** para:
   - ✏️ Editar perfil pessoal
   - 💳 Gerenciar assinatura
   - 🔄 Trocar de plano
   - ❌ Cancelar ou excluir conta

## � Planos Disponíveis

| Plano | Preço | Benefícios |
|-------|-------|------------|
| **🥉 Bronze** | R$ 29,90/mês | Networking básico, cupons de desconto |
| **🥈 Prata** | R$ 59,90/mês | Bronze + conteúdo gamificado |
| **🥇 Ouro** | R$ 99,90/mês | Prata + área VIP + eventos + mentoria |

## 🔧 Desenvolvimento

### Estrutura do Projeto
```
projeto_final_senai/
├── Connect_Sync/           # App principal
│   ├── models.py          # Modelos (Member, Plan, Subscription)
│   ├── views.py           # Views (auth + self-service)
│   ├── urls.py            # Rotas
│   └── templates/         # Templates HTML
├── primeiroProjeto/       # Configurações Django
├── setup_initial_data.py  # Script de dados iniciais
└── requirements.txt       # Dependências
```

### Comandos Úteis
```bash
# Resetar banco (desenvolvimento)
python manage.py flush
python setup_initial_data.py

# Criar superusuário para admin
python manage.py createsuperuser

# Rodar testes
python manage.py test
```

## ⚠️ Troubleshooting

### ❓ Site não mostra planos?
```bash
# Execute o script de dados iniciais
python setup_initial_data.py
```

### ❓ Erro de CSRF?
- Certifique-se que `CSRF_COOKIE_SECURE = False` em desenvolvimento
- Limpe cookies do navegador

### ❓ Erro de migração?
```bash
python manage.py makemigrations
python manage.py migrate
```

## 👥 Equipe de Desenvolvimento

Este projeto foi desenvolvido como **Projeto Integrador** do curso de Desenvolvimento Back-end do SENAI.

### 👨‍💻 Desenvolvedores
- **Ana Carla Cesar Pereira** - Desenvolvimento Full Stack
- **Felipe Amancio Marques** - Desenvolvimento Full Stack  
- **Marcello Augusto Mencalha Gomes** - Desenvolvimento Full Stack
- **Ricardo do Carmo da Silva** - Desenvolvimento Full Stack

## 📜 Licença

Este projeto é de **caráter acadêmico** e foi desenvolvido como Projeto Integrador do SENAI.

---

## 📞 Suporte

Se você tiver problemas para executar o projeto:

1. ✅ Certifique-se de ter executado `python setup_initial_data.py`
2. ✅ Verifique se o ambiente virtual está ativo
3. ✅ Confirme que as dependências foram instaladas


---

**⭐ Se este projeto te ajudou, considere dar uma estrela no repositório!**


# 🔐 Gestor de Senhas Seguras

Sistema desenvolvido como projeto acadêmico para gerenciar senhas de forma segura. O sistema permite o cadastro de usuários, login, geração de senhas fortes, armazenamento criptografado e exportação das senhas salvas. A interface é moderna, com suporte a modo escuro (dark mode), responsiva e intuitiva.

---

## 🚀 Funcionalidades

- Cadastro e autenticação de usuários (com hash seguro)
- Armazenamento seguro com criptografia Fernet
- Geração de senhas seguras com um clique
- Exportação das senhas salvas em CSV
- Interface moderna com CSS Grid e modo escuro
- Botões de copiar senha para facilitar o uso
- Mensagens de erro e sucesso com feedback visual

---

## 📁 Estrutura do Projeto

```
gestor_senhas/
│
├── app.py                      # Backend principal (Flask)
├──database.db                  # Banco de dados SQLite
├── chave.key                   # Chave de criptografia gerada dinamicamente
│
├── templates/                  # Arquivos HTML (frontend)
│   ├── index.html
│   ├── cadastro.html
│   ├── login.html
│   ├── dashboard.html
│   └── gerar_senha.html
│
├── static/
│   ├── estilo.css              # Estilos globais com suporte a dark mode e CSS Grid
│   └── tema.js                 # DOM JS para alternância de tema
└── README.md                   # Documentação
```

---

## 📦 Dependências

Instale as dependências com:

```bash
pip install flask bcrypt cryptography
```

**Principais pacotes:**

- `Flask`: Framework web em Python.
- `bcrypt`: Para criptografia de senhas de usuário (hash seguro).
- `cryptography`: Para criptografia simétrica das senhas salvas.

---

## 🧠 Tecnologias Utilizadas

### ✅ Python (Flask)
- Backend simples, organizado e com rotas bem definidas.
- Modularização de funções como login, dashboard, exportação, etc.

### ✅ HTML5 + CSS3 + JavaScript (DOM)
- Interface responsiva e acessível.
- Manipulação de eventos com `DOM`:
  - Alternância do tema (dark/light)
  - Geração e cópia de senha
  - Validação em tempo real (confirmação de senha, força da senha)
- Código desacoplado com `tema.js`.

### ✅ CSS Grid
- Layouts das telas organizados com **CSS Grid e Flexbox**.
- Layout adaptável a telas menores com media queries.

### ✅ Segurança
- As senhas dos usuários são armazenadas com `bcrypt` (não reversível).
- As senhas salvas (por plataforma) são criptografadas com `Fernet` (chave simétrica).
- A chave é salva em arquivo `chave.key` e carregada automaticamente.

### ✅ SQLite
- Facil implementação e visualização das tabelas criadas
- Suporte nativo no python
- Não precisa de configuração
- Arquivo unico (ótimo para aplicações pequenas como essa)
---

## 🌓 Dark Mode

- Suporte ao modo escuro com persistência via `localStorage`.
- Alternância de tema por botão com ícone intuitivo.
- Variáveis CSS (`--cor-primaria`, `--cor-texto`, etc.) facilitam a transição entre temas.

---

## 📋 Como executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/doppller/https---github.com-doppller-gestor_senha
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o projeto:
   ```bash
   python app.py
   ```
---

## ✅ Sugestões Finais

Este projeto é ideal para aprendizado e demonstração de boas práticas em:
- Desenvolvimento seguro
- Design moderno com CSS
- Uso de Flask de forma simples e eficiente
- Estrutura organizada e escalável

---

**Desenvolvido com 💙 para fins acadêmicos.**

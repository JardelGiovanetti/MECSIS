# MECSIS
Sistema para Oficina Mecânica
Aplicativo desktop em Python, para gerenciar clientes, veiculos, equipe e ordens de servico de uma oficina. O foco e oferecer experiencia pratica: tooltips em todos os campos, mensagens orientativas, atalhos no dashboard e central de ajuda integrada.

## Estrutura do projeto

```
src/
  app.py                     # ponto de entrada do aplicativo
  mecsis/
    assets/mecsis.ico        # icone do executavel e das janelas
    database/schema.sql      # definicao da base SQLite
    database/connection.py   # inicializacao e acesso ao banco embarcado
    services/                # regras de negocio/CRUD
    ui/                      # componentes e telas PySide6
    utils/config.py          # localizacao de arquivos e diretorios em tempo de execucao
dist/
  MEC-SIS.exe                # executavel gerado pelo PyInstaller
```

## Pre-requisitos

- Python 3.11+
- Pip para instalar dependencias (`pip install -r requirements.txt`)
- Windows 10/11 para executar o `.exe`

O banco de dados agora e **SQLite** e fica totalmente offline no arquivo `data/mecsis.db` (criado automaticamente ao iniciar o sistema). Nenhuma configuracao manual e necessaria.

## Executar em modo desenvolvimento

```bash
pip install -r requirements.txt
python src/app.py
```

Credenciais padrao: usuario `123`, senha `123`. Troque a senha diretamente no sistema apos o primeiro login (menu Usuario  Alterar senha, quando disponivel) ou altere pelo menu Alterar senha apos acessar.

## Gerar o executavel

Um build recente esta em `dist/MEC-SIS.exe`. Para gerar novamente:

```powershell
pyinstaller --noconsole --onefile --name "MEC-SIS" ^
  --icon "src\mecsis\assets\mecsis.ico" ^
  --add-data "src\mecsis\database\schema.sql;mecsis/database" ^
  --add-data "src\mecsis\assets\mecsis.ico;mecsis/assets" ^
  --hidden-import _cffi_backend src/app.py
```

O PyInstaller empacota o schema do banco e o icone. Na primeira execucao o aplicativo cria `data/mecsis.db` ao lado do `.exe` e popula a estrutura automaticamente.

### Distribuicao

- Entregue apenas o `MEC-SIS.exe`. O banco sera criado localmente, zero configuracao.
- Para resetar o banco, apague a pasta `data/` e execute novamente.

## Recursos implementados

- Autenticacao com Bcrypt e perfis (admin/manager/staff).
- CRUD completo de clientes, colaboradores, veiculos, marcas, modelos e servicos.
- Ordens de servico com itens, equipe alocada, calculo automatico de mao de obra/pecas/descontos e controle de status.
- Dashboard com indicadores, atalhos rapidos e calendario de entregas.
- Tooltips, mensagens contextuais e central de ajuda acessivel em todas as telas.

- Interface clara inspirada em UI/UX atuais, com navega??o lateral, status hints e tooltips em todas as telas.
- ?rea prefer?ncias permite atualizar usu?rio de login e senha sem acessar o banco.

## Sobre assinatura digital

O executavel nao e assinado. Para remover alertas do SmartScreen e necessario adquirir um certificado de assinatura de codigo (Code Signing) de uma Autoridade Certificadora e assinar o binario com `signtool.exe`. E possivel usar um certificado autoassinado apenas para testes internos, mas o Windows continuara exibindo avisos de seguranca.

## Dicas rapidas

- O icone e o banco sao resolvidos dinamicamente por `mecsis.utils.config`; mantenha a estrutura de pastas ao recompilar.
- Execute `python -m compileall src` para validar sintaxe antes de gerar uma nova build.
- Caso o `.exe` nao abra, verifique permissoes de escrita na pasta (o SQLite precisa criar `data/mecsis.db`).

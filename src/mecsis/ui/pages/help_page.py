from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTextBrowser

from ..components.base_page import BasePage


class HelpPage(BasePage):
    def __init__(self, on_help_requested) -> None:
        super().__init__("Central de Ajuda", on_help_requested)
        self._build_content()

    def _build_content(self) -> None:
        layout = self.content_layout

        intro = QLabel(
            "Aqui estao as principais orientacoes para utilizar o MEC-SIS com eficiencia. "
            "Use os atalhos ao lado esquerdo para navegar rapidamente entre os cadastros e ordens."
        )
        intro.setWordWrap(True)
        intro.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        intro.setToolTip("Contextualiza como utilizar esta tela de ajuda.")
        layout.addWidget(intro)

        help_text = QTextBrowser()
        help_text.setOpenExternalLinks(True)
        help_text.setToolTip("Manual resumido do sistema MEC-SIS.")
        help_text.setMarkdown(
            """
## Fluxo geral

1. **Faca login** com seu usuario e senha.
2. **Cadastre clientes, veiculos e colaboradores** antes de abrir uma Ordem de Servico (OS).
3. Acesse **OS** para abrir um novo atendimento, incluir itens de servicos/pecas e definir responsaveis.
4. Utilize o **calendario** no painel inicial para revisar OS com entrega programada.

## Dicas rapidas

- Passe o mouse sobre botoes e campos para visualizar dicas contextualizadas.
- Utilize o campo de busca em cada listagem para localizar registros de forma instantanea.
- No cadastro de OS, lembre-se de informar a mao de obra e revisar os itens lancados antes de salvar.

## Suporte interno

Em caso de duvidas, contacte a equipe administrativa ou o gestor tecnico da oficina.
            """
        )
        layout.addWidget(help_text)

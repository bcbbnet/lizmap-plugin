__copyright__ = 'Copyright 2023, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'

from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox

from lizmap.qgis_plugin_tools.tools.resources import load_ui

FORM_CLASS = load_ui('ui_lizmap_popup.ui')


class LizmapPopupDialog(QDialog, FORM_CLASS):

    def __init__(self, style_sheet, content):
        QDialog.__init__(self)
        self.setupUi(self)

        accept_button = self.bbConfigurePopup.button(QDialogButtonBox.Ok)
        accept_button.clicked.connect(self.accept)
        cancel_button = self.bbConfigurePopup.button(QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(self.reject)

        self.groupBox.setStyleSheet(style_sheet)
        self.groupBox_2.setStyleSheet(style_sheet)
        self.txtPopup.textChanged.connect(self.update_html)

        self.txtPopup.setText(content)
        self.htmlPopup.setHtml(content)

    def update_html(self):
        content = self.txtPopup.text()
        self.htmlPopup.setHtml(content)

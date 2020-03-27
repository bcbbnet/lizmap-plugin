"""Base class for the edition dialog."""

import re

from collections import OrderedDict

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QPlainTextEdit,
)
from qgis.core import QgsProject

from lizmap import DEFAULT_LWC_VERSION
from lizmap.qt_style_sheets import NEW_FEATURE
from lizmap.definitions.definitions import LwcVersions
from lizmap.definitions.base import InputType
from lizmap.qgis_plugin_tools.tools.i18n import tr

__copyright__ = 'Copyright 2020, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'
__revision__ = '$Format:%H$'


class BaseEditionDialog(QDialog):

    def __init__(self, parent=None, unicity=None):
        super().__init__(parent)
        self.config = None
        self.unicity = unicity
        self.lwc_versions = OrderedDict()
        self.lwc_versions[LwcVersions.Lizmap_3_1] = []
        self.lwc_versions[LwcVersions.Lizmap_3_2] = []
        self.lwc_versions[LwcVersions.Lizmap_3_3] = []
        self.lwc_versions[LwcVersions.Lizmap_3_4] = []

    def setup_ui(self):
        self.button_box.button(QDialogButtonBox.Cancel).clicked.connect(self.close)
        self.button_box.button(QDialogButtonBox.Ok).clicked.connect(self.accept)
        self.error.setVisible(False)

        for layer_config in self.config.layer_config.values():
            widget = layer_config.get('widget')

            tooltip = layer_config.get('tooltip')
            if tooltip:
                label = layer_config.get('label')
                if label:
                    label.setToolTip(tooltip)
                if widget:
                    widget.setToolTip(tooltip)

            if layer_config['type'] == InputType.List:
                if widget is not None:
                    items = layer_config.get('items')
                    if items:
                        for item in items:
                            icon = item.value.get('icon')
                            if icon:
                                widget.addItem(QIcon(icon), item.value['label'], item.value['data'])
                            else:
                                widget.addItem(item.value['label'], item.value['data'])
                        default = layer_config.get('default')
                        if default:
                            index = widget.findData(default.value['data'])
                            widget.setCurrentIndex(index)

            if layer_config['type'] == InputType.CheckBox:
                if widget is not None:
                    widget.setChecked(layer_config['default'])

            if layer_config['type'] == InputType.SpinBox:
                if widget is not None:
                    unit = layer_config.get('unit')
                    if unit:
                        widget.setSuffix(unit)

                    default = layer_config.get('default')
                    if unit:
                        widget.setValue(default)

            if layer_config['type'] == InputType.Color:
                if widget is not None:
                    if layer_config['default'] == '':
                        widget.setShowNull(True)
                        widget.setToNull()
                    else:
                        widget.setDefaultColor(QColor(layer_config['default']))
                        widget.setToDefaultColor()

        self.version_lwc()

    def version_lwc(self):
        current_version = QSettings().value('lizmap/lizmap_web_client_version', DEFAULT_LWC_VERSION.value, str)
        current_version = LwcVersions(current_version)
        found = False

        for lwc_version, items in self.lwc_versions.items():
            if found:
                for item in items:
                    item.setStyleSheet(NEW_FEATURE)

            else:
                for item in items:
                    item.setStyleSheet('')

            if lwc_version == current_version:
                found = True

        found = False
        for lwc_version in self.lwc_versions.keys():
            if found:
                for layer_config in self.config.layer_config.values():
                    version = layer_config.get('version')
                    if version == lwc_version:
                        label = layer_config.get('label')
                        if label:
                            label.setStyleSheet(NEW_FEATURE)
                        if layer_config['type'] == InputType.CheckBox:
                            layer_config.get('widget').setStyleSheet(NEW_FEATURE)
            else:
                for layer_config in self.config.layer_config.values():
                    version = layer_config.get('version')
                    if version == lwc_version:
                        label = layer_config.get('label')
                        if label:
                            label.setStyleSheet('')
                        if layer_config['type'] == InputType.CheckBox:
                            layer_config.get('widget').setStyleSheet('')

            if lwc_version == current_version:
                found = True

    def validate(self):
        if self.unicity:
            for key in self.unicity:
                for k, layer_config in self.config.layer_config.items():
                    if key == k:
                        if layer_config['type'] == InputType.Layer:
                            if layer_config['widget'].currentLayer().id() in self.unicity[key]:
                                msg = tr(
                                    'A duplicated "{}"="{}" is already in the table.'.format(
                                        key, layer_config['widget'].currentLayer().name()))
                                return msg
                        else:
                            raise Exception('InputType "{}" not implemented'.format(layer_config['type']))

        for k, layer_config in self.config.layer_config.items():
            if layer_config['type'] == InputType.Field:
                widget = layer_config.get('widget')

                if not widget:
                    # Dataviz does not have widget for Y, Z
                    continue

                if not widget.allowEmptyFieldName():
                    if widget.currentField() == '':
                        names = re.findall('.[^A-Z]*',  k)
                        names = [n.lower().replace('_', ' ') for n in names]
                        msg = tr('The field "{}" is mandatory.'.format(' '.join(names)))
                        return msg

        return None

    def accept(self):
        message = self.validate()
        if message:
            self.error.setVisible(True)
            self.error.setText(message)
        else:
            super().accept()

    def load_collection(self, value):
        """Load a collection to JSON."""
        # This function is implemented in child class.
        pass

    def save_collection(self) -> dict:
        """Save a collection into JSON."""
        # This function is implemented in child class.
        pass

    def primary_keys_collection(self) -> list:
        """List of unique keys in the collection."""
        # This function is implemented in child class.
        pass

    def load_form(self, data: OrderedDict) -> None:
        """A dictionary to load in the UI."""
        layer_properties = OrderedDict()
        for key, definition in self.config.layer_config.items():
            if definition.get('plural') is None:
                layer_properties[key] = definition

        for key, definition in layer_properties.items():
            value = data.get(key)

            if definition['type'] == InputType.Layer:
                layer = QgsProject.instance().mapLayer(value)
                definition['widget'].setLayer(layer)
            elif definition['type'] == InputType.Layers:
                definition['widget'].set_selection(value.split(','))
            elif definition['type'] == InputType.Field:
                definition['widget'].setField(value)
            elif definition['type'] == InputType.Fields:
                definition['widget'].set_selection(value.split(','))
            elif definition['type'] == InputType.CheckBox:
                definition['widget'].setChecked(value)
            elif definition['type'] == InputType.Color:
                color = QColor(value)
                if color.isValid():
                    definition['widget'].setDefaultColor(color)
                    definition['widget'].setColor(color)
                else:
                    definition['widget'].setToNull()
            elif definition['type'] == InputType.List:
                index = definition['widget'].findData(value)
                definition['widget'].setCurrentIndex(index)
            elif definition['type'] == InputType.SpinBox:
                definition['widget'].setValue(value)
            elif definition['type'] == InputType.Text:
                definition['widget'].setText(value)
            elif definition['type'] == InputType.MultiLine:
                widget = definition['widget']
                if isinstance(widget, QPlainTextEdit):
                    widget.setPlainText(value)
                else:
                    widget.setText(value)
            elif definition['type'] == InputType.Collection:
                self.load_collection(value)
            else:
                raise Exception('InputType "{}" not implemented'.format(definition['type']))

    def save_form(self) -> OrderedDict:
        """Save the UI in the dictionary with QGIS objects"""
        layer_properties = OrderedDict()
        for key, definition in self.config.layer_config.items():
            if definition.get('plural') is None:
                layer_properties[key] = definition

        data = OrderedDict()

        for key, definition in layer_properties.items():

            if definition['type'] == InputType.Layer:
                value = definition['widget'].currentLayer().id()
            elif definition['type'] == InputType.Layers:
                value = ','.join(definition['widget'].selection())
            elif definition['type'] == InputType.Field:
                value = definition['widget'].currentField()
            elif definition['type'] == InputType.Fields:
                value = ','.join(definition['widget'].selection())
            elif definition['type'] == InputType.Color:
                widget = definition['widget']
                if widget.isNull():
                    value = ''
                else:
                    value = widget.color().name()
            elif definition['type'] == InputType.CheckBox:
                value = definition['widget'].isChecked()
            elif definition['type'] == InputType.List:
                value = definition['widget'].currentData()
            elif definition['type'] == InputType.SpinBox:
                value = definition['widget'].value()
            elif definition['type'] == InputType.Text:
                value = definition['widget'].text().strip(' \t')
            elif definition['type'] == InputType.MultiLine:
                widget = definition['widget']
                if isinstance(widget, QPlainTextEdit):
                    value = definition['widget'].toPlainText()
                else:
                    value = definition['widget'].text()
                value = value.strip(' \t')
            elif definition['type'] == InputType.Collection:
                value = self.save_collection()
            else:
                raise Exception('InputType "{}" not implemented'.format(definition['type']))

            data[key] = value
        return data

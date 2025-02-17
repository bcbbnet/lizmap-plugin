"""Test table manager."""
from qgis.core import QgsProject, QgsVectorLayer
from qgis.PyQt.QtWidgets import QComboBox, QTableWidget, QTreeWidget
from qgis.testing import unittest

from lizmap.definitions.dataviz import DatavizDefinitions
from lizmap.drag_drop_dataviz_manager import DragDropDatavizManager
from lizmap.qgis_plugin_tools.tools.resources import plugin_test_data_path
from lizmap.table_manager.base import TableManager

__copyright__ = 'Copyright 2023, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'


class TestDragDropDataviz(unittest.TestCase):

    def test_read_cfg_DD_dataviz(self):
        """ Test to read the data from the CFG. """
        layer = QgsVectorLayer(plugin_test_data_path('lines.geojson'), 'lines', 'ogr')
        QgsProject.instance().addMapLayer(layer)
        self.assertTrue(layer.isValid())

        table = QTableWidget()
        definitions = DatavizDefinitions()

        table_manager = TableManager(
            None, definitions, None, table, None, None, None, None)

        tree_widget = QTreeWidget()
        combo = QComboBox()
        manager = DragDropDatavizManager(None, definitions, table, tree_widget, combo)
        self.assertEqual(0, manager.count_lines())

        plot_data = {
            '0': {
                'title': 'My graph',
                'type': 'box',
                'x_field': 'id',
                'aggregation': '',
                'y_field': 'name',
                'color': '#00aaff',
                'colorfield': '',
                'has_y2_field': 'True',
                'y2_field': 'name',
                'color2': '#ffaa00',
                'colorfield2': '',
                'popup_display_child_plot': 'False',
                'only_show_child': 'True',
                'layerId': layer.id(),
                'uuid': 'test_plot',
                'order': 0
            }
        }
        self.assertEqual(table_manager.table.rowCount(), 0)
        table_manager.from_json(plot_data)

        self.assertEqual(table_manager.table.rowCount(), 1)

        manager.load_dataviz_list_from_main_table()
        self.assertEqual(1, manager.combo_plots.count())

        # Data
        data = [
            {
                'type': 'container',
                'name': 'tab1',
                'content': [],
            },
            {
                'type': 'container',
                'name': 'tab2',
                'content': [
                    {
                        'type': 'plot',
                        '_name': 'plot name',
                        'uuid': 'test_plot',
                    },
                    {
                        'type': 'plot',
                        '_name': 'plot name',
                        'uuid': 'test_plot',
                    },
                    {
                        'type': 'container',
                        'name': 'container2.2',
                        'content': [
                            {
                                'type': 'plot',
                                '_name': 'plot name',
                                'uuid': 'test_plot',
                            },
                        ]
                    },
                ]
            }
        ]
        self.assertTrue(manager.load_tree_from_cfg(data))
        self.assertEqual(6, manager.count_lines())
        # app = QApplication([])
        # tree_widget.show()
        # sys.exit(app.exec_())
        self.assertListEqual(data, manager.to_json())


if __name__ == "__main__":
    from qgis.testing import start_app
    start_app()

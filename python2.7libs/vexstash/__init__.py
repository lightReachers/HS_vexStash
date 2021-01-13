from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtUiTools
import os
import json

import hou
import constant

def has_class(node):
    has_class = False
    _parm = None
    required_parm = ['class', 'bindclass']
    for parm in required_parm:
        class_parm = node.parm(parm)
        if class_parm:
            has_class = True
            _parm = parm
            break
    return has_class, _parm


class saveSnippet(QtWidgets.QDialog):
    def __init__(self, parm=None, parent=hou.qt.mainWindow()):
        super(saveSnippet, self).__init__(parent)

        self.setWindowTitle("HS_vexStash - Save vex snippet")
        self.setFixedWidth(700)
        self.setMinimumHeight(120)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)


        self.parm = parm
        self.local_vexStash = constant.get_vexstash_location()
        self.has_class = has_class(self.parm.node())[0]
        self.create_widget()
        self.add_layout()

        # self.get_savepath()

    def create_widget(self):
        self.class_label = QtWidgets.QLabel('Runs Over(class or bindclass) : ')
        self.class_node = QtWidgets.QComboBox()
        if self.has_class:
            self.class_node.addItems(constant.CLASS_LIST)
            # print((has_class(self.parm.node())[1]))
            current_class = self.parm.node().parm(has_class(self.parm.node())[1]).evalAsString()
            self.class_node.setCurrentText(current_class)
        else:
            self.class_node.addItem('- Not Applicable -')
            self.class_node.setEnabled(False)

        self.snippet_label = QtWidgets.QLabel('Enter name for your vex snippet : ')
        self.snippet_lineedit = QtWidgets.QLineEdit()
        self.ok_btn = QtWidgets.QPushButton('Save')

        self.ok_btn.clicked.connect(self.save_snippet)

    def add_layout(self):
        box_class = QtWidgets.QHBoxLayout()
        box_class.addWidget(self.class_label)
        box_class.addWidget(self.class_node)
        lay_linedit = QtWidgets.QHBoxLayout()
        lay_linedit.addWidget(self.snippet_label)
        lay_linedit.addWidget(self.snippet_lineedit)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(box_class)
        main_layout.addLayout(lay_linedit)
        main_layout.addWidget(self.ok_btn)
        self.layout().setContentsMargins(6, 6, 6, 6)

    def get_savepath(self):
        data = {}
        nodename = self.parm.node().type().nameComponents()[2]
        if self.class_node.currentText() != '- Not Applicable -':
            file_path = os.path.abspath(os.path.join(os.getenv('LOCAL_VEXSTASH'),
                                     nodename,
                                     self.class_node.currentText(),
                                     'vex_snippet.json'))
        else:
            file_path = os.path.abspath(os.path.join(os.getenv('LOCAL_VEXSTASH'),
                                     nodename,
                                     'vex_snippet.json'))
        if not os.path.isdir(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
            json_object = json.dumps(data, indent=4)

            # Writing to empty.json
            with open(file_path, "w") as outfile:
                outfile.write(json_object)
                outfile.close()
        return file_path

    def save_snippet(self):
        snippet_title = self.snippet_lineedit.text()
        vex_code = self.parm.evalAsString()
        snippet_file = self.get_savepath()

        with open(snippet_file, 'r') as f:
            data = json.load(f)
            data[snippet_title] = vex_code

        with open(snippet_file, "w") as outfile:
            json.dump(data, outfile, indent=4)
        self.close()
        self.deleteLater()


class snippetLoader(QtWidgets.QDialog):
    def __init__(self, parm=None, parent=hou.qt.mainWindow()):
        super(snippetLoader, self).__init__(parent)
        self.setWindowTitle("HS_vexStash - Load vex snippet")
        # self.setFixedWidth(700)
        # self.setMinimumHeight(120)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.parm = parm
        self.current_code = ''
        self.local_vexStash = constant.get_vexstash_location()
        self.has_class = has_class(self.parm.node())[0]
        self.init_ui()
        # self.create_widget()
        # self.add_layout()
        self.get_nodes()
        self.set_current_node()

    def init_ui(self):
        ui_file = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui/load.ui'))
        f = QtCore.QFile(ui_file)
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f)
        f.close()
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.ui)


        # signals
        self.ui.node_list.itemClicked.connect(self.get_class)
        self.ui.class_cb.activated.connect(self.get_snippet_names)
        self.ui.snippet_list.itemClicked.connect(self.get_snippet_code)
        self.ui.append_btn.clicked.connect(self.append_code)
        self.ui.replace_btn.clicked.connect(self.replace_code)

        self.ui.append_btn.setEnabled(False)
        self.ui.replace_btn.setEnabled(False)

    def set_current_node(self):
        init_node = self.parm.node().type().nameComponents()[2]
        if init_node in self.nodes:
            node_idx = self.ui.node_list.findItems(init_node, QtCore.Qt.MatchExactly)
            self.ui.node_list.setCurrentItem(node_idx[0])
            self.get_class()


    def get_nodes(self):
        self.nodes = os.listdir(self.local_vexStash)
        self.ui.node_list.addItems(self.nodes)

    def get_class(self):
        self.ui.class_cb.clear()
        self.ui.snippet_list.clear()
        self.ui.code.clear()
        self.ui.append_btn.setEnabled(False)
        self.ui.replace_btn.setEnabled(False)
        selected_node = self.ui.node_list.currentItem().text()
        node_root = os.path.abspath(os.path.join(self.local_vexStash, selected_node))
        node_root_items = os.listdir(node_root)
        if 'vex_snippet.json' in node_root_items:
            self.ui.class_cb.addItem('- Not Applicable -')
            self.ui.class_cb.setEnabled(False)

        else:
            self.ui.class_cb.setEnabled(True)
            self.ui.class_cb.addItems(node_root_items)
        self.get_snippet_names()

    def get_snippet_names(self):
        snippet_data = self.get_snippet_data()
        self.ui.snippet_list.clear()
        self.ui.code.clear()
        self.ui.append_btn.setEnabled(False)
        self.ui.replace_btn.setEnabled(False)
        self.ui.snippet_list.addItems(snippet_data.keys())

    def get_snippet_code(self):
        snippet_data = self.get_snippet_data()
        self.ui.code.clear()
        current_snippet_selection = self.ui.snippet_list.currentItem().text()
        self.current_code = snippet_data[current_snippet_selection]
        self.ui.code.setText(self.current_code)
        self.ui.append_btn.setEnabled(True)
        self.ui.replace_btn.setEnabled(True)

    def get_snippet_data(self):
        data = {}
        selected_node = self.ui.node_list.currentItem().text()
        selected_class = self.ui.class_cb.currentText()
        if selected_class == '- Not Applicable -':
            data_file = os.path.abspath(os.path.join(self.local_vexStash, selected_node, 'vex_snippet.json'))
        else:
            data_file = os.path.abspath(os.path.join(self.local_vexStash, selected_node, selected_class,
                                                     'vex_snippet.json'))
        with open(data_file, 'r') as f:
            data = json.load(f)
        return data

    def append_code(self):
        existing_code = self.parm.evalAsString()
        new_code = "\n".join([existing_code, '// code from Lib - vexStash <--------', self.current_code])
        self.parm.set(new_code)
        self.close()
        self.deleteLater()

    def replace_code(self):
        self.parm.set(self.current_code)
        self.close()
        self.deleteLater()
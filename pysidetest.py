import sys

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt, QMargins, QPoint, QRect, QSize
from PySide2.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QGridLayout,
    QLabel,
    QLayout,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QFrame,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from traits import TRAITS, get_trait_by_name


class FlowLayout(QLayout):
    """https://doc.qt.io/qtforpython/examples/example_widgets_layouts_flowlayout.html"""

    def __init__(self, parent=None):
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(QMargins(0, 0, 0, 0))

        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]

        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        size += QSize(
            2 * self.contentsMargins().top(), 2 * self.contentsMargins().top()
        )
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical
            )
            # space_x = spacing + layout_spacing_x
            space_x = 0
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()


class MainWindow(QMainWindow):
    def __init__(self, width=(342 * 4) + 72, height=900, maximize=False):
        super().__init__()

        self.availableTraits = list(TRAITS)
        self.selectedTraits = []

        self.setWindowTitle("Hunt: Showdown - Trait Presets")

        self.traitsScrollAreaWidget = QWidget()
        self.traitsLayout = FlowLayout(self.traitsScrollAreaWidget)

        self.buttonToTrait = {}
        self.traitNameToButton = {}

        for trait in self.availableTraits:
            name = trait["name"]
            pixmap = QtGui.QPixmap(f"img/{name}.png").scaledToWidth(342)

            button = QPushButton("")
            button.setStyleSheet("padding: 0; border: none;")
            button.setIcon(pixmap)
            button.setIconSize(pixmap.rect().size())
            button.clicked.connect(self.onTraitClicked)

            self.traitNameToButton[name] = button
            self.buttonToTrait[button] = trait

            self.traitsLayout.addWidget(button)

        self.scrollArea = QtWidgets.QScrollArea(self)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.traitsScrollAreaWidget)

        self.availableTraitsLayout = QVBoxLayout()
        self.availableTraitsLayout.addWidget(self.scrollArea)

        self.noTraitsSelectedYetLabel = QLabel("Please select some traits")
        self.noTraitsSelectedYetLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.noTraitsSelectedYetLabel.setMinimumHeight(120)

        self.selectedTraitsLayout = QVBoxLayout()
        self.selectedTraitsLayout.addWidget(self.noTraitsSelectedYetLabel)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.selectedTraitsLayout)
        self.mainLayout.addLayout(self.availableTraitsLayout)

        widget = QWidget()
        widget.setLayout(self.mainLayout)
        self.setCentralWidget(widget)

        if maximize:
            self.setWindowState(Qt.WindowMaximized)
        elif width and height:
            self.resize(width, height)

    def onTraitClicked(self, trait):
        button = self.sender()
        trait = self.buttonToTrait[button]

        if trait not in self.selectedTraits:
            self.selectedTraits.append(trait)

        self.updateUi()

    def updateUi(self):
        self._updateVisibleLabels()
        self._updateVisibleTraitButtons()

    def _updateVisibleLabels(self):
        self.noTraitsSelectedYetLabel.setVisible(len(self.selectedTraits) == 0)

    def _updateVisibleTraitButtons(self):
        for trait in self.availableTraits:
            button = self.traitNameToButton[trait["name"]]
            button.show()
        for trait in self.selectedTraits:
            button = self.traitNameToButton[trait["name"]]
            button.hide()


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec_()

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
    QHBoxLayout,
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
            # layout_spacing_x = style.layoutSpacing(
            #     QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal
            # )
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
    def __init__(
        self,
        equipTraitsCallback: callable,
        width=(342 * 4) + 72,
        height=900,
        maximize=False,
    ):
        super().__init__()

        self.equipTraitsCallback = equipTraitsCallback

        self.orderBy = "name"
        self.availableTraits = list(TRAITS)
        self.selectedTraits = []

        self.setWindowTitle("Hunt: Showdown - Trait Presets")

        self.availableTraitsScrollAreaWidget = QWidget()
        self.availableTraitsLayout = FlowLayout(self.availableTraitsScrollAreaWidget)

        self.selectedTraitsScrollAreaWidget = QWidget()
        self.selectedTraitsLayout = QHBoxLayout(self.selectedTraitsScrollAreaWidget)
        self.selectedTraitsLayout.setAlignment(QtCore.Qt.AlignLeft)

        # Lookups to map buttons to traits and vice versa.
        self.buttonToAvailableTrait = {}
        self.availableTraitNameToButton = {}

        self.buttonToSelectedTrait = {}
        self.selectedTraitNameToButton = {}

        for trait in sorted(self.availableTraits, key=lambda t: t[self.orderBy]):
            name = trait["name"]
            pixmap = QtGui.QPixmap(f"img/{name}.png").scaledToWidth(342)

            button = QPushButton("")
            button.setStyleSheet("padding: 0; border: none;")
            button.setToolTip("Select " + name)
            button.setIcon(pixmap)
            button.setIconSize(pixmap.rect().size())
            button.clicked.connect(self.onAvailableTraitClicked)

            self.availableTraitNameToButton[name] = button
            self.buttonToAvailableTrait[button] = trait

            self.availableTraitsLayout.addWidget(button)

        self.availableTraitsScrollArea = QtWidgets.QScrollArea(self)
        self.availableTraitsScrollArea.setFrameShape(QFrame.NoFrame)
        self.availableTraitsScrollArea.setWidgetResizable(True)
        self.availableTraitsScrollArea.setWidget(self.availableTraitsScrollAreaWidget)

        self.availableTraitsScrollableLayout = QVBoxLayout()
        self.availableTraitsScrollableLayout.addWidget(self.availableTraitsScrollArea)

        self.selectedTraitsScrollArea = QtWidgets.QScrollArea(self)
        self.selectedTraitsScrollArea.setFrameShape(QFrame.NoFrame)
        self.selectedTraitsScrollArea.setWidgetResizable(True)
        self.selectedTraitsScrollArea.setWidget(self.selectedTraitsScrollAreaWidget)

        self.selectedTraitsScrollableLayout = QHBoxLayout()
        self.selectedTraitsScrollableLayout.addWidget(self.selectedTraitsScrollArea)

        self.selectedTraitsLabel = QLabel(self._getSelectedTraitsLabelText())
        self.selectedTraitsLabel.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.equipSelectedTraitsButton = QPushButton("Equip in Hunt: Showdown")
        self.equipSelectedTraitsButton.setToolTip(
            "Make sure you are on the trait selection screen in game"
        )
        self.equipSelectedTraitsButton.setMinimumHeight(48)
        self.equipSelectedTraitsButton.setMaximumWidth(200)
        self.equipSelectedTraitsButton.clicked.connect(self.equipSelectedTraitsInGame)

        self.selectedTraitsHeaderLayout = QHBoxLayout()
        self.selectedTraitsHeaderLayout.addWidget(self.selectedTraitsLabel)
        self.selectedTraitsHeaderLayout.addWidget(self.equipSelectedTraitsButton)

        self.availableTraitsLabel = QLabel("Available Traits")
        self.availableTraitsLabel.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin-bottom: 16px;"
        )

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.selectedTraitsHeaderLayout)
        self.mainLayout.addLayout(self.selectedTraitsScrollableLayout, 1)
        self.mainLayout.addWidget(self.makeVerticalDivider())
        self.mainLayout.addWidget(self.availableTraitsLabel)
        self.mainLayout.addLayout(self.availableTraitsScrollableLayout, 4)

        self.updateUi()

        widget = QWidget()
        widget.setLayout(self.mainLayout)
        self.setCentralWidget(widget)

        if maximize:
            self.setWindowState(Qt.WindowMaximized)
        elif width and height:
            self.resize(width, height)

    def onAvailableTraitClicked(self, trait):
        button = self.sender()
        trait = self.buttonToAvailableTrait[button]
        if trait in self.selectedTraits:
            return

        self.selectedTraits.append(trait)

        name = trait["name"]
        pixmap = QtGui.QPixmap(f"img/{name}.png").scaledToWidth(342)

        button = QPushButton("")
        button.setStyleSheet("padding: 0; border: none;")
        button.setToolTip("Deselect " + name)
        button.setIcon(pixmap)
        button.setIconSize(pixmap.rect().size() / 1.33)
        button.clicked.connect(self.onSelectedTraitClicked)

        self.selectedTraitNameToButton[name] = button
        self.buttonToSelectedTrait[button] = trait

        self.selectedTraitsLayout.addWidget(button)
        self.updateUi()

    def onSelectedTraitClicked(self):
        button = self.sender()
        trait = self.buttonToSelectedTrait[button]
        name = trait["name"]

        # Deselect the trait
        for i, selectedTrait in enumerate(self.selectedTraits):
            if name == selectedTrait["name"]:
                self.selectedTraits.pop(i)

        button = self.selectedTraitNameToButton[name]
        self.selectedTraitsLayout.removeWidget(button)
        button.setParent(None)
        del button

        self.updateUi()

    def equipSelectedTraitsInGame(self):
        self.equipTraitsCallback(self.selectedTraits)

    def makeVerticalDivider(self):
        # https://stackoverflow.com/questions/5671354/
        verticalDivider = QFrame()
        verticalDivider.setGeometry(QRect(60, 110, 751, 20))
        verticalDivider.setFrameShape(QFrame.HLine)
        verticalDivider.setFrameShadow(QFrame.Sunken)
        return verticalDivider

    def _getSelectedTraitsLabelText(self):
        numTraits = len(self.selectedTraits)
        overallCost = sum([trait["cost"] for trait in self.selectedTraits])
        suffix = (
            ""
            if not self.selectedTraits
            else f" ({numTraits} traits, {overallCost} upgrade points)"
        )
        return f"Selected Traits{suffix}"

    def updateUi(self):
        self._updateMainButton()
        self._updateLabels()
        self._updateVisibleTraitButtons()

    def _updateMainButton(self):
        self.equipSelectedTraitsButton.setEnabled(len(self.selectedTraits) > 0)

    def _updateLabels(self):
        self.selectedTraitsLabel.setText(self._getSelectedTraitsLabelText())

    def _updateVisibleTraitButtons(self):
        for trait in self.availableTraits:
            button = self.availableTraitNameToButton[trait["name"]]
            button.setVisible(trait not in self.selectedTraits)


def launch_gui(equipTraitsCallback: callable):
    app = QApplication(sys.argv)
    window = MainWindow(equipTraitsCallback=equipTraitsCallback)
    window.show()

    app.exec_()

# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2018 qingfeng Xia <qingfeng.xia@gmail.coom>             *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "body source and initial value setup"
__author__ = "Qingfeng Xia"
__url__ = "http://www.freecadweb.org"

## @package FemBodyConstraint
#  \ingroup FEM
#  \brief QWidget for FEM general body source and initial value setup

import sys
sys.path.append('/usr/lib/freecad-daily/lib')  # just for testing

# import FreeCAD
# from FreeCAD import Units
# import FreeCADGui as Gui

# from PySide import QtCore
# preparing for PySide2 Qt5
from PySide.QtGui import QApplication
from PySide.QtGui import QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel,\
    QButtonGroup, QRadioButton, QLineEdit, QDoubleSpinBox


class BodyConstraintWidget(QWidget):

    def __init__(self, bodyConstraintSettings):
        super(BodyConstraintWidget, self).__init__()

        bcs = bodyConstraintSettings
        self.settings = bcs
        if bcs['Category'] == "InitialValue":
            self.setWindowTitle(self.tr("set initial value"))
        else:
            self.setWindowTitle(self.tr("set body source"))

        self.numberOfComponents = bcs['NumberOfComponents']
        vtype = bcs['ValueType']
        unit = bcs['Unit']

        _layout = QVBoxLayout()
        self.labelHelpText = QLabel(self.tr('set physical quantity by float or expression'), self)

        _buttonGroupLayout = QHBoxLayout()
        self.buttonGroupValueType = QButtonGroup()
        self.buttonGroupValueType.setExclusive(True)
        self.valueTypes = ['Quantity', 'Expression']
        valueTypeTips = [self.tr(u'float value for each component'), self.tr(u'math expressiong using xyz coord')]
        for id, choice in enumerate(self.valueTypes):
            rb = QRadioButton(choice)
            rb.setToolTip(valueTypeTips[id])
            self.buttonGroupValueType.addButton(rb, id)
            _buttonGroupLayout.addWidget(rb)
            if vtype == choice:
                rb.setChecked(True)
        self.buttonGroupValueType.buttonClicked.connect(self.valueTypeChanged)  # diff conect syntax

        _gridLayout = QGridLayout()
        if self.numberOfComponents == 1:
            self.componentLabels = [u'magnitude']
        else:
            self.componentLabels = [u'x-component', u'x-component', u'x-component']
        self.componentLabels = [l + u'({})'.format(unicode(unit)) for l in self.componentLabels]
        self.quantityInputs = []
        self.expressionInputs = []
        for i in range(self.numberOfComponents):
            input = QDoubleSpinBox()  # Gui.InputField() depends on FreeCAD
            expr = QLineEdit()  # QTextEdit is too big
            # expr.
            _gridLayout.addWidget(QLabel(self.componentLabels[i]), i, 0)
            _gridLayout.addWidget(input, i, 1)
            _gridLayout.addWidget(expr, i, 2)
            self.quantityInputs.append(input)
            self.expressionInputs.append(expr)

        _layout.addWidget(self.labelHelpText)
        _layout.addLayout(_buttonGroupLayout)
        _layout.addLayout(_gridLayout)
        self.setLayout(_layout)

        self.updateUI()

    def updateUI(self):
        # file data into UI, possibibly value is empty
        self.valueTypeChanged()

        value = self.settings['Value']
        if value is None:
            return
        if not isinstance(value, (list, tuple)):
            value = [value]
        for i in range(self.numberOfComponents):
            if self.settings['ValueType'] == 'Expression':
                self.expressionInputs[i].setText(unicode(value[i]))
            else:
                self.quantityInputs[i].setValue(value[i])

    def valueTypeChanged(self):
        # print(self.buttonGroupValueType.checkedId())
        self.currentValueType = self.valueTypes[self.buttonGroupValueType.checkedId()]
        if self.currentValueType == 'Expression':
            for q in self.quantityInputs:
                q.setVisible(False)
            for e in self.expressionInputs:
                e.setVisible(True)
        else:
            for q in self.quantityInputs:
                q.setVisible(True)
            for e in self.expressionInputs:
                e.setVisible(False)

    def bodyConstraintSettings(self):
        bcs = self.settings.copy()
        if self.currentValueType == 'Expression':
            value = [e.text() for e in self.expressionInputs]
        else:
            value = [q.value() for q in self.quantityInputs]
        bcs['Value'] = value
        bcs['ValueType'] = self.currentValueType
        return bcs


if __name__ == "__main__":
    app = QApplication(sys.argv)
    _DefaultInitialTemperature = {
        'Name': 'Temperature', 'Symbol': u'T', 'Category': 'InitialValue',
        'ValueType': 'Quantity', 'Unit': 'K', 'NumberOfComponents': 1, 'Value': 300
    }
    _DefaultBodyAcceleration = {
        'Name': 'Acceleration', 'Symbol': u'g', 'Category': 'BodySource',
        'ValueType': 'Quantity', 'Unit': 'm/s^2', 'NumberOfComponents': 3, 'Value': [0, 0, -9.8]
    }

    settings = _DefaultBodyAcceleration
    dialog = BodyConstraintWidget(settings)
    dialog. show()
    app.exec_()

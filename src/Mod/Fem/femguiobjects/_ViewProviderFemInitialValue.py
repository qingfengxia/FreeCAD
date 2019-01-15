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

__title__ = "FreeCAD FEM body constraint initial value ViewProvider"
__author__ = "Juergen Riegel, Bernd Hahnebach, Qingfeng Xia"
__url__ = "http://www.freecadweb.org"

## @package ViewProviderFemInitialValue
#  \ingroup FEM
#  \brief FreeCAD FEM view provider for constraint initial flow velocity object

import FreeCAD
from FreeCAD import Units
import FreeCADGui
from . import ViewProviderFemConstraint
from . import ViewProviderFemConstraint

# for the panel
from . import FemSelectionWidgets
from BodyConstraintWidget import BodyConstraintWidget

class _ViewProvider(ViewProviderFemConstraint.ViewProxy):

    def getIcon(self):
        # todo: dynamically generate icon by overlaying physical field symbol
        return ":/icons/fem-add-initial-value"

    def setEdit(self, vobj, mode=0):
        # hide all meshes
        for o in FreeCAD.ActiveDocument.Objects:
            if o.isDerivedFrom("Fem::FemMeshObject"):
                o.ViewObject.hide()
        # show task panel
        task =_TaskPanel(vobj.Object)
        FreeCADGui.Control.showDialog(task)
        return True

    def unsetEdit(self, vobj, mode=0):
        FreeCADGui.Control.closeDialog()
        return True


class _TaskPanel:
    '''The editmode TaskPanel for FemInitialValue objects (FemBodySource and FemInitialValue)'''

    def __init__(self, obj):
        self.obj = obj
        self.BodyConstraintSettings = self.obj.InitialValue
        self.BodyConstraintSettings['Category'] = 'InitialValue'
        shapeTypes = ['Solid', 'Face']  # Todo: detect geometry dimension

        self.parameterWidget = BodyConstraintWidget(self.BodyConstraintSettings)
        # geometry selection widget
        self.selectionWidget = FemSelectionWidgets.GeometryElementsSelection(obj.References, shapeTypes, False)
        # check references, has to be after initialisation of selectionWidget
        self.selectionWidget.has_equal_references_shape_types()

        # form made from param and selection widget
        self.form = [self.parameterWidget, self.selectionWidget]

    # ********* leave task panel *********
    def accept(self):
        # print(self.material)
        if self.selectionWidget.has_equal_references_shape_types():
            self.obj.InitialValue = self.parameterWidget.bodyConstraintSettings()
            self.obj.References = self.selectionWidget.references
            self.recompute_and_set_back_all()
            return True

    def reject(self):
        self.recompute_and_set_back_all()
        return True

    def recompute_and_set_back_all(self):
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.Document.recompute()
        self.selectionWidget.setback_listobj_visibility()
        if self.selectionWidget.sel_server:
            FreeCADGui.Selection.removeObserver(self.selectionWidget.sel_server)
        doc.resetEdit()
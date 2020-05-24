# ***************************************************************************
# *   Copyright (c) 2018 qingfeng Xia <qingfeng.xia@gmail.coom>             *
# *   Copyright (c) 2020 Bernd Hahnebach <bernd@bimstatik.org>              *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
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

__title__ = "FreeCAD FEM constraint body (point, line, face, volume) source document object"
__author__ = "Bernd Hahnebach, Qingfeng Xia"
__url__ = "http://www.freecadweb.org"

## @package _FemConstraintGeneric
#  \ingroup FEM
#  \brief FreeCAD FEM generic constraint object

from . import base_fempythonobject


class ConstraintGeneric(base_fempythonobject.BaseFemPythonObject):
    """
    The generic object for initial values and source constraint

    Currently: "Acceleration", a more generic one than SelfWeight,
    and "InitialPressure", are implemented using this generic constraint class. 
    `Acceleration` belongs to "Source" category, while InitialPressure is of 
    "InitialValue" category. A third category "Constraint" means constraint/
    boundary condition applied to geometry elements (point, line, face, body).
    If a simple constraint type, e.g. applying a fixed temperature value on some
    face boundary, then this generic constraint type can be used.

    Two types of value input are supported:
     1. constant scalar/vector means homogenous value in the selected geometry.
     2. textual expression, e.g. "1x+3y-2t", means values depends on time(t) 
        and coordinate (x, y, z). The solver input writer should parse and 
        this expression to fit specific solver input expression format.

    This generic constraint type is designed to reduce code duplication.
    To add a new constraint type based on this generic constraint:

    1. define the data structure,  e.g. `_DefaultConstraintAcceleration`
        in the file "femobjects.ConstraintGenericDefaults" 
    2. add `makeXXXConstraint()` function in `FemObject.py`, 
        following existing examples in "FemObject.py"
    3. add a new FemCommand class in "femcommands.py"
        to create the new constraint type, including icon.
        If a new icon file is added, remember to update "Gui/Resources/Fem.qrc"
    4. enable the new constraint type in "InitGui.py" or/and "Gui/Workbench.cpp"
    5. add new files into specific groups of Fem module's CMakeLists.txt
    
    All done, no TaskPanel nor ViewProvider is needed. The default taskpanel has 
    generic Boundary/Geometry selection widget and a generic value input widget
    for constant scalar/vector and expression. In a nonlinear simulation, a good
    guess of initial value can significantly reduce the computation time.
    """

    Type = "Fem::ConstraintGeneric"

    def __init__(self, obj):
        super(ConstraintGeneric, self).__init__(obj)

        obj.addProperty(
            "App::PropertyEnumeration",
            "Category",
            "GenericConstraint",
            "to distinguish constraint or initial value or source"
        )
        obj.addProperty(
            "App::PropertyLinkSubList",
            "References", "GenericConstraint",
            "List of geometry references/links"
        )
        obj.addProperty(
            "App::PropertyEnumeration",
            "ShapeType",  # consider: rename to PreferedShapeType or DefaultShapeType
            "GenericConstraint",
            "the default geometry shape type for this constraint"
        )
        obj.addProperty(
            "App::PropertyStringList",
            "ShapeTypes",
            "GenericConstraint",
            "List of applicable shape types"
        )
        obj.addProperty(
            "App::PropertyPythonObject",
            "Settings",
            "GenericConstraint",
            "A dictionary holds settings for constraint, initial value or source"
        )
        obj.Category = ["Constraint", "InitialValue", "Source"]
        obj.Category = "Constraint"
        obj.ShapeTypes = ["Solid", "Face", "Edge", "Vertex"]  # == OCCT ShapeType names
        obj.ShapeType = ["Solid", "Face", "Edge", "Vertex"]  # == OCCT ShapeType names
        obj.ShapeType = "Solid"  # default shape type
        obj.References = []
        obj.Settings = {"Velocity": {}}

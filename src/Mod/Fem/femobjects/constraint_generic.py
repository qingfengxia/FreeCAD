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

    This generic constraint type is designed to reduce code duplication.
    To add a new constraint type based on this generic constraint:

    1. define the data structure, in "femobjects/ConstraintGenericDefaults.py"
        This a python dictionary object, the default values are used
        to initialize the TaskPanel UI; once accepted, user input values are
        updated to the `Setting` property (python dictionary) of ConstraintGeneric
        ```python
            _DefaultConstraintAcceleration = {
            "Name": "Acceleration",
            "Symbol": u"g",
            "ValueType": "Quantity",
            "NumberOfComponents": 3,
            "Unit": "m/s^2",
            "Value": [0, 0, -9.8]
        }
        ```
        Two types of input `ValueType` are supported: Quantity, Expression
        + constant scalar/vector quantity means homogenous distrbution.
        + textual expression, e.g. "1x+3y-2t", means values depends on time(t) 
            and coordinate (x, y, z). The solver input writer should parse and 
            this expression to fit specific solver input expression format.
        
        Unit and Value are essential to create a Quantity, while Symbol are Name
        can be used to generate per quantity type icon and DocumentObject names.

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

    To retrieve info from this constraint type in a FEM model writer:
    1. use ConstraintGeneric's properties: Category, Settings, Reference
    2. use the `References` a list of geometry sublink as other FEM constraints
    3. value can be retrieved from Settings["Value"], which is a list of components.
        The component can be number or string depends on Settings["ValueType"];
        Settings["NumberOfComponents"] hints value dim: scalar, vector and tensor;
        Settings["Unit"] is needed as an essential part of physical quantity.
        
    Note: Quantity input UI `Gui.InputField` has not been used in the task panel
          since the contraint value input widget is created according to "Settings", 
          instead of *.ui file.
    """

    Type = "Fem::ConstraintGeneric"

    def __init__(self, obj):
        super(ConstraintGeneric, self).__init__(obj)

        obj.addProperty(
            "App::PropertyEnumeration",
            "Category",
            "ConstraintGeneric",
            "to distinguish InitialValue, Constraint or Source"
        )
        obj.addProperty(
            "App::PropertyLinkSubList",
            "References", "ConstraintGeneric",
            "List of geometry references/links this contraint will apply to"
        )
        obj.addProperty(
            "App::PropertyEnumeration",
            "ShapeType",  # consider: rename to PreferedShapeType or DefaultShapeType
            "ConstraintGeneric",
            "the default geometry shape type for this constraint"
        )
        obj.addProperty(
            "App::PropertyStringList",
            "ShapeTypes",
            "ConstraintGeneric",
            "List of applicable shape types"
        )
        obj.addProperty(
            "App::PropertyPythonObject",
            "Settings",
            "ConstraintGeneric",
            "A dictionary holds settings for constraint, initial value or source"
        )
        obj.Category = ["Constraint", "InitialValue", "Source"]
        obj.Category = "Constraint"
        obj.ShapeTypes = ["Solid", "Face", "Edge", "Vertex"]
        obj.ShapeType = ["Solid", "Face", "Edge", "Vertex"]
        obj.ShapeType = "Solid"  # default shape type
        obj.References = []
        obj.Settings = {} #  user type default values defined in ConstraintGenericDefaults.py

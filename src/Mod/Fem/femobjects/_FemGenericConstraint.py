# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2017 Markus Hovorka <m.hovorka@live.de>                 *
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

__title__ = "FreeCAD FEM constraint body (point, line, face, volume) source document object"
__author__ = "Bernd Hahnebach, Qingfeng Xia"
__url__ = "http://www.freecadweb.org"

## @package FemGenericConstraint
#  \ingroup FEM
#  \brief FreeCAD FEM generic constraint object


class _FemGenericConstraint(object):
    "The FEM body source document object"
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "Fem::GenericConstraint"

        obj.addProperty(
            "App::PropertyEnumeration",
            "Category",
            "GenericConstraint",
            "to distinguish contraint or initial value or source"
        )
        obj.addProperty(
            "App::PropertyLinkSubList",
            "References", "GenericConstraint",
            "List of geometry references/links"
        )
        obj.addProperty(
            "App::PropertyEnumeration",
            "ShapeType",  # code review: rename to PreferedShapeType? or just remove this
            "GenericConstraint",
            "perfered geometry shape type"
        )
        obj.addProperty(
            "App::PropertyStringList",
            "ShapeTypes",
            "GenericConstraint",
            "List of ppliable shape types"
        )
        obj.addProperty(
            "App::PropertyPythonObject",
            "Settings",
            "GenericConstraint",
            "A dictionary holds settings for contraint, initial value or source"
        )
        obj.Category = ["Constraint", "InitialValue", "Source"]
        obj.Category = "Constraint"
        obj.ShapeTypes = ["Solid", "Face", "Edge", "Vertex"]  # == OCCT ShapeType names
        obj.ShapeType = ["Solid", "Face", "Edge", "Vertex"]  # == OCCT ShapeType names
        obj.ShapeType = "Solid"
        obj.References = []
        obj.Settings = {}

    def execute(self, obj):
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
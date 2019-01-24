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
__author__ = "Markus Hovorka, Bernd Hahnebach, Qingfeng Xia"
__url__ = "http://www.freecadweb.org"

## @package FemBodySource
#  \ingroup FEM
#  \brief FreeCAD FEM constraint body heat source object


class _FemBodySource:
    "The FEM body source document object"
    def __init__(self, obj):
        obj.addProperty("App::PropertyLinkSubList", "References", "BodySource", "List of body shapes")
        obj.addProperty("App::PropertyEnumeration", "ShapeType", "BodySource", "List of body shapes")
        obj.addProperty("App::PropertyPythonObject", "BodySource", "BodySource", "Initial value or body source")
        obj.ShapeType = ['Solid', 'Face', 'Edge', 'Vertex']  # same shape name with OpenCASCADE
        obj.ShapeType = "Solid"
        obj.Proxy = self
        self.Type = "Fem::BodySource"

    def execute(self, obj):
        return

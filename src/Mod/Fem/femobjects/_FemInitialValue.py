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

__title__ = "FreeCAD FEM body constraint (initial value) document object"
__author__ = "Markus Hovorka, Bernd Hahnebach, Qingfeng Xia"
__url__ = "http://www.freecadweb.org"

## @package FemInitialValue
#  \ingroup FEM
#  \brief FreeCAD FEM intial value, one kind of body constraint


class _FemInitialValue:
    "The general Fem InitialValue object"
    def __init__(self, obj):
        obj.addProperty("App::PropertyLinkSubList", "References", "InitialValue", "List of body shapes")
        obj.addProperty("App::PropertyPythonObject", "InitialValue", "InitialValue", "Initial value python dict")
        obj.Proxy = self
        self.Type = "Fem::InitialValue"

    def execute(self, obj):
        return

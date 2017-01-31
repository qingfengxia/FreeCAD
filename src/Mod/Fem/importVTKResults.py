# ***************************************************************************
# *   (c) Qingfeng Xia 2017                       *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Lesser General Public License for more details.                   *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with FreeCAD; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# *   Juergen Riegel 2002                                                   *
# ***************************************************************************/

__title__ = "FreeCAD Result import and export VTK file library"
__author__ = "Qingfeng Xia"
__url__ = "http://www.freecadweb.org"

## @package importVTKResults
#  \ingroup FEM

import os
import FreeCAD
import Fem


if open.__module__ == '__builtin__':
    pyopen = open  # because we'll redefine open below


def insert(filename, docname):
    "called when freecad wants to import a file"
    try:
        doc = FreeCAD.getDocument(docname)
    except NameError:
        doc = FreeCAD.newDocument(docname)
    FreeCAD.ActiveDocument = doc
    importFemResult(filename)


def open(filename):
    "called when freecad opens a file"
    docname = os.path.splitext(os.path.basename(filename))[0]
    insert(filename, docname)


def importFemResult(filename):
    result_name_prefix = "Result"
    # if properties can be added in FemVTKTools importCfdResult(), this file can be used for CFD workbench
    from FemResult import makeFemResult
    result_obj = makeFemResult(result_name_prefix)
    import Fem
    Fem.readResult(filename, result_obj.Name)  # always create a new femmesh

    filenamebase = '.'.join(filename.split('.')[:-1])  # pattern: filebase_timestamp.vtk
    ts = filenamebase.split('_')[-1]
    try:
        time_step = float(ts)
    except:
        time_step = 0.0
    #Stats has been setup in C++ function FemVTKTools importCfdResult()

def export(objectslist, filename):
    "called when freecad exports a fem result object"
    if len(objectslist) != 1:
        FreeCAD.Console.PrintError("This exporter can only export one object at once\n")
        return
    obj = objectslist[0]
    if not obj.isDerivedFrom("Fem::FemResultObject"):
        FreeCAD.Console.PrintError("object selcted is not FemResultObject.\n")
        return
    import Fem
    Fem.writeResult(filename, obj)

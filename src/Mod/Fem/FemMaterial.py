# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2013 - Juergen Riegel <FreeCAD@juergen-riegel.net>      *
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

__title__ = "FluidMaterial"
__author__ = "Juergen Riegel, Qingfeng Xia"
__url__ = "http://www.freecadweb.org"

"""
FSI or multiple physics model needs a general material model
"""

import FreeCAD
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui

def makeFemMaterial(name, category = "Fluid"):
    '''makeMaterial(name): makes an Material name therefore is a material name or an file name for a FCMat file'''
    obj = FreeCAD.ActiveDocument.addObject("App::MaterialObjectPython", category)
    _FemMaterial(obj)
    obj.Category = category
    if FreeCAD.GuiUp:
        #import _ViewProviderFemMaterial
        _ViewProviderFemMaterial(obj.ViewObject)
    # FreeCAD.ActiveDocument.recompute()
    return obj


class _FemMaterial:
    "The General Material object for Fluid and Mechanical"
    def __init__(self, obj):
        self.Type = "FemMaterial" # Type ID: 'App::MaterialObjectPython'
        self.Object = obj
        obj.Proxy = self
        
        obj.addProperty("App::PropertyLinkSubList", "References", "Material", 
                        "List of material shapes")
        #App::Material has MaterialType property already, predefined material for OpenGL rendering
        
        obj.addProperty("App::PropertyEnumeration", "Category", "Material", 
                        "Mateial states: Solid, Fluid(liquid, gas), etc")
        obj.Category = ["Fluid", "Solid"]  # "Liquid", "Gas", "Mixture" etc
        obj.addProperty("App::PropertyString", "Name", "Material")
        obj.addProperty("App::PropertyString", "Description", "Material")

        #"Material" to store mechanical properties + "Name" "Description"
        # it is a python dict, where it is defined? 
        """
        obj.addProperty("App::PropertyQuantity", "YoungModulus", "Mechanical",
                        "Young modulus for solid material", False)
        obj.addProperty("App::PropertyQuantity", "YieldStrength", "Mechanical",
                        "Yield strength for solid material", False)
        obj.addProperty("App::PropertyQuantity", "Density", "Mechanical",
                        "Density for solid material", False)
        """
        #FluidicProperties,  App::PropertyQuantity may lead to JSON serialisation error
        obj.addProperty("App::PropertyPythonObject", "FluidicProperties", "Material",
                "App::PropertyMap of FluidicProperties", False)
        obj.FluidicProperties = {'name':'water', 'kinematicViscosity':1e6}
        """
        obj.addProperty("App::PropertyEnumeration", "ViscosityType", "Fluidic",
                        "scheme to calc kinematic viscosity", True)
        obj.ViscosityType = ["FixedValue", "IdealGas"]
        obj.addProperty("App::PropertyQuantity", "KinematicViscosity", "Fluidic",
                        "", False)
        #obj.KinematicViscosity = 1e-6
        obj.addProperty("App::PropertyEnumeration", "DensityType", "Fluidic",
                        "", True)
        obj.DensityType = ["FixedValue", "IdealGas"]  # for compressible flow
        obj.addProperty("App::PropertyQuantity", "FluidDensity", "Fluidic",
                        "", False)
        #obj.FluidDensity = 1e3
        """
        
        #ThermalProperties
        obj.addProperty("App::PropertyPythonObject", "ThermalProperties", "Material",
                "python dict of ThermalProperties", False)
        """
        obj.addProperty("App::PropertyQuantity", "SpecificHeat", "Thermal",
                "", False)
        obj.addProperty("App::PropertyQuantity", "ThermalConductivity", "Thermal",
                "", False)
        obj.addProperty("App::PropertyQuantity", "ThermalExpansion", "Thermal",
                "unit [m/m/K]", False)
        """
        #Eletromagnetic properties
                
    def execute(self, obj):
        return

class _ViewProviderFemMaterial:
    "A View Provider for the General Material object for Fem workbench"

    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        return ":/icons/fem-material.svg"

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def updateData(self, obj, prop):
        return

    def onChanged(self, vobj, prop):
        return

    def setEdit(self, vobj, mode):
        import _TaskPanelFemMaterial
        taskd = _TaskPanelFemMaterial.TaskPanelFemMaterial(self.Object)
        taskd.obj = vobj.Object
        FreeCADGui.Control.showDialog(taskd)
        return True

    def unsetEdit(self, vobj, mode):
        FreeCADGui.Control.closeDialog()
        return

    # overwrite the doubleClicked to make sure no other Material taskd (and thus no selection observer) is still active
    def doubleClicked(self, vobj):
        doc = FreeCADGui.getDocument(vobj.Object.Document)
        if not doc.getInEdit():
            doc.setEdit(vobj.Object.Name)
        else:
            FreeCAD.Console.PrintError('Active Task Dialog found! Please close this one first!\n')
        return True

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
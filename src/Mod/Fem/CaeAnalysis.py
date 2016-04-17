#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2015 - Qingfeng Xia <qingfeng.xia()eng.ox.ac.uk> *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************

__title__ = "Command and Classes for New CAE Analysis"
__author__ = "Qingfeng Xia"
__url__ = "http://www.freecadweb.org"

"""
Changelog: CaeSolver.py is merged into this file, 
FemAnalysis is still designed for Calculix only, therefore, CaeAnalysis is kept for 
"""

import FreeCAD
from FemCommands import FemCommands
from CaeSolver import makeCaeSolver

if FreeCAD.GuiUp:
    import FreeCADGui
    import FemGui
    from PySide import QtCore


"""
def makeMechanicalAnalysis(name):
    '''makes a Fem MechAnalysis object'''
    obj =  _CreateCaeAnalysis('Calculix', name)
    obj.Type = "MechAnalysis"
    return obj
"""

def _makeCaeAnalysis(name):
    '''makeCaeAnalysis(name): makes a CAE Analysis object,
    this is designed for internal usage only'''
    obj = FreeCAD.ActiveDocument.addObject("Fem::FemAnalysisPython", name)
    CaeAnalysis(obj)
    if FreeCAD.GuiUp:
        ViewProviderCaeAnalysis(obj.ViewObject)
    #FreeCAD.ActiveDocument.recompute()
    return obj


class CaeAnalysis:
    """The CaeAnalysis container object, serve CFD ,FEM, etc
    This class should not have instance methods,
    since document reload, this class's instance does not exist!
    """
    def __init__(self, obj):
        self.Type = "CaeAnalysis"
        self.Object = obj  # keep a ref to the DocObj for nonGui usage
        obj.Proxy = self  # link between App::DocumentObject to  this object
        obj.addProperty("App::PropertyString", "Category", "Analysis", "Cfd, Computional solid mechanics")
        obj.addProperty("App::PropertyString", "SolverName", "Analysis", "External solver unique name")

    # following are the FeutureT standard methods
    def execute(self, obj):
        """updated Part should lead to recompute of mesh, if result_present"""
        return

    def onChanged(self, obj, prop):
        """updated Part should lead to recompute of mesh"""
        if prop in ["MaterialName"]:
            return  # todo!

    def __getstate__(self):
        "store python attribute into FCStd file"
        return self.Type

    def __setstate__(self, state):
        "restore python attribute from  FCStd file"
        if state:
            self.Type = state


class ViewProviderCaeAnalysis:
    """A View Provider for the CaeAnalysis container object
    doubleClicked() should activate AnalysisControlTaskView
    """
    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        return ":/icons/fem-analysis.svg"

    def setIcon(self,icon):
        self.icon = icon

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object
        self.bubbles = None

    def updateData(self, obj, prop):
        return

    def onChanged(self, vobj, prop):
        return

    def doubleClicked(self, vobj):
        if not FemGui.getActiveAnalysis() == self.Object:
            if FreeCADGui.activeWorkbench().name() != 'FemWorkbench':
                FreeCADGui.activateWorkbench("FemWorkbench")
            FemGui.setActiveAnalysis(self.Object)
            return True
        else:
            import _TaskPanelAnalysisControl
            taskd = _TaskPanelAnalysisControl._TaskPanelAnalysisControl(self.Object)
            FreeCADGui.Control.showDialog(taskd)
        return True

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def _CreateCaeAnalysis(solverName, analysisName=None):
        """ work for both Gui and nonGui mode"""
        _analysisName = analysisName if analysisName else solverName + "Analysis"
        if FreeCAD.GuiUp:
            FreeCAD.ActiveDocument.openTransaction("Create Cae Analysis")
            FreeCADGui.addModule("FemGui")
            FreeCADGui.addModule("CaeAnalysis")
            FreeCADGui.doCommand("CaeAnalysis._makeCaeAnalysis('{}')".format(_analysisName))
            obj = FreeCAD.activeDocument().ActiveObject
            FreeCADGui.doCommand("FemGui.setActiveAnalysis(App.activeDocument().ActiveObject)")
            # create an solver and append into analysisObject
            FreeCADGui.doCommand("CaeAnalysis.makeCaeSolver('{}')".format(solverName))
            FreeCADGui.doCommand("FemGui.getActiveAnalysis().Member = FemGui.getActiveAnalysis().Member + [App.activeDocument().ActiveObject]")
            sel = FreeCADGui.Selection.getSelection()
            if (len(sel) == 1):
                if(sel[0].isDerivedFrom("Fem::FemMeshObject")):
                    FreeCADGui.doCommand("FemGui.getActiveAnalysis().ActiveObject.Member = FemGui.getActiveAnalysis().Member + [App.activeDocument()." + sel[0].Name + "]")
                if(sel[0].isDerivedFrom("Part::Feature")):
                    FreeCADGui.doCommand("App.activeDocument().addObject('Fem::FemMeshShapeNetgenObject', '" + sel[0].Name + "_Mesh')")
                    FreeCADGui.doCommand("App.activeDocument().ActiveObject.Shape = App.activeDocument()." + sel[0].Name)
                    FreeCADGui.doCommand("FemGui.getActiveAnalysis().Member = FemGui.getActiveAnalysis().Member + [App.activeDocument().ActiveObject]")
                    #FreeCADGui.doCommand("Gui.activeDocument().hide('" + sel[0].Name + "')")
                    #FreeCADGui.doCommand("App.activeDocument().ActiveObject.touch()")
                    #FreeCADGui.doCommand("App.activeDocument().recompute()")
                    FreeCADGui.doCommand("Gui.activeDocument().setEdit(App.ActiveDocument.ActiveObject.Name)")

            #FreeCAD.ActiveDocument.commitTransaction()
            FreeCADGui.Selection.clearSelection()
        else:
            import CaeAnalysis
            obj = CaeAnalysis._makeCaeAnalysis(_analysisName)
            import CaeSolver
            sobj = CaeSolver.makeCaeSolver(solverName)
            obj.Member = obj.Member + [sobj]
        return obj


class _CommandNewCfdAnalysis(FemCommands):
    "the Cfd Analysis command definition"
    def __init__(self):
        super(_CommandNewCfdAnalysis, self).__init__()
        self.resources = {'Pixmap': 'fem-cfd-analysis',
                          'MenuText': QtCore.QT_TRANSLATE_NOOP("Fem_CfdAnalysis", "New CFD analysis"),
                          'Accel': "N, A",  # conflict with mechanical analysis?
                          'ToolTip': QtCore.QT_TRANSLATE_NOOP("Fem_CfdAnalysis", "Create a new computional fluid dynamics analysis")}
        self.is_active = 'with_document'

    def Activated(self):
        _CreateCaeAnalysis('OpenFOAM')
        

class _CommandNewMaterial(FemCommands):
    "the create new FemMaterial command definition"
    def __init__(self):
        super(_CommandNewMaterial, self).__init__()
        self.resources = {'Pixmap': 'fem-material',
                          'MenuText': QtCore.QT_TRANSLATE_NOOP("Fem_NewMaterial", "New material for any Fem analysis"),
                          'Accel': "N, A",  # conflict with mechanical analysis?
                          'ToolTip': QtCore.QT_TRANSLATE_NOOP("Fem_NewMaterial", "Create a new material for anlaysis")}
        self.is_active = 'with_document'

    def Activated(self):
        femDoc = FemGui.getActiveAnalysis().Document
        if FreeCAD.ActiveDocument is not femDoc:
            FreeCADGui.setActiveDocument(femDoc)
        FreeCAD.ActiveDocument.openTransaction("Create Material for Fem or Cfd")
        FreeCADGui.addModule("FemMaterial")
        FreeCADGui.doCommand("FemMaterial.makeFemMaterial('Fluid')")
        FreeCADGui.doCommand("App.activeDocument()." + FemGui.getActiveAnalysis().Name + ".Member = App.activeDocument()." + FemGui.getActiveAnalysis().Name + ".Member + [App.ActiveDocument.ActiveObject]")
        FreeCADGui.doCommand("Gui.activeDocument().setEdit(App.ActiveDocument.ActiveObject.Name)")


"""
class _CommandNewMechAnalysis(FemCommands):
    "the Mechancial FEM Analysis command definition"
    def __init__(self):
        super(_CommandNewMechAnalysis, self).__init__()
        self.resources = {'Pixmap': 'fem-mech-analysis',
                          'MenuText': QtCore.QT_TRANSLATE_NOOP("Fem_MechAnalysis", "New FEM Mechanical Analysis"),
                          'Accel': "N, A",
                          'ToolTip': QtCore.QT_TRANSLATE_NOOP("Fem_MechAnalysis", "Create a new Mechanical FEM Analysis")}
        self.is_active = 'with_document'

    def Activated(self):
        _CreateCaeAnalysis('Calculix')

"""
class _CommandAnalysisControl(FemCommands):
    "the Fem Analysis Job Control command definition"
    def __init__(self):
        super(_CommandAnalysisControl, self).__init__()
        self.resources = {'Pixmap': 'fem-new-analysis',
                          'MenuText': QtCore.QT_TRANSLATE_NOOP("Fem_AnalysisControl", "Start analysis"),
                          'Accel': "S, C",
                          'ToolTip': QtCore.QT_TRANSLATE_NOOP("Fem_AnalysisControl", "Dialog to start the calculation of the anlysis")}
        self.is_active = 'with_analysis'

    def Activated(self):
        import _TaskPanelAnalysisControl
        import FemGui
        taskd = _TaskPanelAnalysisControl._TaskPanelAnalysisControl(FemGui.getActiveAnalysis())
        taskd.update()
        FreeCADGui.Control.showDialog(taskd)

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Fem_NewCfdAnalysis', _CommandNewCfdAnalysis())
    FreeCADGui.addCommand('Fem_NewMaterial', _CommandNewMaterial())
    #FreeCADGui.addCommand('Fem_NewMechAnalysis', _CommandNewMechAnalysis())
    FreeCADGui.addCommand('Fem_AnalysisControl', _CommandAnalysisControl())


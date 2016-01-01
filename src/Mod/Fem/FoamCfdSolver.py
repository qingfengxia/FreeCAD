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

import os.path

import FreeCAD
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui


from FoamCaseBuilder import supported_turbulence_models
from FoamCaseBuilder import supported_multiphase_models
#from FoamCaseBuilder import supported_radiation_models


class CaeSolver():
    """Fem::FemSolverObject 's Proxy python type
    add solver specific properties, methods and bring up SolverControlTaskPanel.
    After loaded from FCStd file, this python class is not instantiated.
    use CaeTools.getSolverPythonFromAnalysis() to get/create such an instance.
    """
    def __init__(self, obj):
        self.Type = "CfdSolver"
        self.Object = obj  # keep a ref to the DocObj for nonGui usage
        obj.Proxy = self  # link between App::DocumentObject to  this object
        
        #some properties previously defined in FemSolver C++ object are moved here
        if not "SolverName" in obj.PropertiesList:
            obj.addProperty("App::PropertyString", "SolverName", "Solver",
                            "unique solver name to identify the solver")
            obj.addProperty("App::PropertyEnumeration", "Category", "Solver",
                            "unique solver name to identify the solver")
            obj.Category = ['CFD', 'FEM']
            obj.addProperty("App::PropertyString", "Module", "Solver",
                            "python module for case writer")            
            obj.addProperty("App::PropertyString", "ExternalResultViewer", "Solver",
                            "External Result Viewer's program name like paraview")
            obj.addProperty("App::PropertyString", "ExternalCaseEditor", "Solver",
                            "External Case Editor's program name like any text editor")
            #the above the properties can be initialised in CaeAnalysis._makeCaeAnalysis()                
            obj.addProperty("App::PropertyString", "WorkingDir", "Solver",
                            "Solver process is run in this directory")
            obj.addProperty("App::PropertyString", "InputCaseName", "Solver",
                            "input file name without suffix or case folder name")
            obj.addProperty("App::PropertyBool", "Parallel", "Solver",
                            "solver is run with muliticore or on cluster")
            obj.addProperty("App::PropertyBool", "ResultObtained", "Solver",
                            "result of analysis has been obtained, i.e. case setup is fine")
            obj.InputCaseName = 'TestCase'
            obj.WorkingDir = './'
        # general CFD properties,  create if not existent
        if not "Compressible" in obj.PropertiesList:
            # API: addProperty(self,type,name='',group='',doc='',attr=0,readonly=False,hidden=False)
            obj.addProperty("App::PropertyEnumeration", "TurbulenceModel", "CFD",
                            "Laminar,KE,KW,LES,etc")
            obj.TurbulenceModel = list(supported_turbulence_models)
            obj.addProperty("App::PropertyEnumeration", "MultiPhaseModel", "CFD",
                            "Mixing, VoF, DiscreteParticleModel")
            obj.MultiPhaseModel = list(supported_multiphase_models)
            # DynanicMeshing, MultiPhaseModel, Combustion will not be implemented for model setup complexity
            obj.addProperty("App::PropertyBool", "DynamicMeshing", "CFD",
                            "mobile/moving meshing function", True)
            obj.addProperty("App::PropertyBool", "Compressible", "CFD",
                            "Compressible air or Incompressible like liquid, including temperature field", True)
            obj.addProperty("App::PropertyBool", "Porous", "CFD",
                            "Porous material model enabled or not", True)
            obj.addProperty("App::PropertyBool", "Nonnewtonian", "CFD",
                            "fluid property, strain-rate and stress constition, water and air are Newtonion", True)
            #heat transfer group
            obj.addProperty("App::PropertyBool", "HeatTransfering", "HeatTransfer",
                             "calc temperature field, needed by compressible flow", True)
            obj.addProperty("App::PropertyBool", "Buoyant", "HeatTransfer",
                             "gravity induced flow, needed by compressible heat transfering analysis", True, True)
            #obj.addProperty("App::PropertyEnumeration", "RadiationModel", "HeatTransfer",
            #                 "radiation heat transfer model", True)
            #obj.RadiationModel = list(supported_radiation_models)
            obj.addProperty("App::PropertyBool", "Conjugate", "HeatTransfer",
                             "MultiRegion fluid and solid conjugate heat transfering analysis", True)
            # CurrentTime TimeStep StartTime, StopTime
            obj.addProperty("App::PropertyBool", "Transient", "Transient",
                            "Static or transient analysis", True)
            #MultiphysicalCoupling
            # additional solver specific properties
        # FemSolverObject standard properties should be set in _SetSolverInfo() of CaeSolver.py

    ########## CaeSolver API #####################
    def check_prerequisites(self, analysis_object):
        return ""

    def write_case(self, analysis_object=None):
        if analysis_object is None and FreeCAD.GuiUp:
            import FemGui
            analysis_object = FemGui.getActiveAnalysis()
        import FoamCaseWriter
        writer = FoamCaseWriter.CaseWriter(analysis_object)
        writer.write_case()


    def generate_cmdline(self):
        case_path = self.Object.WorkingDir + os.path.sep + self.Object.InputCaseName
        import FoamCaseBuilder
        solver_name = FoamCaseBuilder.getSolverName(self.Object)
        return "{} -case {}".format(solver_name, case_path)

    def edit_case_externally(self):
        case_path = self.Object.WorkingDir + os.path.sep + self.Object.InputCaseName
        if FreeCAD.GuiUp:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(case_path))
        else:
            FreeCAD.PrintMessage("Please edit the case input files under {}".format(case_path))

    def view_result_externally(self):
        case_path = self.Object.WorkingDir + os.path.sep + self.Object.InputCaseName
        return "paraFoam  -case {}".format(case_path)

    ############ standard FeutureT methods ##########
    def execute(self, obj):
        """"this method is executed on object creation and whenever the document is recomputed"
        update Part or Mesh should NOT lead to recompution of the analysis automatically, time consuming"""
        return

    def onChanged(self, obj, prop):
        return

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state


# this class could be moved into CaeSolver, as it can be shared by any solver
class ViewProviderCaeSolver:
    """A View Provider for the Solver object, base class for all derived solver
    derived solver should implement  a specific TaskPanel and set up solver and override setEdit()"""

    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        """after load from FCStd file, self.icon does not exist, return constant path instead"""
        return ":/icons/fem-solver.svg"

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def updateData(self, obj, prop):
        return

    def onChanged(self, vobj, prop):
        return

    def doubleClicked(self, vobj):
        """after load from FCStd file, self.Object does not exist, use vobj.Object instead"""
        # from solver_specific module import _SolverControlTaskPanel
        taskd = _TaskPanelSolverControl(vobj.Object)
        FreeCADGui.Control.showDialog(taskd)
        return True

    def setEdit(self, vobj, mode):
        taskd = _TaskPanelSolverControl(vobj.Object)
        FreeCADGui.Control.showDialog(taskd)
        return True

    def unsetEdit(self, vobj, mode):
        #FreeCADGui.Control.closeDialog()
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class _TaskPanelSolverControl:
    def __init__(self, solver_object):
        self.form = FreeCADGui.PySideUic.loadUi(FreeCAD.getHomePath() + "Mod/Fem/TaskPanelSolverControl.ui")
        #QtGui.QMessageBox.critical(None, "This task panel is not implement yet", "Please edit in property editor ")
        pass

    def accept(self):
        return True

    def reject(self):
        return True

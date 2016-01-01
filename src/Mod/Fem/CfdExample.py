#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2015 - Qingfeng Xia @iesensor.com                 *
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

App.newDocument("Unnamed")
App.setActiveDocument("Unnamed")
App.ActiveDocument=App.getDocument("Unnamed")
Gui.ActiveDocument=Gui.getDocument("Unnamed")
#
Gui.activateWorkbench("PartWorkbench")
App.ActiveDocument.addObject("Part::Cylinder","Cylinder")
App.ActiveDocument.ActiveObject.Label = "Cylinder"
App.ActiveDocument.recompute()
Gui.SendMsgToActiveView("ViewFit")
Gui.activateWorkbench("FemWorkbench")
#
mesh_obj = App.activeDocument().addObject('Fem::FemMeshShapeNetgenObject', 'Cylinder_Mesh')
App.activeDocument().ActiveObject.Shape = App.activeDocument().Cylinder
Gui.activeDocument().setEdit(App.ActiveDocument.ActiveObject.Name)
Gui.activeDocument().resetEdit()
#
import FemGui
import CaeAnalysis
analysis_obj = CaeAnalysis._CreateCaeAnalysis('OpenFOAM', 'OpenFOAMAnalysis')
analysis_obj.Member = analysis_obj.Member  + [mesh_obj]

#
Gui.getDocument("Unnamed").getObject("Cylinder_Mesh").Visibility=False
Gui.getDocument("Unnamed").getObject("Cylinder").Visibility=True
#
import MechanicalMaterial
MechanicalMaterial.makeMechanicalMaterial('MechanicalMaterial')
App.activeDocument().OpenFOAMAnalysis.Member = App.activeDocument().OpenFOAMAnalysis.Member + [App.ActiveDocument.ActiveObject]
Gui.activeDocument().setEdit(App.ActiveDocument.ActiveObject.Name,0)
#velocity inlet
FemGui.setActiveAnalysis(App.activeDocument().OpenFOAMAnalysis)
App.activeDocument().addObject("Fem::ConstraintForce","Inlet")
App.activeDocument().OpenFOAMAnalysis.Member = App.activeDocument().OpenFOAMAnalysis.Member + [App.activeDocument().Inlet]
App.ActiveDocument.Inlet.Force = 0.100000  # unit? 
App.ActiveDocument.Inlet.Direction = None
App.ActiveDocument.Inlet.Reversed = False
App.ActiveDocument.Inlet.References = [(App.ActiveDocument.Cylinder,"Face3")]
App.ActiveDocument.recompute()
#pressure outlet
App.activeDocument().addObject("Fem::ConstraintPressure","FemConstraintPressure")
App.activeDocument().FemConstraintPressure.Pressure = 0.0
App.activeDocument().OpenFOAMAnalysis.Member = App.activeDocument().OpenFOAMAnalysis.Member + [App.activeDocument().FemConstraintPressure]
App.ActiveDocument.recompute()
Gui.activeDocument().setEdit('FemConstraintPressure')
App.ActiveDocument.FemConstraintPressure.Pressure = 0.000010
App.ActiveDocument.FemConstraintPressure.Label = 'PressureOutlet'
App.ActiveDocument.FemConstraintPressure.Reversed = True
App.ActiveDocument.FemConstraintPressure.References = [(App.ActiveDocument.Cylinder,"Face2")]
App.ActiveDocument.recompute()
Gui.activeDocument().resetEdit()
# analysis_obj  mesh_obj are present
bc_obj = App.activeDocument().FemConstraintPressure
#
# must generate mesh in GUI dialog, or the mesh_obj is empty without cells
# CFD mesh must NOT second-order, or optimized, so untick those checkboxes in GUI
#
import FoamCaseWriter
writer = FoamCaseWriter.FoamCaseWriter(App.activeDocument().OpenFOAMAnalysis)
writer.write_case()
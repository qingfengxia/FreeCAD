# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2015 - Qingfeng Xia <qingfeng.xia eng ox ac uk>                 *       *
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

"""
Mesh object can not update without click
2D meshing is hard to converted to OpenFOAM, but possible to export UNV mesh
"""

import FreeCAD
import os
import sys
import time

__title__ = "FoamCaseWriter"
__author__ = "Qingfeng Xia"
__url__ = "http://www.freecadweb.org"


import FreeCAD
if FreeCAD.GuiUp:
    from PySide.QtGui import QApplication
    from PySide.QtCore import Qt
import os.path
import CaeTools
import FoamCaseBuilder as fcb # function not depends on FreeCAD


def convert_quantity_to_MKS(input, quantity_type, unit_system="MKS"):
    """ convert non MKS unit quantity to SI MKS (metre, kg, second)
    FreeCAD default length unit is mm, not metre, thereby, area is mm^2, pressure is MPa, etc
    MKS (metre, kg, second) could be selected from "Edit->Preference", "General -> Units"
    see:
    mesh generated from FreeCAD nees to be scaled by 0.001
    transformPoints -scale "(1e-3 1e-3 1e-3)"
    """
    return input


def is_solid_mesh(fem_mesh):
    if fem_mesh.VolumeCount > 0:  # solid mesh
        return True


class FoamCaseWriter:
    """write_case() is the only public API
    """
    def __init__(self, analysis_obj):
        """analysis_obj should contains all the information needed,
        boundaryConditionList is a list of all boundary Conditions objects(FemConstraint)
        """
        self.analysis_obj = analysis_obj
        self.solver_obj = CaeTools.getSolver(analysis_obj)
        self.mesh_obj = CaeTools.getMesh(analysis_obj)
        self.bc_group = CaeTools.getConstraintGroup(analysis_obj)
        self.mesh_generated = False
        
        self.case_folder = self.solver_obj.WorkingDir + os.path.sep + self.solver_obj.InputCaseName
        #solver_name = fcb.getSolverName(self.solver_obj)  # solver_name = 'simpleFoam' 
        #template_path = fcb.getTemplate(solver_name)
        self.mesh_file_name = self.case_folder + os.path.sep + self.solver_obj.InputCaseName + u".unv"
        #solver_settings = {k:self.solver_object.property(), for k in self.solver_object.properties()}
        self.builder = fcb.BasicBuilder(self.case_folder, self.mesh_file_name)
        self.builder.setup()

    def write_case(self, updating=False):
        if FreeCAD.GuiUp:
            QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.write_mesh()
            fcb.convertMesh(self.case_folder, self.mesh_file_name, True)
            
            self.write_material()
            self.write_boundary_condition()
            
            self.write_solver_control()
            self.write_time_control()
            FreeCAD.Console.PrintMessage("{} Sucessfully write {} case to folder".format(self.solver_obj.SolverName, self.solver_obj.WorkingDir))
        except e:
            print(e)
            return False
        finally:
            if FreeCAD.GuiUp:
                QApplication.restoreOverrideCursor()
            return True

    def write_bc_faces(self, unv_mesh_file, bc_id, bc_object):
        FreeCAD.Console.PrintMessage('write face_set or patches for boundary\n')
        f = unv_mesh_file
        facet_list = []
        for o, e in bc_object.References:
            elem = o.Shape.getElement(e)
            if elem.ShapeType == 'Face':  # OpenFOAM needs only 2D face boundary for 3D model, normally
                ret = self.mesh_obj.FemMesh.getVolumesByFace(elem)
                # return a list of tuple (vol->GetID(), face->GetID())
                facet_list.extend([i[1] for i in ret])
        nr_facets = len(facet_list)
        #assert nr_facets > 0
        f.write("{:>10d}         0         0         0         0         0         0{:>10d}\n".format(bc_id,  nr_facets))
        f.writelines(bc_object.Label + "\n")
        for i in range(int(nr_facets/2)):
            f.write("         8{:>10d}         0         0         ".format(facet_list[2*i]))
            f.write("         8{:>10d}         0         0         \n".format(facet_list[2*i+1]))
        if nr_facets%2:
            f.write("         8{:>10d}         0         0         \n".format(facet_list[-1]))


    def write_bc_mesh(self, unv_mesh_file):
        FreeCAD.Console.PrintMessage('write face_set or patches for boundary\n')
        f = open(unv_mesh_file, 'a')   # appending bc to the volume mesh, which contains node and element definition, ends with '-1' 
        f.write("{:6d}\n".format(-1))  # start of a section 
        f.write("{:6d}\n".format(2467))  # group section 
        for bc_number, bc_obj in enumerate(self.bc_group):
            self.write_bc_faces(f, bc_number+1, bc_obj)
        f.write("{:6d}\n".format(-1))  # end of a section 
        f.write("{:6d}\n".format(-1))  # end of file
        f.close()

    def write_mesh(self, mesh_obj=None):
        """This is FreeCAD specific code"""
        if mesh_obj == None:
            mesh_obj = self.mesh_obj
        __objs__ = []
        __objs__.append(mesh_obj)
        print mesh_obj.FemMesh  # debug
        import Fem
        case_folder = self.solver_obj.WorkingDir + os.path.sep + self.solver_obj.InputCaseName
        mesh_file_name = case_folder + os.path.sep + self.solver_obj.InputCaseName + u".unv"
        print mesh_file_name  # debug info
        Fem.export(__objs__, mesh_file_name)
        del __objs__

        # repen this unv file and write the boundary faces
        self.write_bc_mesh(mesh_file_name)

        # convert from UNV to OpenFoam
        caseFolder = self.solver_obj.WorkingDir + os.path.sep + self.solver_obj.InputCaseName
        unvMeshFile = caseFolder + os.path.sep + self.solver_obj.InputCaseName + u".unv"
        fcb.convertMesh(caseFolder, unvMeshFile)
        
        FreeCAD.Console.PrintMessage('mesh file {} converted and scaled\n'.format(mesh_file_name))
        self.mesh_generated = True
        return mesh_file_name

    def write_material(self, material=None):
        """Air, Water, CustomedFluid, first step, default to Water"""
        pass

    def write_boundary_condition(self):
        """switch case to deal diff boundary condition, mapping FEM constrain to CFD boundary conditon
        thermal BC heat flux and or fixed temperature, volume force / load, is not implemented yet
        """
        caseFolder = self.solver_obj.WorkingDir + os.path.sep + self.solver_obj.InputCaseName
        #turbulence_model setting up here, is object oriented builder better?
        bc_settings = []
        for bc in self.bc_group:
            if bc.isDerivedFrom("Fem::ConstraintPressure"):  # pressure inlet or outlet (Revsered = True)
                if bc.Reversed == True:
                    #FreeCAD pressure unit is MPa, while OpenFoam accept only Pa
                    bc_settings.append({'name': bc.Label, "type": "outlet", "valueType": "pressureOutlet", "value": bc.Pressure*1e6})
                else:
                    bc_settings.append({'name': bc.Label, "type": "pressureInlet", "valueType": "totalPressure", "value": bc.Pressure*1e6})
            elif bc.isDerivedFrom("Fem::ConstraintForce"):  # mapping force to fluid velocity inlet or outlet
                if bc.Reversed == True:
                    bc_settings.append({'name': bc.Label, "type": "outlet", "valueType": "outFlow", "value": 0.01})
                else:
                    bc_settings.append({'name': bc.Label, "type": "velocityInlet", "valueType": "fixedValue", "value": (0.1,0,0)})  # to-do
            elif bc.isDerivedFrom("Fem::ConstraintSymmetry"):  # plane symmetry to halve the computation time
                bc_settings.append({'name': bc.Label, type: "symmetry"})
            elif bc.isDerivedFrom("Fem::ConstraintFixed"):  # wall
                bc_settings.append({'name': bc.Label, type: "wall"})
            else:
                FreeCAD.Console.PrintMessage('boundary condition not supported yet\n')
        # non-group boundary surface should be wall, print a warning msg
        self.builder.setBoundaryConditions(bc_settings)

    def write_solver_control(self):
        """ relaxRatio, fvOptions. fvControl
        """
        caseFolder = self.solver_obj.WorkingDir + os.path.sep + self.solver_obj.InputCaseName
        fcb.setRelaxationFactors(caseFolder, 0.25)  # set relaxationFactors to 0.25 for the coarse 3D mesh

    def write_time_control(self):
        """ controlDict for time information
        """
        if self.solver_obj.Transient == False:
            pass

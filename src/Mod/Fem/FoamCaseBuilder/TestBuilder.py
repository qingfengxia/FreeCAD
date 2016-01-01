# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2015 - Qingfeng Xia <qingfeng.xia iesensor.com>         *
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


from BasicBuilder import *

def test_builder():
    """assuming mesh has generated with patches name same as bc_names list
    This is only a test, it will not generate accurate result due to low mesh quality
    PyFoam/examples/CaseBuilder/lesSnappy.pfcb
    """
    using_pressure_inlet = False  # only for compressible fluid case, not implemented yet
    using_laminar_model = True  # case setup is fine for kEpsilon, but will diverge!
    using_zipped_template = True  # Failed to create case from existent tutorial case, due to OpenFOAM 3.0 is not supported by PyFoam
    using_openfoam_2x = True
    
    solver_settings = getDefaultSolverSettings()
    script_path = os.path.dirname(os.path.abspath( __file__ ))
    case="/tmp/TestCase"
    #zipped_template_file = get_template(source_path) # from solver_name to zip file

    #default to '/opt/openfoam30'
    if using_openfoam_2x:
        setFoamDir('/home/qingfeng/OpenFOAM/OpenFOAM-2.1.x/')
        setFoamVersion((2,1,0))
        print FOAM_SETTINGS['FOAM_VERSION']
        zipped_template_file = script_path + '/simpleFoamTemplate_v2.zip'
    else:
        zipped_template_file = script_path + '/simpleFoamTemplate_v3.zip'
    
    tutorial_path = getFoamDir() + os.path.sep + "tutorials/incompressible/simpleFoam/pipeCyclic"
    mesh_file = script_path + '/TestCase.unv'
    
    if using_laminar_model:
        turbulenceModel={'name': "laminar"}
        inletVelocity = (0, 0, 0.001)
    else:
        turbulenceModel={'name': "realizableKE", 'turbulentIntensity': 0.05, 'hydraulicDiameter': 0.01} 
        # 'kEpsilon' case setup is fine, but divergent for mesh quality
        inletVelocity = (0, 0, 0.1)
    if using_zipped_template:
        template_path = zipped_template_file
    else:
        template_path = tutorial_path
  
    if using_pressure_inlet:   # compressible flow only, currently not supported yet!
        inlet={'name': "Inlet", 'type': "pressureInlet", 'valueType': "totalPressure", 'value': 1.0, 'turbulenceSettings': turbulenceModel}
    else:
        inlet={'name': "Inlet", 'type': "velocityInlet", 'valueType': "fixedValue", 'value': inletVelocity, 'turbulenceSettings': turbulenceModel}
        #inlet={'name': "Inlet", 'type': "velocityInlet", 'valueType': "flowRateInletVelocity", 'value': 0.01}

    outlet={'name': "PressureOutlet", 'type': "outlet", 'valueType': "pressureOutlet", 'value': 0.0}
    #outlet={'name': "PressureOutlet", 'type': "outlet", 'valueType': "outFlow", 'value': 0.0, 'turbulenceSettings': turbulenceModel}

    
    case_builder = BasicBuilder(case, mesh_file, solver_settings, template_path)
    case_builder.setup()
    convertMesh(case, mesh_file, True)
    case_builder.setTurbulenceProperties(turbulenceModel)
    #case_builder.fluidProperties = {'nu': 1e-5}
    #print case_builder.fluidProperties
    case_builder.setFluidProperties({'nu': 1e-5})
    case_builder.setBoundaryConditions([inlet, outlet])
    case_builder.setInternalFields({'U': inletVelocity})
    #case_builder.build()
    
    bc_names = BoundaryDict(case).patches()
    print bc_names
    
    #fvScheme file: divSchemes, fvSolution file has turbulence model specific var setting up
    setRelaxationFactors(case, 0.25)  # reduce for the coarse 3D mesh
    
    cmdline = "simpleFoam -case {}".format(case)
    print cmdline
    runFoamCommand(cmdline)  # lauch command outside please
    
if __name__ == '__main__':
    test_builder()
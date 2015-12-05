from FoamCaseBuilder import *

def test_builder():
    """assuming mesh has generated with patches name same as bc_names list
    This is only a test, it will not generate accurate result due to low mesh quality
    PyFoam/examples/CaseBuilder/lesSnappy.pfcb
    """
    using_pressure_inlet = False
    using_laminar_model = True
    using_zipped_template = True 
    # Failed, due to OpenFOAM 3.0 is not supported by PyFoam

    solver_settings = get_default_solver_settings()
    script_path = os.path.dirname(os.path.abspath( __file__ ))
    case="/tmp/TestCase"
    #zipped_template_file = get_template(source_path) # from solver_name to zip file
    zipped_template_file = script_path + '/simpleFoamTemplate_v3.zip'
    tutorial_path = get_foam_dir() + os.path.sep+ "tutorials/incompressible/simpleFoam/pipeCyclic"
    mesh_file = script_path + '/cfd_files/TestCase.unv'
    
    if using_laminar_model:
        turbulenceModel={'name': "laminar"}
        inletVelocity = (0, 0, 0.001)
    else:
        turbulenceModel={'name': "kEpsilon", 'inletTurbulentIntensity': 0.05, 'inletTurbulentMixingLength': 0.01} 
        # 'kEpsilon' case setup is fine, but divergent for mesh quality
        inletVelocity = (0, 0, 0.001)
    if using_zipped_template:
        create_case_from_template(zipped_template_file, case)
    else:
        create_case_from_template(tutorial_path, case)
    set_turbulence_properties(case, turbulenceModel)

    bd = BoundaryDict(case)
    bc_names = bd.patches()
    print bc_names
    init_boundary_condition(case, bc_names, turbulenceModel)
    
    reduce_relaxationFactors(case)  # set relaxationFactors to 0.25 for the coarse 3D mesh
    
    if using_pressure_inlet:   # compressible flow only, currently not supported yet!
        inlet={'name': "PressureInlet", 'type': "pressureInlet", 'value_type': "totalPressure", 'value': 1.0, 'turbulence_model': turbulenceModel}
        set_transport_properties(case, solver_settings, 'nu',1e-4)  #default , air, 1e-6
    else:
        inlet={'name': "PressureInlet", 'type': "velocityInlet", 'value_type': "fixedValue", 'value': inletVelocity, 'turbulence_model': turbulenceModel}
    set_internal_field(case,'U', inletVelocity)
    #inlet={'name': "PressureInlet", 'type': "velocityInlet", 'value_type': "flowRateInletVelocity", 'value': 0.01, 'turbulence_model': turbulenceModel}
    set_bc(case, inlet)

    #outlet={'name': "PressureOutlet", 'type': "outlet", 'value_type': "pressureOutlet", 'value': 0.0, 'turbulence_model': turbulenceModel}
    outlet={'name': "PressureOutlet", 'type': "outlet", 'value_type': "outFlow", 'value': 0.0, 'turbulence_model': turbulenceModel}
    set_bc(case, outlet)
    #set_outlet_bc(case, "PressureOutlet", "pressureOutlet", "0", turbulenceModel)
    
    cmdline = "simpleFoam -case {}".format(case)
    print cmdline
    #launch_cmdline(cmdline)
    
if __name__ == '__main__':
    test_builder()
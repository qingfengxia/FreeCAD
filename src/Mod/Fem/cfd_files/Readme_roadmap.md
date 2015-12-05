==================
FoamCFDSolver
===================

### Software prerequisits for Testing

test on ubuntu 14.04

OpenFoam 2.x can be installed from repo, which will install the correct Paraview

Basically, I need several progam on PATH, like icoFoam, paraview, paraFoam
Can be easily done by source a bash script in your .bashrc

see [OpenFoam quick startup guide]()



## CFD Roadmap

### Phase I demonstration 

- CaeAnalysis: class should operate on diff category of solvers
- CaseSolver: extending Fem::FemSolverObject
- FoamCaseWriter: OpenFOAM case writer, the key part is meshing and case setup
- Fixed material as air or water
- Use fem::constraint Constraint mapping: 
    Force->Velocity (Displacement is missing), 
    Pressure->Pressure, Symmetry is missing (Pulley), 
    PressureOutlet (Gear), VelocityOutlet(Bearing),

- Use exteranal result viewer paraview
    CFD is cell base solution, while FEM is node base. It is not easy to reuse ResultObject 
    volPointInterpolation - interpolate volume field to point field;

### Phase II general usability

- FluidMaterail: discussion with community for standardizing Material model, 
   also design for other CAE analysis EletroMagnetics
- CFD boundary conditions

- More AnalysisType supported, 
   
- CFD mesh with viscous layer and hex meshcell supported
- Unsteady case support
- SolverControlTaskPanel: better solver parameter control


### Phase III  FSI 

- The best way to do that will be in Salome, 

- AnalysisCoupler.py
list of CaeAnalysis instances,  add_analysis()  add_time()
timeStep, currentTime,  adaptiveTimeStep=False
historicalTimes chain up all historical case data file. 

static multiple solvers are also possible

- feature request from FreeCADGui
NamedSelection: coupling of faces/interfaces
Part section: build3DFromCavity buildEnclosureBox




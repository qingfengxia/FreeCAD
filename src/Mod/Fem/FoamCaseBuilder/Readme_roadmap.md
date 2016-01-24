
## Foam CaseBuilder for FreeCAD Roadmap

### Phase I demonstration 

- CaeAnalysis: class should operate on diff category of solvers
- CaseSolver: extending Fem::FemSolverObject, factory pattern, create solver from name
- FoamCaseWriter: OpenFOAM case writer, the key part is meshing and case setup
- Fixed material as air or water
- 3D UNV meshing writing function, FreeCAD mesh export does not write boundary elements
- Use fem::constraint Constraint mapping: 
    Force->Velocity (Displacement is missing), 
    Pressure->Pressure, Symmetry is missing (Pulley), 
    PressureOutlet (Gear), VelocityOutlet(Bearing),

- Use exteranal result viewer paraview
    CFD is cell base solution, while FEM is node base. It is not easy to reuse ResultObject 
    volPointInterpolation - interpolate volume field to point field;

### Phase II general usability

- FluidMaterial: discussion with community for standardizing Material model, 
   also design for other CAE analysis EletroMagnetics
- CFD boundary conditions toolbar buttons

- More AnalysisType supported, transient, possible heat transfer simulation
   
- CFD mesh with viscous layer and hex meshcell supported

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




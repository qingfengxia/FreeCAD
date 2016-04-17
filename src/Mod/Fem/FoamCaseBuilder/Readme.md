==================
#FoamCaseBuilder
==================

Qingfeng Xia
Jan 24, 2016
updated: April 17, 2016


### Introduction

FoamCaseBuilder aims to setup OpenFOAM case from python script, based on PyFoam. 

Merging FEM and CFD into a single processing pipeline (solver -> analysis -> AnalysisControlTaskPanel) is given up. 
CFD case setup code should be independent from CalculiX code, to reduce work to merge with master each time. 

### OpenFoam is designed for POSIX, but possible on windows

Possible routes: 
- FreeFoam+cygwin; 
- docker as the OpenFoam official done (launched in 2015);  
see [windows support in Docker](http://www.openfoam.com/download/install-windows.php).
I have not tried to call a command in docker Linux Image from windows. 
- ubuntu on windows (Annouced in April 2016)

### Software prerequisits for Testing (Linux ONLY!!!)

Test only on ubuntu 14.04

OpenFoam 2.x/3.0 can be installed from repo, which will also install the correct Paraview.  Please install OpenFoam 3.0 to default location /opt/, as if the FoamCaseBuilder default to 3.0 version if it can not detect the OpenFoam version.

Also install PyFoam, which can be done via "pip install PyFoam", on linux, FreeCAD reuses the system python 2.7, so PyFoam is accessible from FreeCAD. It is GPL software? can not be copy to FreeCAD source. 

see [installation guide](http://www.openfoam.com/download/install-binary.php) If it is not for your linux ver, just try your package manager
see [OpenFoam quick startup guide](http://www.openfoam.org/)
see [tutorials](http://cfd.direct/openfoam/user-guide/) 

Basically, I need several programs on PATH and some env var exported, like icoFoam, paraview, paraFoam. This be easily done by source a bash script(/opt/openfoam30/etc/bashrc.sh) in your ~/.bashrc, but there is a serious issue,  this script can not been sourced to system wide, like /etc/profile,  user can not log into desktop once source this. Nevertheless, I failed to run Popen(cmd, Terminal=True) , which I wish it can simulate run a program in a new terminal (which will source ~/.bashrc).

default to openfoam installation path: "/opt/openfoam30/" , as in Ubuntu 14.04
runFoamCommand():
bash -c 'source /opt/openfoam30/etc/bashrc.sh & paraFoam'

### FoamCaseBuilder as an independent module

FoamCaseBuilder  is designed as working without any GUI, seen "TestBulderer.py"

git clone --branch foambuilder_pre2 https://github.com/qingfengxia/FreeCAD.git  --single-branch

Please run the "TestBulderer.py" from the FoamCaseBuilder folder, as all data file (template.zip and mesh) are relative from this folder/file

 trimmed case is copied from a zipped template file, then FoamCaseBuilder script will modify the case folder accordingly. 

### Test FoamCaseBuilder in FreeCAD

As the boundary condition/constraint GUI is finished , it is possible to test in GUI. 

I have a CfdExample.py in Mod/Fem folder,  paste the first half into FreeCAD console, it can make the example shown in my figure above.  
However, the mesh can not be re-generated from the macro/script, it needs to click Mesh Taskpanel GUI to generate mesh.

Material taskpanel is not needed in CFD mode as it is default to water. Change the viscosity in OpenFoam case setup please

### see Readme_roadmap.md for plan

Huge work is needed to make a GUI for case setup for CFD, I may just focus on making it work in script mode first. 

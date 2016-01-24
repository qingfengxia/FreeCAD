==================
#FoamCaseBuilder
==================

Qingfeng Xia
Jan 24, 2016


### Introduction

FoamCaseBuilder aims to setup OpenFOAM case from python script, based on PyFoam. 

Merging FEM and CFD into a single processing pipeline (solver -> analysis -> AnalysisControlTaskPanel) is given up. 
CFD case setup code should be independent from CalculiX code, to reduce work to merge with master each time. 

### OpenFoam is designed for POSIX, but possible on windows

possible routes: FreeFoam+cygwin; docker as the OpenFoam official done;  wine

see [windows support in Docker](http://www.openfoam.com/download/install-windows.php).
I have not tried to call a command in docker Linux Image from windows. 

### Software prerequisits for Testing (Linux ONLY!!!)

Test on ubuntu 14.04

OpenFoam 2.x/3.0 can be installed from repo, which will also install the correct Paraview.  Please install OpenFoam 3.0 to default location /opt/, as if the FoamCaseBuilder default to 3.0 version if it can not detect the OpenFoam version.

Also install PyFoam, which can be done via "pip install PyFoam", on linux, FreeCAD reuses the system python 2.7, so PyFoam is accessible from FreeCAD. It is GPL software? can not be copy to FreeCAD source. 

see [installation guide](http://www.openfoam.com/download/install-binary.php) If it is not for your linux ver, just try your package manager
see [OpenFoam quick startup guide](http://www.openfoam.org/)
see [tutorials](http://cfd.direct/openfoam/user-guide/) 

Basically, I need several progam on PATH and some env var exported, like icoFoam, paraview, paraFoam. This be easily done by source a bash script(/opt/openfoam30/etc/bashrc.sh) in your ~/.bashrc, but there is a serious issue,  this script can not been sourced to system wide, like /etc/profile,  user can not log into desktop once source this. Nevertheless, I failed to run Popen(cmd, Terminal=True) , which I wish it can simulate run a program in a new terminal (which will source ~/.bashrc).

Could some one help out this? making /opt/openfoam30/etc/bashrc.sh  sourced before Popen().

### Test FoamCaseBuilder independently from FreeCAD

git clone --branch foambuilder_pre1 https://github.com/qingfengxia/FreeCAD.git  --single-branch

Please run the "TestFolder.py" from the FoamCaseBuilder folder, as all data file (template.zip and mesh) are relative from this folder/file

 trimmed case is copied from a zipped template file, then FoamCaseBuilder script will modify the case folder accordingly. 

### Test FoamCaseBuilder from FreeCAD

As the boundary condition/constraint GUI is not designed, it is not necessary to test this part for the moment. 

I have a CfdExample.py in FEM folder,  paste this into FreeCAD, can make the example shown in my figure above.  
However, the mesh can not be re-generated from the macro/script, it needs to click GUI to generate mesh.
Material taskpanel need to re-opened to select a material, while it is not needed in CFD for the moment, it is default to Air. 
Maybe, I should record a vidoe to show in later stage.

### see Readme_roadmap.md for plan

Huge work is needed to make a GUI for case setup for CFD, I may just focus on making it work in script mode first. 

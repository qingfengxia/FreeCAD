# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2015 - Qingfeng Xia <qingfeng.xia eng ox ac uk>         *
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
This script help setup OpenFOAM case as boundary conditions setup in Ansys Fluent/CFX
OpenFOAM for windows is available now: http://www.openfoam.com/products/openfoam-windows.php
docker container in VirtualBox, also  ubuntu on windows 10 may run OpenFOAM directly in the future
decomposePar should generate the boundary automatically
Phase I: incompressible laminar and RAS turbulent flow:
2D mesh, GGI and dynamic mesh will not be supported here
"""

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.RunDictionary.BoundaryDict import BoundaryDict
from PyFoam.Applications.PlotRunner import PlotRunner
from PyFoam.FoamInformation import foamVersionString, foamVersionNumber
from PyFoam.ThirdParty.six import print_, string_types, iteritems
import numbers
import os, os.path
#import PyFoam.Error, etc

DEFAULT_FOAM_DIR = '/opt/openfoam30'
DEFAULT_FOAM_VERSION = (3,0,0)
FOAM_SETTINGS = {"FOAM_DIR": None, "FOAM_VERSION": None}

def setFoamDir(dir):
    if os.path.exists(dir) and os.path.isdir(dir):
        if os.path.exists(dir + os.path.sep + "etc/bashrc"):
            FOAM_SETTINGS['FOAM_DIR'] = dir
    else:
        print_("Warning: {} is not an existent folder to set as foam_dir".format(dir))

def setFoamVersion(ver):
    FOAM_SETTINGS['FOAM_VERSION'] = ver
    
def getFoamDir():
    """$WM_PROJECT_DIR PyFoam.PyFomaInformation.foamVersionNumber()"""
    if FOAM_SETTINGS['FOAM_DIR']:
        return FOAM_SETTINGS['FOAM_DIR']
    elif "WM_PROJECT_DIR" in os.environ:
        return os.environ["WM_PROJECT_DIR"]
    else:
        print("""Environment var 'WM_PROJECT_DIR' is not defined nor FOAM_DIR is set, 
                 fallback to default {}""".format(DEFAULT_FOAM_DIR))
        return DEFAULT_FOAM_DIR
    
def getFoamVersion():
    """ `export WM_PROJECT_VERSION=3.0.0` in /opt/openfoam30/etc/bashrc
    """
    if FOAM_SETTINGS['FOAM_VERSION']:
        return FOAM_SETTINGS['FOAM_VERSION']
    elif 'WM_PROJECT_VERSION' in os.environ:
        return tuple([int(s) for s in os.environ['WM_PROJECT_VERSION'].split('.')])
    else:
        print("""environment var 'WM_PROJECT_VERSION' or _FOAM_VERSION is not defined\n,
              fallback to default {}""".format(DEFAULT_FOAM_VERSION))
        return DEFAULT_FOAM_VERSION

    #return foamVersionNumber()  # PyFoam.foamVersionString()

def isFoamExtend():
    #how to detect?
    if getFoamDir().find('ext') > 0:
        return True
    else:
        return False

def getFoamExtendVersion():
    pass

#supported_species_models = set([])
supported_multiphase_models = set(['singlePhase', 'twoLiquidMixing', 'twoPhaseEuler', 'multiphaseImmiscible'])

######################################################################


""" access dict as property of class
class PropDict(dict):
    def __init__(self, *args, **kwargs):
        super(PropDict, self).__init__(*args, **kwargs)
        #first letter lowercase conversion by mapping: 
        f = lambda s : s[0].lower() + s[1:]
        d = {f(k):v for k,v in self.iteritems()}
        self.__dict__ = d  # self
"""
        
def getDefaultSolverSettings():
    return {
            'parallel': False,
            'compressible': False,
            'nonNewtonian': False, 
            'compressible': False,
            'porous':False,
            'dynamicMeshing':False,
            'transient':False,
            'turbulenceModel': 'laminar',
            #
            'heatTransfering':False,
            'conjugate': False
            #'radiationModel': 'noRadiation',
            #'conbustionModel': 'noConbustion',
            #'viscoelasticModel':
            #
            #'lagrangianPhaseModel': 'singlePhase',
            #'multiPhaseModel': 'singlePhase'
            }  # containing all setting properties


"""
## incompressible
icoFoam is transient solver for incompressible, laminar flow of Newtonian fluids.
pimpleFoam is large time-step transient solver for incompressible (merged PISO-SIMPLE).
pisoFoam is transient solver for incompressible flow.
simpleFoam is steady-state solver for compressible, turbulent flow
Turbulence modelling is generic, i.e. laminar, RAS or LES may be selected.

## Heat Transferring is not yet implemented
buoyantBoussinesqSimpleFoam: Steady-state solver for buoyant, turbulent flow of incompressible fluids
buoyantSimpleFoam: Steady-state solver for buoyant, turbulent flow of compressible fluids
radiation model can be applied to all those solvers

## compressible      
sonicDyMFoam, sonicFoam, sonicLiquidFoam
rhoCentralFoam rhoPimpleFoam  rhoSimpleFoam   
rhoPorousSimpleFoam  rhoPimpleDyMFoam  rhoCentralDyMFoam

## multiphaseModels, speciesModels
cavitatingFoam                   multiphaseEulerFoam
compressibleInterDyMFoam         multiphaseInterDyMFoam
compressibleInterFoam            multiphaseInterFoam
compressibleMultiphaseInterFoam  potentialFreeSurfaceDyMFoam
driftFluxFoam                    potentialFreeSurfaceFoam
interDyMFoam                     reactingMultiphaseEulerFoam
interFoam                        reactingTwoPhaseEulerFoam
interMixingFoam                  twoLiquidMixingFoam
interPhaseChangeDyMFoam          twoPhaseEulerFoam
interPhaseChangeFoam

## lagrangian
coalChemistryFoam                reactingParcelFilmFoam
DPMFoam                          reactingParcelFoam
icoUncoupledKinematicParcelFoam  simpleReactingParcelFoam
MPPICFoam                        sprayFoam

## foam-extend 3.0 has viscoelastic solver and coupled, multisolver, mechanic
"""
def getSolverName(settings):
    """ LES model relies on the case template for wall functions and turbulenceProperties
    """
    if settings['turbulenceModel'] == "LES":
        if settings['compressible']:
            return 'rhoPimpleFoam'
        else:
            return 'pisoFoam'
    if settings['turbulenceModel'] == "DNS":
        return 'dnsFoam'
    if settings['heatTransfering']:
        if settings['dynamicMeshing'] or settings['porous'] or settings['nonNewtonian']:
            print_("Error: no matched solver for heat transfering, please develop such a solver")
            return
        if settings['transient']:
            if settings['conjugate']:
                return 'chtMultiRegionFoam'
            if settings['compressible']:
                return 'buoyantPimpleFoam'  # natural convection of compressible
            else:
                return 'buoyantBoussinesqPimpleFoam'  # natural convection of incompressible
        else:
            if settings['conjugate']:
                return 'chtMultiRegionSimpleFoam'
            if settings['compressible']:
                return 'buoyantSimpleFoam'
            else:
                return 'buoyantBoussinesqSimpleFoam'
    #if settings.MultiphaseModel != "singlePhase" or settings.ConbustionModel != "noConbustion"
    #    print_("Error: multiphase, conbustion model is not checked yet")
    #    return None
    if settings['compressible']:
        #if settings.superSonic:
            #return 'sonicFoam'
        if settings['transient']:
            if settings['dynamicMeshing']:
                return 'rhoPimpleDyMFoam'
            return 'rhoPimpleFoam'
        else:
            if settings['porous']:
                return 'rhoPorousSimpleFoam'
            return 'rhoSimpleFoam'
    else:  # incompressible:
        if settings['transient']:
            if settings['dynamicMeshing']:
                return 'pimpleDyMFoam'
            if not settings['nonNewtonian']:
                return 'pimpleFoam'  # pisoFoam
            else:
                return  'nonNewtonianIcoFoam'
        else:
            if not settings['nonNewtonian']:
                if settings['porous']:
                    return 'porousSimpleFoam'
                else:
                    return 'simpleFoam'
    #finally, reached here
    print_(" no matched solver, print solver setting and raise")
    print_(settings)
    raise Exception('Transient analysis by icoFoam has not been implemented')



"""Base on tutorials of OpenFoam 3.0, not all solver templates are tested"""
supported_RAS_solver_templates = {'simpleFoam': "tutorials/incompressible/simpleFoam/cyclicPipe",
                    'icoFoam': "tutorials/incompressible/icoFoam/elbow",
                    'pisoFoam': "tutorials/incompressible/pisoFoam/ras/cavity/",
                    'pimpleFoam': "tutorials/incompressible/pimpleFoam/TJunction",
                    'porousSimpleFoam': "tutorials/incompressible/porousSimpleFoam/",
                    'nonNewtonianIcoFoam': "tutorials/incompressible/nonNewtonianIcoFoam/",
                    #compressible
                    'rhoSimpleFoam': "tutorials/compressible/rhoSimpleFoam/squareBend",
                    'rhoPimpleFoam': "tutorials/compressible/rhoPimpleFoam/ras/angledDuct",
                    #HeatTransferring
                    'buoyantSimpleFoam': "tutorials/heatTransfer/buoyantSimpleFoam/hotRadiationRoom/",
                    'buoyantBoussinesqSimpleFoam': "tutorials/heatTransfer/buoyantBoussinesqSimpleFoam/hotRoom/"
                    }

supported_LES_solver_templates = {'pisoFoam': "tutorials/incompressible/pisoFoam/les/pitzDaily/",
                    'rhoPimpleFoam': "tutorials/compressible/rhoPimpleFoam/les/pitzDaily"
                    }
                    


def getTemplate(solver_name, using_LES=False):
    script_path = os.path.dirname(os.path.abspath( __file__ ))
    template_path = script_path + os.path.sep + os.path.sep + solver_name + "Template_v" + str(getFoamVersion()[0]) + ".zip"
    if not os.path.exists(template_path):
        if solver_name in supported_RAS_solver_templates:
            return getFoamDir() + os.path.sep + supported_RAS_solver_templates[solver_name]
        if using_LES and solver_name in supported_LES_solver_templates:
            return getFoamDir() + os.path.sep + supported_LES_solver_templates[solver_name]
    else:
        return template_path

"""create case from zipped template or existent case folder relative to $WM_PROJECT_DIR
clear the mesh and boundary setup, but keep the dict under system/ constant/ 
<solver_name>Template_v3.zip: case folder structure without mesh and initialisation of boundary in folder case/0/
registered dict  from solver name: tutorials/incompressible/icoFoam/elbow/
"""
def createCaseFromTemplate(output_path, source_path, backup_path=None):
    import shutil
    if backup_path and os.path.isdir(output_path):
        shutil.move(output_path, backup_path)
    if os.path.isdir(output_path):
        shutil.rmtree(output_path)
    #
    if not source_path[-4:] == ".zip":  # create case from existent case folder
        if not os.path.isabs(source_path) and source_path.find("tutorials")>0:
            source_path = getFoamDir() + os.path.sep + source_path
            if not os.path.isdir(source_path):
                 print_("Error: template case {} is not a directory".format(source_path))
        shutil.copytree(source_path, output_path)
        mesh_dir = os.path.join(output_path, "constant", "polyMesh")
        init_dir = output_path + os.path.sep + "0"
        if os.path.isdir(mesh_dir):
            shutil.rmtree(mesh_dir)
        if os.path.isdir(output_path + os.path.sep +"0.org") and not os.path.isdir(init_dir):
            shutil.move(output_path + os.path.sep +"0.org", init_dir)
        else:
            print_("Error: template case {} has no 0 or 0.orig subfolder".format(source_path))

        if os.path.isdir(init_dir):
            for var in list_var(output_path):
                #os.remove(os.path.join(init_dir, var))
                f = ParsedParameterFile(os.path.join(init_dir, var))  # Failed for OpenFOAM 3.0
                f["boundaryField"] = {}
                f.writeFile()
        #clean history data, etc.
        if os.path.isfile(output_path + os.path.sep +"Allrun.sh"):
            os.remove(output_path + os.path.sep +"Allrun.sh")
    else:  # zipped case template
        template_path = source_path
        if os.path.isfile(template_path):
            import zipfile
            with zipfile.ZipFile(source_path, "r") as z:
                z.extractall(output_path)  #auto replace existent case setup without warning
        else:
            print_("Error: template case {} not found".format(source_path))


def createCaseFromScratch(tutorial_path, output_path):
    """build case structure from string template"""
    pass
    

##################################################################
def convertMesh(case, mesh_file, scaling=False):
    """ see all mesh conversion tool: 
    CAD has mm as length unit usually, while CFD meshing using SI metre"""
    if mesh_file[-4:] == ".unv":
        cmdline = "ideasUnvToFoam -case {} {}".format(case, mesh_file)
        runFoamCommand(cmdline)
        changeBoundaryType(case, 'defaultFaces', 'wall')  # unique to ideasUnvToFoam
        #Most CAD software is use MM as the basic unit, while CFD uses metre
        if scaling:
            cmdline='transformPoints -case {} -scale "(1e-3 1e-3 1e-3)"'.format(case)
        else:
            cmdline='transformPoints -case {}'.format(case)
        runFoamCommand(cmdline)
    if mesh_file[-4:] == ".geo":  # GMSH mesh
        pass


def listBoundaryNames(case):
    return BoundaryDict(case).patches()


def changeBoundaryType(case, bc_name, type):
    f = BoundaryDict(case)
    if bc_name in f.patches():
        f[bc_name]['type'] = type
    else:
        print_("boundary `{}` not found, so boundary type is not changed".format(bc_name))
    f.writeFile()
    
    

def runFoamCommand(cmdline, printing=False):
    """ source foam_dir/etc/bashrc before run foam related program
    PyFoam.Runner
    """
    #"""
    OF_path = getFoamDir()
    env_setup_script = "source {}/etc/bashrc".format(OF_path)
    cmd = "/bin/bash -c '{} && {}'".format(env_setup_script , cmdline)
    print_("Run command: {}", cmd)
    os.system(cmd)
    """
    from subprocess import Popen, PIPE
    #process = Popen(cmdline, stdout=PIPE, stderr=PIPE, shell=True,executable='/bin/bash')

    OF_path = getFoamDir()
    env_setup_script = "source {}/etc/bashrc && ".format(OF_path)
    print_("/bin/bash -c '{} {}'".format(env_setup_script , cmdline))
    process = Popen("/bin/bash -c '{} {}'".format(env_setup_script , cmdline),stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    exitCode = process.returncode

    if (exitCode == 0):
        if printing:
            print_(stdout)
    else:
        if printing:
            print_(stdout)
            print_(stderr)
        else:
            raise Exception(cmdline, exitCode)
    """
        
def plotSolverProgress(case):
    """GNUplot to plot convergence progress of simulation"""
    pass
    
    
def clearCase(case):
    runFoamCommand("rm -rf {}".format(case) )
    

def editCase(casepath):
    import subprocess
    import sys
    path = casepath
    if sys.platform == 'darwin':
        def openFolder(path):
            subprocess.check_call(['open', '--', path])
    elif "linux" in sys.platform:  # python 2: linux2 linux3, but 'linux' for python3
        def openFolder(path):
            subprocess.check_call(['xdg-open', '--', path])
    elif sys.platform == 'win32':
        def openFolder(path):
            subprocess.check_call(['explorer', path])
    openFolder()
    
def showResult(case):
    runFoamCommand("paraFoam -case {}".format(case) )   
    
    
###############################################################################
def getDict(dict_file, key):
    if isinstance(key, string_types) and key.find('/')>=0:
        group = [k for k in key.split('/') if k]
    elif isinstance(key, list) or isinstance(key, tuple):
        group = [s for s in key if isinstance(s, string_types)]
    else:
        print_("Warning: input key is not string or sequence type, return None".format(key))
        return None

    f = ParsedParameterFile(dict_file)
    if len(group) >= 1:
        d = f
        for i in range(len(group)-1):
            if group[i] in d:
                d = d[group[i]]
            else:
                return None
        if group[-1] in d:
            return d[group[-1]]
        else:
            return None


def formatValue(v):
    if isinstance(v, string_types) or isinstance(v, numbers.Number):
        return v
    elif isinstance(v, list) or isinstance(v, tuple):  # or isinstance(v, tupleProxy))
        return "({} {} {})".format(v[0], v[1], v[2])
    else:
        raise Exception("Error: vector input {} is not string or sequence type, return zero vector string")

    
def formatList():
    pass
    
def setDict(dict_file, key, value):
    """all parameters are string type, accept, None or empty string
    dict_file: file must exist, checked by caller
    key
    value: None or empty string  will delet such key
    """
    
    if isinstance(key, string_types) and key.find('/')>=0:
        group = [k for k in key.split('/') if k]
    elif isinstance(key, list) or isinstance(key, tuple):
        group = [s for s in key if isinstance(s, string_types)]
    else:
        print_("Warning: input key is not string or sequence type, so do nothing but return".format(key))
        return
        
    f = ParsedParameterFile(dict_file)        
    if len(group) == 3:
        d = f[group[0]][group[1]]  # at most 3 levels, assuming it will auto create not existent key
    elif len(group) == 2:
        d = f[group[0]]
    else:
        d = f
    k = group[-1]
    

    if value:  # 
        d[k] = formatValue(value)
    elif key in d:
        del d[k]  #if None, or empty string is specified, delete this key
    else:
        print_('Warning: check parameters for set_dict() key={} value={}'.format(key, value))
    f.writeFile()

#################################topoSet, multiregion#####################################

"""
cellSet, faceSet, pointSet, '/system/topoSetDict'
source: BoxToCells/patchToCells/fieldToCell
https://openfoamwiki.net/index.php/TopoSet
"""
def listZones(case):
    pass  # check topoSetDict file???  mesh file folder should have a file 
    
"""
conjugate heat transfer model needs multi-region
"""
def listRegions(case):
    pass


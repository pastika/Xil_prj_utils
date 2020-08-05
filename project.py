import click
import yaml
import os
import shutil
from glob import glob
from . import prj_creation

def parseConfigFile(options):


    with open(options["projectcfg"], "r") as cfg:
        try:
            projectCfgDict = yaml.safe_load(cfg)
        except yaml.YAMLError as exc:
            print("Failed to parse config yaml, yaml error follows:")
            print(exc)
            exit()

    # list all possible projects and exit 
    if options["list"]:
        print(", ".join(projectCfgDict.keys()))
        exit(0)

    return projectCfgDict

def selectProjectAndSpecialize(options, ctxobj):

    projectCfgDict = ctxobj['projectCfgDoc']
    
    # select desired project
    try:
        projectCfg = projectCfgDict[options["projectname"]]
    except KeyError:
        print("Requested project \"%s\" not found in cfg file"%options["projectname"])
        exit()

    projectCfg["baseDirName"] = options["projectname"]
    projectCfg["basePath"] = ctxobj["projectBase"]
    
    # override 
    if "boardPart" in options:
        try:
            projectCfg["boardPart"] = options["boardpart"]
        except KeyError:
            print("Option \"boardPart\" missing for requested project \"%s\""%options["projectname"])
            exit()

    return projectCfg


def createProject(projectCfg):

    #check if directory exists
    if os.path.exists(projectCfg["baseDirName"]):
        print("Project dir %(dbn)s already exists. Use './project clean %(dbn)s' to remove it (DO NOT SIMPLY DELETE IT)."%{"dbn": projectCfg["baseDirName"]})
        exit()
    
    #create directory
    os.mkdir(projectCfg["baseDirName"])
    os.chdir(projectCfg["baseDirName"])

    #make softlink in directory
    os.symlink(os.path.relpath(os.path.join(projectCfg["basePath"], "project")), projectCfg["baseDirName"])
    
    # create golden xpr
    prj_creation.generate_golden(projectCfg["project"], projectCfg["device"], projectCfg["boardPart"])

    # add source to xpr
    prj_creation.update_filesets("golden.xpr", projectCfg["project"], projectCfg["primaryFilelist"])
    

def cleanProject(projectCfg):
    #rm project dir
    if os.path.lexists(projectCfg["baseDirName"]):
        shutil.rmtree(projectCfg["baseDirName"])

    # clean up all bd directories
    with open(projectCfg["primaryFilelist"], "r") as cfg:
        try:
            fileListDict = yaml.safe_load(cfg)
        except yaml.YAMLError as exc:
            print("Failed to parse file yaml, yaml error follows:")
            print(exc)
            exit()

    if "bd" in fileListDict:
        for bd in fileListDict["bd"]:
            path = os.path.dirname(bd)
            fname = os.path.basename(bd)

            #delete everything in bd folder except the bd
            for fp in glob(os.path.join(path, "*")):
                if not fname == os.path.basename(fp):
                    try:
                        shutil.rmtree(fp)
                    except NotADirectoryError:
                        os.remove(fp)
                    except OSError:
                        #maybe its a softlink
                        os.remove(fp)

def createDeviceTree(projectCfg):
    #create xsa file
    basePath = projectCfg["basePath"]
    create_xsa_script = os.path.abspath(os.path.join(basePath, "prj_utils/tcl/create_xsa.tcl"))
    create_dt_overlay_script = os.path.abspath(os.path.join(basePath, "prj_utils/tcl/create_dt_overlay.tcl"))
    dtPath  = os.path.join(basePath, projectCfg["baseDirName"], "device-tree")
    dtFile = os.path.join(dtPath, projectCfg["project"].replace("xpr","xsa"))
    prj_path = os.path.join(basePath, projectCfg["baseDirName"])
    prj_name = os.path.join(basePath, projectCfg["baseDirName"], projectCfg["project"])
    repoPath = os.path.join(basePath, "shared/device-tree-xlnx")
    
    if not os.path.exists(dtPath):
        os.mkdir(dtPath)

    os.chdir(prj_path)

    os.system('vivado -mode batch -source %s -tclargs %s'%(create_xsa_script, "%s %s"%(prj_name, dtFile)))

    #create device tree overlay
    os.chdir(dtPath)
    # MAKE processor an option in yaml
    os.system('xsct %s %s'%(create_dt_overlay_script, "%s %s %s"%(dtFile, repoPath, "psu_cortexa53_0")))

    
@click.group(invoke_without_command=True)
@click.option("--projectcfg", "-p", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "projects.yaml")),     help="Cfg file defining avaliable projects in yaml format")
@click.option("--boardpart",  "-b",                              help="Override default board part specification")
@click.option("--list",       "-l", default=False, is_flag=True, help="List all avaliable projects")
@click.pass_context
def project(ctx, projectcfg, boardpart, list):
    ctx.ensure_object(dict)
    ctx.obj['projectCfgDoc'] = parseConfigFile(ctx.params)
    ctx.obj['projectBase'] = os.path.abspath(os.path.dirname(__file__) + "/..")

    if ctx.invoked_subcommand is None and not list:
        click.echo(ctx.get_help())

@project.command()
@click.argument("projectname")
@click.pass_context
def create(ctx, projectname):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    createProject(projectCfg)
    
@project.command()
@click.argument("projectname")
@click.pass_context
def clean(ctx, projectname):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    cleanProject(projectCfg)
    

@project.command()
@click.argument("projectname")
@click.pass_context
def devicetree(ctx, projectname):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    createDeviceTree(projectCfg) 


if __name__ == "__main__":
    project()

import click
import yaml
import os
import sys
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
            exit(-1)

    # list all possible projects and exit 
    if options["list"]:
        print('\n'.join(projectCfgDict.keys()))
        exit(0)

    return projectCfgDict

def selectProjectAndSpecialize(options, ctxobj):

    projectCfgDict = ctxobj['projectCfgDoc']
    
    # select desired project
    try:
        projectCfg = projectCfgDict[options["projectname"]]
    except KeyError:
        print("Requested project \"%s\" not found in cfg file"%options["projectname"])
        exit(-1)

    projectCfg["baseDirName"] = options["projectname"]
    projectCfg["basePath"] = ctxobj["projectBase"]
    
    # override 
    if "boardPart" in options:
        try:
            projectCfg["boardPart"] = options["boardpart"]
        except KeyError:
            print("Option \"boardPart\" missing for requested project \"%s\""%options["projectname"])
            exit(-1)

    return projectCfg


def createProject(projectCfg):

    #check if directory exists
    if os.path.exists(projectCfg["baseDirName"]):
        print("Project dir %(dbn)s already exists. Use './project clean %(dbn)s' to remove it (DO NOT SIMPLY DELETE IT)."%{"dbn": projectCfg["baseDirName"]})
        exit(-1)
    
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
            exit(-1)

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

# stage: 0 = synthesis, 1 = implementation, 2 = bitfile, 3 = device tree overlay
def projectBuild(projectCfg, stage_start, stage_end, force=False):
    #create xsa file
    basePath = projectCfg["basePath"]
    create_xsa_script = os.path.abspath(os.path.join(basePath, "prj_utils/tcl/build_project.tcl"))
    #create_dt_overlay_script = os.path.abspath(os.path.join(basePath, "prj_utils/tcl/create_dt_overlay.tcl"))
    dtPath  = os.path.join(basePath, projectCfg["baseDirName"], "device-tree")
    dtFile = os.path.join(dtPath, projectCfg["project"].replace("xpr","xsa"))
    prj_path = os.path.join(basePath, projectCfg["baseDirName"])
    prj_name = os.path.join(basePath, projectCfg["baseDirName"], projectCfg["project"])
    repoPath = os.path.join(basePath, "shared/device-tree-xlnx")
    
    if not os.path.exists(dtPath):
        os.mkdir(dtPath)

    os.chdir(prj_path)

    return os.system('vivado -mode batch -source %s -tclargs %s'%(create_xsa_script, " ".join([prj_name, os.path.splitext(projectCfg["project"])[0], repoPath, "psu_cortexa53_0", str(int(os.cpu_count()/2)), str(stage_start), str(stage_end), str(1 if force else 0)])))

    
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

@project.resultcallback()
def process_pipeline(status, projectcfg, boardpart, list):
    # The following makes sure it works ~everywhere 
    # E.g. in some systems, status==512 and sys.exit(512) is reported as 0 (success)...
    if status:
        sys.exit(-1)
        
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
@click.option("--force",       "-f", default=False, is_flag=True, help="Force redo of synthesis")
def synthesis(ctx, projectname, force):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    return projectBuild(projectCfg, 0, 0, force) 

@project.command()
@click.argument("projectname")
@click.pass_context
@click.option("--force",       "-f", default=False, is_flag=True, help="Force redo of implementation")
def implementation(ctx, projectname, force):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    return projectBuild(projectCfg, 1, 1, force) 

@project.command()
@click.argument("projectname")
@click.pass_context
@click.option("--force",       "-f", default=False, is_flag=True, help="Force redo of bitfile generation")
def bitfile(ctx, projectname, force):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    return projectBuild(projectCfg, 2, 2, force) 
    
@project.command()
@click.argument("projectname")
@click.pass_context
def devicetree(ctx, projectname):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    return projectBuild(projectCfg, 3, 3) 

@project.command()
@click.argument("projectname")
@click.pass_context
@click.option("--force",       "-f", default=False, is_flag=True, help="Force full rebuild")
def build(ctx, projectname, force):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    return projectBuild(projectCfg, 0, 3, force) 

if __name__ == "__main__":
    project()

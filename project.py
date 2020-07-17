import click
import yaml
import os
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

def selectProjectAndSpecialize(options, projectCfgDict):
    # select desired project
    try:
        projectCfg = projectCfgDict[options["projectname"]]
    except KeyError:
        print("Requested project \"%s\" not found in cfg file"%options["projectname"])
        exit()

    projectCfg["baseDirName"] = options["projectname"]
        
    # override 
    if "boardPart" in options:
        try:
            projectCfg["boardPart"] = options["boardpart"]
        except KeyError:
            print("Option \"boardPart\" missing for requested project \"%s\""%options["projectname"])
            exit()

    return projectCfg

def prepareFilelist(projectCfg):
    # construct full filelist (add error checking)
    with open(projectCfg["primaryFilelist"]) as primaryFile:
        filelist = primaryFile.read()

    # parse any secondary files lists that exist (Add error checking)
    if "secondaryFilelists" in  projectCfg:
        for key, secondaryFileName in projectCfg["secondaryFilelists"].items():
            with open(secondaryFileName) as secondaryFile:
                filelist = filelist%{key : secondaryFile.read()}

    # scrub blank lines from filelist
    filelist = "\n".join([s.strip() for s in filelist.splitlines() if s.strip()])

    return filelist

def createProject(projectCfg):

    #check if directory exists
    if os.path.exists(projectCfg["baseDirName"]):
        print("Project dir %(dbn)s already exists. Use './project clean %(dbn)s' to remove it."%{"dbn": projectCfg["baseDirName"]})
        exit()
    
    #create directory
    os.mkdir(projectCfg["baseDirName"])
    os.chdir(projectCfg["baseDirName"])
    
    # create golden xpr
    prj_creation.generate_golden(projectCfg["project"], projectCfg["device"], projectCfg["boardPart"])

    # add source to xpr
    prj_creation.update_filesets("golden.xpr", projectCfg["project"], projectCfg["primaryFilelist"])
    

def cleanProject(projectCfg):
    #rm project dir
    if os.path.lexists(projectCfg["baseDirName"]):
        os.system("rm -r %s"%projectCfg["baseDirName"])

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
            files = ["hdl/", "shared/", "synth/", "*.bxml", "*_ooc.xdc", "sim/", "ipshared/", "hw_handoff/", "ip/", "ui/"]
            for file in files:
                filepath = os.path.join(path, file)
                for fp in glob(filepath):
                    if os.path.lexists(fp):
                        os.system("rm -r %s"%fp)

    
@click.group(invoke_without_command=True)
@click.option("--projectcfg", "-p", default="projects.yaml",     help="Cfg file defining avaliable projects in yaml format")
@click.option("--boardpart",  "-b",                              help="Override default board part specification")
@click.option("--list",       "-l", default=False, is_flag=True, help="List all avaliable projects")
@click.pass_context
def project(ctx, projectcfg, boardpart, list):
    ctx.ensure_object(dict)
    ctx.obj['projectCfgDoc'] = parseConfigFile(ctx.params)

    if ctx.invoked_subcommand is None and not list:
        click.echo(ctx.get_help())

@project.command()
@click.argument("projectname")
@click.pass_context
def create(ctx, projectname):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj['projectCfgDoc'])

    createProject(projectCfg)
    
@project.command()
@click.argument("projectname")
@click.pass_context
def clean(ctx, projectname):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj['projectCfgDoc'])

    cleanProject(projectCfg)
    


if __name__ == "__main__":
    project()

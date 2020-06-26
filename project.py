import click
import yaml
import os

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

    filelist = prepareFilelist(projectCfg)

    print(filelist)


@click.group(invoke_without_command=True)
@click.option("--projectcfg", "-p", default="projects.yaml",     help="Cfg file defining avaliable projects in yaml format")
@click.option("--boardpart",  "-b",                              help="Override default board part specification")
@click.option("--list",       "-l", default=False, is_flag=True, help="Override default board part specification")
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
    


if __name__ == "__main__":
    project()

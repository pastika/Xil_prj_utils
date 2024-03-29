import click
import yaml
import os
import sys
import shutil
import builtins
from glob import glob
from . import prj_creation
from . import uHALXML_creation

def xil_cpu_count():
    # Vivado does not like more than 32
    ncpus = int(os.cpu_count()/2)
    return min(ncpus,32)

def parseConfigFile(options):

    with open(options["projectcfg"], "r") as cfg:
        try:
            projectCfgDict = yaml.safe_load(cfg)
        except yaml.YAMLError as exc:
            print("Failed to parse config yaml, yaml error follows:")
            print(exc)
            exit(-1)

    # list all possible projects and exit 
    if "list" in options and options["list"]:
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
    projectCfg["project"] = options["projectname"]+".xpr"
    projectCfg["basePath"] = ctxobj["projectBase"]
    
    # override 
    if "boardPart" in options:
        try:
            projectCfg["boardPart"] = options["boardpart"]
        except KeyError:
            print("Option \"boardPart\" missing for requested project \"%s\""%options["projectname"])
            exit(-1)

    return projectCfg

def readDesignYaml(projectCfg):
    #read filelist as yaml 
    filelist =  projectCfg["primaryFilelist"];
    basePath="..";  
    with open(os.path.join(basePath, filelist), "r") as cfg:
        try:
            fileListDict = yaml.safe_load(cfg)
        except yaml.YAMLError as exc:
            print("Failed to parse file yaml, yaml error follows:")
            print(exc)
            exit()
    #read extrafilelist if exist 
    try:    
        extrafilelist =  projectCfg["extraFilelist"];
        try: #extend (if list) , append (if str) xdc
            if isinstance(extrafilelist["xdc"], builtins.list):
                fileListDict["xdc"].extend(extrafilelist["xdc"]); 
            else:
                fileListDict["xdc"].append(extrafilelist["xdc"]);               
        except Exception as e:
            print(e)
            pass
        try: # override bd 
            if isinstance(extrafilelist["xdc"], builtins.list):  
                fileListDict["bd"] = extrafilelist["bd"];  
            else:
                fileListDict["bd"] = [extrafilelist["bd"]];     
        except: 
            pass
    except: 
        pass

    return fileListDict

def addGitFilters():
    os.system('git config filter.jsonsort.clean "python3 -E -m json.tool --sort-keys"')

def createProject(projectCfg):

    addGitFilters()

    #check if directory exists
    if os.path.exists(projectCfg["baseDirName"]):
        print("Project dir %(dbn)s already exists. Use './project clean %(dbn)s' to remove it (DO NOT SIMPLY DELETE IT)."%{"dbn": projectCfg["baseDirName"]})
        exit(-1)
    
    #create directory
    os.mkdir(projectCfg["baseDirName"])
    os.chdir(projectCfg["baseDirName"])

    #make softlink in directory
    os.symlink(os.path.relpath(os.path.join(projectCfg["basePath"], "project")), projectCfg["baseDirName"])
    
    #read filelist as yaml
    fileListDict = readDesignYaml(projectCfg)
    
    # create golden xpr
    prj_creation.generate_golden(projectCfg["project"], projectCfg["device"], projectCfg["boardPart"], fileListDict["ip_repo"])

    # print (fileListDict["xdc"])
    # print (fileListDict["bd"])
    # add source to xpr
    return prj_creation.update_filesets("golden.xpr", projectCfg["project"], fileListDict)
    

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

    #read extrafilelist if exist 
    try:    
        extrafilelist =  projectCfg["extraFilelist"];
        try: # override bd 
            if isinstance(extrafilelist["xdc"], list):  
                fileListDict["bd"] = extrafilelist["bd"];  
            else:
                fileListDict["bd"] = [extrafilelist["bd"]];   
        except: 
            pass
    except: 
        pass
        
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
    device_tree_xsct_script = os.path.abspath(os.path.join(basePath, "prj_utils/tcl/device_tree_xsct.tcl"))
    #create_dt_overlay_script = os.path.abspath(os.path.join(basePath, "prj_utils/tcl/create_dt_overlay.tcl"))
    dtPath  = os.path.join(basePath, projectCfg["baseDirName"], "device-tree")
    dtFile = os.path.join(dtPath, projectCfg["project"].replace("xpr","xsa"))
    bitFileName = projectCfg["project"].replace("xpr","bit")
    prj_path = os.path.join(basePath, projectCfg["baseDirName"])
    prj_name = os.path.join(basePath, projectCfg["baseDirName"], projectCfg["project"])
    repoPath = os.path.join(basePath, "prj_utils/device-tree-xlnx")
    processor = projectCfg["processor"]

    # device tree file name
    dtsiname = "pl.dtsi"

    if not os.path.exists(dtPath):
        os.mkdir(dtPath)

    os.chdir(prj_path)

    retval = os.system('vivado -mode batch -source %s -tclargs %s'%(create_xsa_script, " ".join([prj_name, os.path.splitext(projectCfg["project"])[0], repoPath, processor, str(xil_cpu_count()), str(stage_start), str(stage_end), str(1 if force else 0)])))
    retval = os.system('xsct %s %s'%(device_tree_xsct_script, " ".join([prj_name, os.path.splitext(projectCfg["project"])[0], repoPath, processor, str(xil_cpu_count()), str(stage_start), str(stage_end), str(1 if force else 0)])))

    if retval: return retval

    #if this is a zynq-7000 we need to translate the bit file to a bin file
    if "ps7_cortexa9" in processor:
        with open("translate_bit.bif", "w") as bif:
            bif.write("all:\n{\n  ./%s\n}\n"%bitFileName)
        os.system("bootgen -image translate_bit.bif -arch zynq -o ./%s.bin -w -process_bitstream bin"%bitFileName)
    
    #generate the dtbo from the dtsi file
    if not (stage_start > 3 or stage_end < 3):
        os.chdir(dtPath)

        # Compile the full dtsi for posterity
        if "customdtsi" in projectCfg:
            cdtsi = os.path.join(basePath, projectCfg["customdtsi"])
            retval_dtsi = os.system('dtc -W no-unit_address_vs_reg -@ -i . -i %s -I dts %s -O dts -o pl-full.dtsi'%(os.path.dirname(os.path.realpath(cdtsi)), cdtsi))
        else:
            retval_dtsi = os.system('dtc -W no-unit_address_vs_reg -@ -I dts %s -O dts -o pl-full.dtsi'%dtsiname)
        if retval_dtsi: return retval_dtsi

        # Compile the full dtbo
        if "customdtsi" in projectCfg:
            cdtsi = os.path.join(basePath, projectCfg["customdtsi"])
            retval_dtbo = os.system('dtc -W no-unit_address_vs_reg -@ -i . -i %s -I dts %s -O dtb -o pl.dtbo'%(os.path.dirname(os.path.realpath(cdtsi)), cdtsi))
        else:
            retval_dtbo = os.system('dtc -W no-unit_address_vs_reg -@ -I dts %s -O dtb -o pl.dtbo'%dtsiname)
        return retval_dtbo

    return retval
    
    
def projectReport(projectCfg, run="impl_1"):
    #create xsa file
    basePath = projectCfg["basePath"]
    create_report_script = os.path.abspath(os.path.join(basePath, "prj_utils/tcl/create_reports.tcl"))
    #create_dt_overlay_script = os.path.abspath(os.path.join(basePath, "prj_utils/tcl/create_dt_overlay.tcl"))
    dtPath  = os.path.join(basePath, projectCfg["baseDirName"], "device-tree")
    dtFile = os.path.join(dtPath, projectCfg["project"].replace("xpr","xsa"))
    prj_path = os.path.join(basePath, projectCfg["baseDirName"])
    prj_name = os.path.join(basePath, projectCfg["baseDirName"], projectCfg["project"])
    
    os.chdir(prj_path)

    return os.system('vivado -mode batch -source %s -tclargs %s'%(create_report_script, " ".join([prj_name, os.path.splitext(projectCfg["project"])[0], str(xil_cpu_count()), run])))
    
@click.group(invoke_without_command=True)
@click.option("--projectcfg", "-p", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "projects.yaml")),     help="Cfg file defining avaliable projects in yaml format")
@click.option("--boardpart",  "-b",                              help="Override default board part specification")
@click.pass_context
def project(ctx, projectcfg, boardpart):
    ctx.ensure_object(dict)
    ctx.obj['projectCfgDoc'] = parseConfigFile(ctx.params)
    ctx.obj['projectBase'] = os.path.abspath(os.path.dirname(__file__) + "/..")

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

@project.result_callback()
def process_pipeline(status, projectcfg, boardpart):
    # The following makes sure it works ~everywhere 
    # E.g. in some systems, status==512 and sys.exit(512) is reported as 0 (success)...
    if status:
        sys.exit(-1)
        
@project.command(short_help="Create specified project if it does not already exist")
@click.argument("projectname")
@click.pass_context
def create(ctx, projectname):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    return createProject(projectCfg)
    
@project.command(short_help="Remove all generated file for selected project")
@click.argument("projectname")
@click.pass_context
def clean(ctx, projectname):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    cleanProject(projectCfg)
    

@project.command(short_help="Run synthesis on project")
@click.argument("projectname")
@click.pass_context
@click.option("--force",       "-f", default=False, is_flag=True, help="Force redo of synthesis")
def synthesis(ctx, projectname, force):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    return projectBuild(projectCfg, 0, 0, force) 

@project.command(short_help="Run implementation on project")
@click.argument("projectname")
@click.pass_context
@click.option("--force",       "-f", default=False, is_flag=True, help="Force redo of implementation")
def implementation(ctx, projectname, force):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    return projectBuild(projectCfg, 1, 1, force) 

@project.command(short_help="Generates bistream file")
@click.argument("projectname")
@click.pass_context
@click.option("--force",       "-f", default=False, is_flag=True, help="Force redo of bitfile generation")
def bitfile(ctx, projectname, force):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    return projectBuild(projectCfg, 2, 2, force) 
    
@project.command(short_help="Generates device tree overlay file")
@click.argument("projectname")
@click.pass_context
def devicetree(ctx, projectname):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    return projectBuild(projectCfg, 3, 3) 

@project.command(short_help="Run full build (synthesis through device tree generation)")
@click.argument("projectname")
@click.pass_context
@click.option("--force",       "-f", default=False, is_flag=True, help="Force full rebuild")
def build(ctx, projectname, force):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    return projectBuild(projectCfg, 0, 3, force) 

@project.command(short_help="Create uHAL XML address tables")
@click.argument("projectname")
@click.pass_context
def xml(ctx, projectname):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    os.chdir(os.path.join(projectCfg["basePath"], projectCfg["baseDirName"]))
    
    #read filelist as yaml
    fileListDict = readDesignYaml(projectCfg)

    uHALXML_creation.produceuHALXML("device-tree/pl.dtbo", fileListDict["ip_repo"], "..", "uHAL_xml")

    return 0

@project.command(short_help="Create post implementation reports")
@click.argument("projectname")
@click.pass_context
@click.option("--run",       "-r", default="impl_1", help="Select run to create reports for")
def report(ctx, projectname, run):
    params = ctx.params
    params.update(ctx.parent.params)

    projectCfg = selectProjectAndSpecialize(params, ctx.obj)

    return projectReport(projectCfg, run)

@project.command(short_help="Lists all avaliable projects")
@click.pass_context
def list(ctx):
    params = ctx.params
    params.update(ctx.parent.params)

    params["list"] = True

    parseConfigFile(params)

@project.command(short_help="Add git filters")
@click.pass_context
def addgitfilters(ctx):
    params = ctx.params
    params.update(ctx.parent.params)

    addGitFilters()
    
if __name__ == "__main__":
    project()

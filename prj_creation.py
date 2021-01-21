import yaml
import os

filesets_header = '  <FileSets Version="1" Minor="31">\n'
  
src_header = """    <FileSet Name="sources_1" Type="DesignSrcs" RelSrcDir="$PSRCDIR/sources_1">
      <Filter Type="Srcs"/>"""

src_entry = """      <File Path="$PPRDIR/%(filePath)s">
%(fileinfo)s
%(attributes)s
        </FileInfo>
      </File>"""

src_entry_v   = '        <FileInfo>'
src_entry_vhd = '        <FileInfo SFType="VHDL2008">'
src_entry_synth = '          <Attr Name="UsedIn" Val="synthesis"/>'
src_entry_impl  = '          <Attr Name="UsedIn" Val="implementation"/>'
src_entry_sim   = '          <Attr Name="UsedIn" Val="simulation"/>'


src_footer = """      <Config>
        <Option Name="DesignMode" Val="RTL"/>
        <Option Name="TopModule" Val="%(topmod)s"/>
      </Config>
    </FileSet>"""
  
xdc_header = """    <FileSet Name="constrs_1" Type="Constrs" RelSrcDir="$PSRCDIR/constrs_1">
          <Filter Type="Constrs"/>"""
  
xdc_entry = """      <File Path="$PPRDIR/%(filePath)s">
        <FileInfo>
          <Attr Name="UsedIn" Val="implementation"/>
        </FileInfo>
      </File>"""
  
xdc_footer = """      <Config>
        <Option Name="TargetConstrsFile" Val="$PPRDIR/%(filePath)s"/>
        <Option Name="ConstrsType" Val="XDC"/>
      </Config>
    </FileSet>"""
  
sim_entry = """    <FileSet Name="sim_1" Type="SimulationSrcs" RelSrcDir="$PSRCDIR/sim_1">
      <Filter Type="Srcs"/>
      <Config>
        <Option Name="DesignMode" Val="RTL"/>
        <Option Name="TopAutoSet" Val="TRUE"/>
        <Option Name="TransportPathDelay" Val="0"/>
        <Option Name="TransportIntDelay" Val="0"/>
        <Option Name="SrcSet" Val="sources_1"/>
      </Config>
    </FileSet>"""
  
util_entry = """    <FileSet Name="utils_1" Type="Utils" RelSrcDir="$PSRCDIR/utils_1">
      <Filter Type="Utils"/>
      <Config>
        <Option Name="TopAutoSet" Val="TRUE"/>
      </Config>
    </FileSet>"""
  
filesets_footer = '  </FileSets>'


def update_filesets (golden_name, prj_name, filelist, basePath=".."):
    # ---------------------------
    # Constants
    # ---------------------------
    
    
    # ---------------------------
    # Step 1: remove source files
    # ---------------------------
    
    print("------------------------------------------------------------------------------------------")
    print("[info]: start")
    print("------------------------------------------------------------------------------------------")
   # file copy -force $prj_name $prj_name.bak
  
    outfile = ""
    outFileLines = []
  
    with open(golden_name, "r") as infile:
        foundFileSets = False
        for line in infile:
            if "<FileSets" in line:
                foundFileSets = True
                outFileLines.append("%(FileSets)s\n")
            elif "FileSets>" in line:
                foundFileSets = False
            elif not foundFileSets:
                outFileLines.append(line)
    
    outfile = "".join(outFileLines)

    # ---------------------------
    # Step 2a: search for source files
    # ---------------------------

    fileSetsStrs = []
    
    with open(os.path.join(basePath, filelist), "r") as cfg:
        try:
            fileListDict = yaml.safe_load(cfg)
        except yaml.YAMLError as exc:
            print("Failed to parse file yaml, yaml error follows:")
            print(exc)
            exit()

    # ---------------------------
    # Step 2b: format source files
    # ---------------------------
    
    if (("hdl" in fileListDict and (fileListDict["hdl"] is not None) and len(fileListDict["hdl"]) > 0) or
        ("bd"  in fileListDict and (fileListDict["bd"] is not None) and len(fileListDict["bd"]) > 0) or
        ("coe" in fileListDict and (fileListDict["coe"] is not None) and len(fileListDict["coe"]) > 0)):
      
        fileSetsStrs.append(filesets_header)
      
        fileSetsStrs.append(src_header)

        # add hdl files
        if "hdl" in fileListDict and fileListDict["hdl"] is not None:
            for filePath in fileListDict["hdl"]:
                filePath = os.path.relpath(os.path.join(basePath, filePath))
                if os.path.isfile(filePath):
                    ext = os.path.splitext(filePath)[1]
                    print("[info]: Added src file %s"%filePath)
                    fileSetsStrs.append(src_entry%{"filePath": filePath,
                                                   "fileinfo": src_entry_vhd if ext == ".vhd" else src_entry_v,
                                                   "attributes": "\n".join([src_entry_synth, src_entry_impl, src_entry_sim]) })

        # add bd files
        if "bd"  in fileListDict and fileListDict["bd"] is not None:
            for filePath in fileListDict["bd"]:
                filePath = os.path.relpath(os.path.join(basePath, filePath))
                if os.path.isfile(filePath):
                    ext = os.path.splitext(filePath)[1]
                    print("[info]: Added bd file %s"%filePath)
                    fileSetsStrs.append(src_entry%{"filePath": filePath,
                                                   "fileinfo": src_entry_v,
                                                   "attributes": "\n".join([src_entry_synth, src_entry_impl, src_entry_sim]) })

        # --- scan again for coe that must be just above the top level definition
        if "coe" in fileListDict and fileListDict["coe"] is not None:
            for filePath in fileListDict["coe"]:
                filePath = os.path.relpath(os.path.join(basePath, filePath))
                if os.path.isfile(filePath):
                    ext = os.path.splitext(filePath)[1]
                    print("[info]: Added coe file %s"%filePath)
                    fileSetsStrs.append(src_entry%{"filePath": filePath,
                                                   "fileinfo": src_entry_v,
                                                   "attributes": "\n".join([src_entry_synth]) })


        fileSetsStrs.append(src_footer%{"topmod":fileListDict["topMod"]})
    
    # ---------------------------
    # Step 3b: format constraints
    # ---------------------------
    if ("xdc" in fileListDict and len(fileListDict["xdc"]) > 0) or ("xdcTarget" in fileListDict):
        fileSetsStrs.append(xdc_header)
      
        for filePath in fileListDict["xdc"]:
            filePath = os.path.relpath(os.path.join(basePath, filePath))
            if os.path.isfile(filePath):
                print("[info]: Added xdc file %s"%filePath)
                fileSetsStrs.append(xdc_entry%{"filePath": filePath,})

        if "xdcTarget" in fileListDict:
            if not (fileListDict["xdcTarget"] in fileListDict["xdc"]):
                filePath = os.path.relpath(os.path.join(basePath, fileListDict["xdcTarget"]))
                if os.path.isfile(filePath):
                    print("[info]: Added xdc file %s"%filePath)
                    fileSetsStrs.append(xdc_entry%{"filePath": filePath,})
            fileSetsStrs.append(xdc_footer%{"filePath": filePath,})
        else:
            filePath = os.path.relpath(os.path.join(basePath, filePath))
            fileSetsStrs.append(xdc_footer%{"filePath": filePath,})

    fileSetsStrs.append(sim_entry)
    fileSetsStrs.append(util_entry)
  
    fileSetsStrs.append(filesets_footer)
  
    # ---------------------------
    # Step 4: combine the two parts
    # ---------------------------
    outfile = outfile%{"FileSets": "\n".join(fileSetsStrs)}
    with open(prj_name, "w") as fout:
        fout.write(outfile)


    # ---------------------------
    # Step 5: Generate wrapper for all bd files 
    # ---------------------------

    if "bd"  in fileListDict:
        for filePath in fileListDict["bd"]:
            fileName = os.path.basename(filePath)
            os.system('vivado -mode batch -source %s -tclargs %s'%(os.path.abspath(os.path.join(basePath, "prj_utils/tcl/create_bd_wrapper.tcl")), "%s %s"%(prj_name, fileName)))
    

    print("------------------------------------------------------------------------------------------")
    print("[info]: done")
    print("------------------------------------------------------------------------------------------")


template_xpr = """<?xml version="1.0" encoding="UTF-8"?>
<!-- Product Version: Vivado v2019.2 (64-bit)              -->
<!--                                                         -->
<!-- Copyright 1986-2019 Xilinx, Inc. All Rights Reserved.   -->

<Project Version="7" Minor="44" Path="./%(proj_name)s">
  <DefaultLaunch Dir="$PRUNDIR"/>
  <Configuration>
    <Option Name="Id" Val="b2c57fb812724b1f8aa4de52fe4c2167"/>
    <Option Name="Part" Val="%(dev_name)s"/>
    <Option Name="CompiledLibDir" Val="$PCACHEDIR/compile_simlib"/>
    <Option Name="CompiledLibDirXSim" Val=""/>
    <Option Name="CompiledLibDirModelSim" Val="$PCACHEDIR/compile_simlib/modelsim"/>
    <Option Name="CompiledLibDirQuesta" Val="$PCACHEDIR/compile_simlib/questa"/>
    <Option Name="CompiledLibDirIES" Val="$PCACHEDIR/compile_simlib/ies"/>
    <Option Name="CompiledLibDirXcelium" Val="$PCACHEDIR/compile_simlib/xcelium"/>
    <Option Name="CompiledLibDirVCS" Val="$PCACHEDIR/compile_simlib/vcs"/>
    <Option Name="CompiledLibDirRiviera" Val="$PCACHEDIR/compile_simlib/riviera"/>
    <Option Name="CompiledLibDirActivehdl" Val="$PCACHEDIR/compile_simlib/activehdl"/>
    <Option Name="TargetLanguage" Val="VERILOG"/>
    <Option Name="BoardPart" Val="%(board_part)s"/>
    <Option Name="BoardPartRepoPaths" Val="$PPRDIR/../shared/board_parts"/>
    <Option Name="ActiveSimSet" Val="sim_1"/>
    <Option Name="DefaultLib" Val="xil_defaultlib"/>
    <Option Name="ProjectType" Val="Default"/>
    <Option Name="IPRepoPath" Val="$PPRDIR/../shared/ip_repo"/>
    <Option Name="IPOutputRepo" Val="$PIPUSERFILESDIR/ipstatic"/>
    <Option Name="IPCachePermission" Val="disable"/>
    <Option Name="EnableCoreContainer" Val="TRUE"/>
    <Option Name="CreateRefXciForCoreContainers" Val="FALSE"/>
    <Option Name="IPUserFilesDir" Val="$PIPUSERFILESDIR"/>
    <Option Name="IPStaticSourceDir" Val="$PIPUSERFILESDIR/ipstatic"/>
    <Option Name="EnableBDX" Val="FALSE"/>
    <Option Name="DSABoardId" Val="te0820_2eg_1e"/>
    <Option Name="WTXSimLaunchSim" Val="0"/>
    <Option Name="WTModelSimLaunchSim" Val="0"/>
    <Option Name="WTQuestaLaunchSim" Val="0"/>
    <Option Name="WTIesLaunchSim" Val="0"/>
    <Option Name="WTVcsLaunchSim" Val="0"/>
    <Option Name="WTRivieraLaunchSim" Val="0"/>
    <Option Name="WTActivehdlLaunchSim" Val="0"/>
    <Option Name="WTXSimExportSim" Val="11"/>
    <Option Name="WTModelSimExportSim" Val="11"/>
    <Option Name="WTQuestaExportSim" Val="11"/>
    <Option Name="WTIesExportSim" Val="11"/>
    <Option Name="WTVcsExportSim" Val="11"/>
    <Option Name="WTRivieraExportSim" Val="11"/>
    <Option Name="WTActivehdlExportSim" Val="11"/>
    <Option Name="GenerateIPUpgradeLog" Val="TRUE"/>
    <Option Name="XSimRadix" Val="hex"/>
    <Option Name="XSimTimeUnit" Val="ns"/>
    <Option Name="XSimArrayDisplayLimit" Val="1024"/>
    <Option Name="XSimTraceLimit" Val="65536"/>
    <Option Name="SimTypes" Val="rtl"/>
    <Option Name="SimTypes" Val="bfm"/>
    <Option Name="SimTypes" Val="tlm"/>
    <Option Name="SimTypes" Val="tlm_dpi"/>
    <Option Name="MEMEnableMemoryMapGeneration" Val="TRUE"/>
    <Option Name="DcpsUptoDate" Val="TRUE"/>
  </Configuration>
  <FileSets Version="1" Minor="31">
  </FileSets>
  <Simulators>
    <Simulator Name="XSim">
      <Option Name="Description" Val="Vivado Simulator"/>
      <Option Name="CompiledLib" Val="0"/>
    </Simulator>
    <Simulator Name="ModelSim">
      <Option Name="Description" Val="ModelSim Simulator"/>
    </Simulator>
    <Simulator Name="Questa">
      <Option Name="Description" Val="Questa Advanced Simulator"/>
    </Simulator>
    <Simulator Name="IES">
      <Option Name="Description" Val="Incisive Enterprise Simulator (IES)"/>
    </Simulator>
    <Simulator Name="Xcelium">
      <Option Name="Description" Val="Xcelium Parallel Simulator"/>
    </Simulator>
    <Simulator Name="VCS">
      <Option Name="Description" Val="Verilog Compiler Simulator (VCS)"/>
    </Simulator>
    <Simulator Name="Riviera">
      <Option Name="Description" Val="Riviera-PRO Simulator"/>
    </Simulator>
  </Simulators>
  <Runs Version="1" Minor="11">
    <Run Id="synth_1" Type="Ft3:Synth" SrcSet="sources_1" Part="%(synth_part)s>
      <Strategy Version="1" Minor="2">
        <StratHandle Name="Vivado Synthesis Defaults" Flow="Vivado Synthesis 2018"/>
        <Step Id="synth_design"/>
      </Strategy>
      <GeneratedRun Dir="$PRUNDIR" File="gen_run.xml"/>
      <ReportStrategy Name="Vivado Synthesis Default Reports" Flow="Vivado Synthesis 2018"/>
      <Report Name="ROUTE_DESIGN.REPORT_METHODOLOGY" Enabled="1"/>
      <RQSFiles/>
    </Run>
    <Run Id="impl_1" Type="Ft2:EntireDesign" Part="%(impl_part)s>
      <Strategy Version="1" Minor="2">
        <StratHandle Name="Vivado Implementation Defaults" Flow="Vivado Implementation 2018"/>
        <Step Id="init_design"/>
        <Step Id="opt_design"/>
        <Step Id="power_opt_design"/>
        <Step Id="place_design"/>
        <Step Id="post_place_power_opt_design"/>
        <Step Id="phys_opt_design"/>
        <Step Id="route_design"/>
        <Step Id="post_route_phys_opt_design"/>
        <Step Id="write_bitstream"/>
      </Strategy>
      <GeneratedRun Dir="$PRUNDIR" File="gen_run.xml"/>
      <ReportStrategy Name="Vivado Implementation Default Reports" Flow="Vivado Implementation 2018"/>
      <Report Name="ROUTE_DESIGN.REPORT_METHODOLOGY" Enabled="1"/>
      <RQSFiles/>
    </Run>
  </Runs>
  <Board>
    <Jumpers/>
  </Board>
  <DashboardSummary Version="1" Minor="0">
    <Dashboards>
      <Dashboard Name="default_dashboard">
        <Gadgets>
          <Gadget Name="drc_1" Type="drc" Version="1" Row="2" Column="0">
            <GadgetParam Name="REPORTS" Type="string_list" Value="impl_1#impl_1_route_report_drc_0 "/>
          </Gadget>
          <Gadget Name="gadget_1" Type="timing" Version="1" Row="3" Column="0">
            <GadgetParam Name="REPORTS" Type="string_list" Value="impl_1#impl_1_route_report_timing_summary_0 "/>
            <GadgetParam Name="VIEW.TYPE" Type="string" Value="graph"/>
          </Gadget>
          <Gadget Name="methodology_1" Type="methodology" Version="1" Row="2" Column="1">
            <GadgetParam Name="REPORTS" Type="string_list" Value="impl_1#impl_1_route_report_methodology_0 "/>
          </Gadget>
          <Gadget Name="power_1" Type="power" Version="1" Row="1" Column="0">
            <GadgetParam Name="REPORTS" Type="string_list" Value="impl_1#impl_1_route_report_power_0 "/>
          </Gadget>
          <Gadget Name="timing_1" Type="timing" Version="1" Row="0" Column="1">
            <GadgetParam Name="REPORTS" Type="string_list" Value="impl_1#impl_1_route_report_timing_summary_0 "/>
          </Gadget>
          <Gadget Name="utilization_1" Type="utilization" Version="1" Row="0" Column="0">
            <GadgetParam Name="REPORTS" Type="string_list" Value="synth_1#synth_1_synth_report_utilization_0 "/>
            <GadgetParam Name="RUN.STEP" Type="string" Value="synth_design"/>
            <GadgetParam Name="RUN.TYPE" Type="string" Value="synthesis"/>
          </Gadget>
          <Gadget Name="utilization_2" Type="utilization" Version="1" Row="1" Column="1">
            <GadgetParam Name="REPORTS" Type="string_list" Value="impl_1#impl_1_place_report_utilization_0 "/>
            <GadgetParam Name="VIEW.TYPE" Type="string" Value="graph"/>
          </Gadget>
        </Gadgets>
      </Dashboard>
      <CurrentDashboard>default_dashboard</CurrentDashboard>
    </Dashboards>
  </DashboardSummary>
</Project>"""

def generate_golden (prj_name, dev_name, brd_name):
    # constants   
    synth_suffix = '" ConstrsSet="constrs_1" Description="Vivado Synthesis Defaults" AutoIncrementalCheckpoint="false" WriteIncrSynthDcp="false" State="current" Dir="$PRUNDIR/synth_1" IncludeInArchive="true"'
    impl_suffix = '" ConstrsSet="constrs_1" Description="Default settings for Implementation." AutoIncrementalCheckpoint="false" WriteIncrSynthDcp="false" State="current" Dir="$PRUNDIR/impl_1" SynthRun="synth_1" IncludeInArchive="true" GenFullBitstream="true"'
    
    outfile = template_xpr%{"proj_name"  : prj_name,
                            "dev_name"   : dev_name,
                            "board_part" : brd_name,
                            "synth_part" : "".join([dev_name, synth_suffix]),
                            "impl_part"  : "".join([dev_name, impl_suffix]),}

    with open("golden.xpr", "w") as fout:
        fout.write(outfile)

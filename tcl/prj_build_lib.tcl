proc prj_build {prj_name filelist top_module_name} {
  # ---------------------------
  # Constants
  # ---------------------------
  
  set filesets_header {  <FileSets Version="1" Minor="31">}
  
  set src_header_0    {    <FileSet Name="sources_1" Type="DesignSrcs" RelSrcDir="$PSRCDIR/sources_1">}
  set src_header_1    {      <Filter Type="Srcs"/>}
  
  set src_entry_0     {      <File Path="$PPRDIR/}
  set src_entry_1     {        <FileInfo>}
  set src_entry_1_vhd {        <FileInfo SFType="VHDL2008">}
  set src_entry_2     {          <Attr Name="UsedIn" Val="synthesis"/>}
  set src_entry_3     {          <Attr Name="UsedIn" Val="implementation"/>}
  set src_entry_3b    {            <Attr Name="UsedIn" Val="simulation"/>}
  set src_entry_4     {        </FileInfo>}
  set src_entry_5     {      </File>}
  
  set src_footer_0    {      <Config>}
  set src_footer_1    {        <Option Name="DesignMode" Val="RTL"/>}
  set src_footer_2    {        <Option Name="TopModule" Val="}
  set src_footer_3    {      </Config>}
  set src_footer_4    {    </FileSet>}
  
  set xdc_header_0    {    <FileSet Name="constrs_1" Type="Constrs" RelSrcDir="$PSRCDIR/constrs_1">}
  set xdc_header_1    {          <Filter Type="Constrs"/>}
  
  set xdc_entry_0     {      <File Path="$PPRDIR/}
  set xdc_entry_1     {        <FileInfo>}
  set xdc_entry_2     {          <Attr Name="UsedIn" Val="implementation"/>}
  set xdc_entry_3     {        </FileInfo>}
  set xdc_entry_4     {      </File>}
  
  set xdc_footer_0    {      <Config>}
  set xdc_footer_1    {        <Option Name="TargetConstrsFile" Val="$PPRDIR/}
  set xdc_footer_2    {        <Option Name="ConstrsType" Val="XDC"/>}
  set xdc_footer_3    {      </Config>}
  set xdc_footer_4    {    </FileSet>}
  
  set sim_entry_0     {    <FileSet Name="sim_1" Type="SimulationSrcs" RelSrcDir="$PSRCDIR/sim_1">}
  set sim_entry_1     {      <Filter Type="Srcs"/>}
  set sim_entry_2     {      <Config>}
  set sim_entry_3     {        <Option Name="DesignMode" Val="RTL"/>}
  set sim_entry_4     {        <Option Name="TopAutoSet" Val="TRUE"/>}
  set sim_entry_5     {        <Option Name="TransportPathDelay" Val="0"/>}
  set sim_entry_6     {        <Option Name="TransportIntDelay" Val="0"/>}
  set sim_entry_7     {        <Option Name="SrcSet" Val="sources_1"/>}
  set sim_entry_8     {      </Config>}
  set sim_entry_9     {    </FileSet>}
  
  set util_entry_0    {    <FileSet Name="utils_1" Type="Utils" RelSrcDir="$PSRCDIR/utils_1">}
  set util_entry_1    {      <Filter Type="Utils"/>}
  set util_entry_2    {      <Config>}
  set util_entry_3    {        <Option Name="TopAutoSet" Val="TRUE"/>}
  set util_entry_4    {      </Config>}
  set util_entry_5    {    </FileSet>}
  
  set filesets_footer {  </FileSets>}
  
  # ---------------------------
  # Step 1: remove source files
  # ---------------------------
  
  puts "------------------------------------------------------------------------------------------"
  puts "\[\info\]: start"
  puts "------------------------------------------------------------------------------------------"
 # file copy -force $prj_name $prj_name.bak

  set infile [open $prj_name r]
  set outfile [open $prj_name.dat w]
  set srclist [open $filelist r]
  
  set flag 1
  
  while { [gets $infile line] >= 0 } {
    if {[regexp {<FileSets} $line match]} {
        set flag 0
        puts $outfile "////placeholder////"
    } elseif {[regexp {FileSets>} $line match]} {
        set flag 1
    } elseif {$flag == 1} {
        #puts $line 
        puts $outfile $line
    }
  }
  
  close $outfile
  close $infile
  
  
  # ---------------------------
  # Step 2a: search for source files
  # ---------------------------
  
  set src_found 0
  set srclist [open $filelist r]
  #set srclistpath [file normalize ../../src/lst/filelist.txt]
  #puts $srclistpath
  
  while { [gets $srclist srcline] >= 0 } {
    set commented_out 0
    if {[regexp {#} $srcline match]} {
        set commented_out 1
    }  
    
    if {$commented_out == 0} {
     set filename [file normalize $srcline]
     set valid [file isfile $filename]
     if {$valid == 0} {
       puts "\[\ERROR\]: \"$filename\" not found"
       puts "------------------------------------------------------------------------------------------"
       return
       #return -level 0 -code break
     }
          
     if {$valid == 1} {
       set ext [file extension $filename]
       if {$ext == ".vhd" || $ext == ".v" || $ext == ".xci" || $ext == ".bd" || $ext == ".coe"} {
         set src_found 1
       }
     }
    }
    
  }
  close $srclist
  # ---------------------------
  # Step 2b: format source files
  # ---------------------------
  
  set srclist [open $filelist r]
  set src_out [open src_temp.dat w]
  if {$src_found == 1} {
  
    puts $src_out $filesets_header
    
    puts $src_out $src_header_0
    puts $src_out $src_header_1
  
    while { [gets $srclist srcline] >= 0 } {
      set filename [file normalize $srcline]
      set valid [file isfile $filename]
      if {$valid == 1 } {
        set ext [file extension $filename]
        if {$ext == ".vhd" || $ext == ".v" || $ext == ".xci" || $ext == ".bd"} {
          puts "\[\info\]: added src file \"$filename\""
          set entry0  "$src_entry_0$srcline\">"
          puts $src_out $entry0 
          if {$ext == ".vhd"} {
            puts $src_out $src_entry_1_vhd
          } else {
            puts $src_out $src_entry_1
          }        
          puts $src_out $src_entry_2
          if {$ext != ".vhd"} {
            puts $src_out $src_entry_3
          }
          puts $src_out $src_entry_4
          puts $src_out $src_entry_5
        }
      }
    }
    
    # --- scan again for coe that must be just above the top level definition
    close $srclist
    set srclist [open $filelist r]
    while { [gets $srclist srcline] >= 0 } {
      set filename [file normalize $srcline]
      set valid [file isfile $filename]
      if {$valid == 1 } {
        set ext [file extension $filename]
        if {$ext == ".coe"} {
          puts "\[\info\]: added coe file \"$filename\""
          set entry0  "$src_entry_0$srcline\">"
          puts $src_out $entry0 
          puts $src_out $src_entry_1 
          puts $src_out $src_entry_2
          puts $src_out $src_entry_4
          puts $src_out $src_entry_5
        }
      }
    }
    
    set footer_2 "$src_footer_2$top_module_name\"/>"
    puts $src_out $src_footer_0
    puts $src_out $src_footer_1
    puts $src_out     $footer_2
    puts $src_out $src_footer_3
    puts $src_out $src_footer_4
  }
  close $srclist
  
  # ---------------------------
  # Step 3a: search for constraints
  # ---------------------------
  set xdc_found 0
  set srclist [open $filelist r]
  while { [gets $srclist srcline] >= 0 } {
    set filename [file normalize $srcline]
    set valid [file isfile $filename]
    if {$valid == 1 } {
      set ext [file extension $filename]
      if {$ext == ".xdc"} {
        set xdc_found 1
      }
    }
  }
  close $srclist
  
  # ---------------------------
  # Step 3b: format constraints
  # ---------------------------
  set srclist [open $filelist r]
  if {$xdc_found == 1} {
  
    puts $src_out $xdc_header_0
    puts $src_out $xdc_header_1
  
    while { [gets $srclist srcline] >= 0 } {
      set filename [file normalize $srcline]
      set valid [file isfile $filename]
      if {$valid == 1 } {
        set ext [file extension $filename]
        if {$ext == ".xdc"} {
          set lastxdc $srcline
          puts "\[\info\]: added xdc file \"$filename\""
          set entry0 "$xdc_entry_0$srcline\">"
          puts $src_out $entry0
          puts $src_out $xdc_entry_1
          puts $src_out $xdc_entry_2
          puts $src_out $xdc_entry_3
          puts $src_out $xdc_entry_4
          }
      }
    }
    puts $src_out $xdc_footer_0
    set target_entry "$xdc_footer_1$lastxdc\"/>"
    puts $src_out $target_entry
    puts $src_out $xdc_footer_2
    puts $src_out $xdc_footer_3
    puts $src_out $xdc_footer_4
  }
  
  
  puts $src_out $sim_entry_0
  puts $src_out $sim_entry_1
  puts $src_out $sim_entry_2
  puts $src_out $sim_entry_3
  puts $src_out $sim_entry_4
  puts $src_out $sim_entry_5
  puts $src_out $sim_entry_6
  puts $src_out $sim_entry_7
  puts $src_out $sim_entry_8
  puts $src_out $sim_entry_9
  
  puts $src_out $util_entry_0
  puts $src_out $util_entry_1
  puts $src_out $util_entry_2
  puts $src_out $util_entry_3
  puts $src_out $util_entry_4
  puts $src_out $util_entry_5

  puts $src_out $filesets_footer

  close $srclist
  close $src_out
  
  # ---------------------------
  # Step 4: combine the two parts
  # ---------------------------
  set prjfile [open $prj_name.dat r]
  set srcfile [open src_temp.dat r]
  set outfile [open $prj_name w]
  
  while { [gets $prjfile prjline] >= 0 } {
    if {[regexp {////placeholder////} $prjline match]} {
      while { [gets $srcfile srcline] >= 0 } {puts $outfile $srcline}
    } else {
      puts $outfile $prjline
    }
  }
  close $srcfile
  close $prjfile
  close $outfile
  
  file delete $prj_name.dat
  file delete src_temp.dat
  #file copy -force $prj_name $prj_name.pre
  puts "------------------------------------------------------------------------------------------"
  puts "\[\info\]: done"
  puts "------------------------------------------------------------------------------------------"
}

proc generate {prj_name dev_name brd_name} {

  # constants   
  array set template_xpr {}

  set template_xpr(0)   {<?xml version="1.0" encoding="UTF-8"?>}
  set template_xpr(1)   {<!-- Product Version: Vivado v2019.2 (64-bit)              -->}
  set template_xpr(2)   {<!--                                                         -->}
  set template_xpr(3)   {<!-- Copyright 1986-2019 Xilinx, Inc. All Rights Reserved.   -->}
  set template_xpr(4)   {}
  set template_xpr(5)   {<Project Version="7" Minor="44" Path="./}
  set template_xpr(6)   {  <DefaultLaunch Dir="$PRUNDIR"/>}
  set template_xpr(7)   {  <Configuration>}
  set template_xpr(8)   {    <Option Name="Id" Val="b2c57fb812724b1f8aa4de52fe4c2167"/>}
  set template_xpr(9)   {    <Option Name="Part" Val="}
  set template_xpr(10)  {    <Option Name="CompiledLibDir" Val="$PCACHEDIR/compile_simlib"/>}
  set template_xpr(11)  {    <Option Name="CompiledLibDirXSim" Val=""/>}
  set template_xpr(12)  {    <Option Name="CompiledLibDirModelSim" Val="$PCACHEDIR/compile_simlib/modelsim"/>}
  set template_xpr(13)  {    <Option Name="CompiledLibDirQuesta" Val="$PCACHEDIR/compile_simlib/questa"/>}
  set template_xpr(14)  {    <Option Name="CompiledLibDirIES" Val="$PCACHEDIR/compile_simlib/ies"/>}
  set template_xpr(15)  {    <Option Name="CompiledLibDirXcelium" Val="$PCACHEDIR/compile_simlib/xcelium"/>}
  set template_xpr(16)  {    <Option Name="CompiledLibDirVCS" Val="$PCACHEDIR/compile_simlib/vcs"/>}
  set template_xpr(17)  {    <Option Name="CompiledLibDirRiviera" Val="$PCACHEDIR/compile_simlib/riviera"/>}
  set template_xpr(18)  {    <Option Name="CompiledLibDirActivehdl" Val="$PCACHEDIR/compile_simlib/activehdl"/>}
  set template_xpr(19)  {    <Option Name="TargetLanguage" Val="VERILOG"/>}
  set template_xpr(20)  {    <Option Name="BoardPart" Val="}
  set template_xpr(21)  {    <Option Name="BoardPartRepoPaths" Val="$PPRDIR/../../brd"/>}
  set template_xpr(22)  {    <Option Name="ActiveSimSet" Val="sim_1"/>}
  set template_xpr(23)  {    <Option Name="DefaultLib" Val="xil_defaultlib"/>}
  set template_xpr(24)  {    <Option Name="ProjectType" Val="Default"/>}
  set template_xpr(25)  {    <Option Name="IPRepoPath" Val="$PPRDIR/../../src/ip/custom_ip"/>}
  set template_xpr(26)  {    <Option Name="IPRepoPath" Val="$PPRDIR/../../../../shared/src/ip/custom_ip"/>}
  set template_xpr(27)  {    <Option Name="IPOutputRepo" Val="$PIPUSERFILESDIR/ipstatic"/>}
  set template_xpr(28)  {    <Option Name="IPCachePermission" Val="disable"/>}
  set template_xpr(29)  {    <Option Name="EnableCoreContainer" Val="TRUE"/>}
  set template_xpr(30)  {    <Option Name="CreateRefXciForCoreContainers" Val="FALSE"/>}
  set template_xpr(31)  {    <Option Name="IPUserFilesDir" Val="$PIPUSERFILESDIR"/>}
  set template_xpr(32)  {    <Option Name="IPStaticSourceDir" Val="$PIPUSERFILESDIR/ipstatic"/>}
  set template_xpr(33)  {    <Option Name="EnableBDX" Val="FALSE"/>}
  set template_xpr(34)  {    <Option Name="DSABoardId" Val="te0820_2eg_1e"/>}
  set template_xpr(35)  {    <Option Name="WTXSimLaunchSim" Val="0"/>}
  set template_xpr(36)  {    <Option Name="WTModelSimLaunchSim" Val="0"/>}
  set template_xpr(37)  {    <Option Name="WTQuestaLaunchSim" Val="0"/>}
  set template_xpr(38)  {    <Option Name="WTIesLaunchSim" Val="0"/>}
  set template_xpr(39)  {    <Option Name="WTVcsLaunchSim" Val="0"/>}
  set template_xpr(40)  {    <Option Name="WTRivieraLaunchSim" Val="0"/>}
  set template_xpr(41)  {    <Option Name="WTActivehdlLaunchSim" Val="0"/>}
  set template_xpr(42)  {    <Option Name="WTXSimExportSim" Val="11"/>}
  set template_xpr(43)  {    <Option Name="WTModelSimExportSim" Val="11"/>}
  set template_xpr(44)  {    <Option Name="WTQuestaExportSim" Val="11"/>}
  set template_xpr(45)  {    <Option Name="WTIesExportSim" Val="11"/>}
  set template_xpr(46)  {    <Option Name="WTVcsExportSim" Val="11"/>}
  set template_xpr(47)  {    <Option Name="WTRivieraExportSim" Val="11"/>}
  set template_xpr(48)  {    <Option Name="WTActivehdlExportSim" Val="11"/>}
  set template_xpr(49)  {    <Option Name="GenerateIPUpgradeLog" Val="TRUE"/>}
  set template_xpr(50)  {    <Option Name="XSimRadix" Val="hex"/>}
  set template_xpr(51)  {    <Option Name="XSimTimeUnit" Val="ns"/>}
  set template_xpr(52)  {    <Option Name="XSimArrayDisplayLimit" Val="1024"/>}
  set template_xpr(53)  {    <Option Name="XSimTraceLimit" Val="65536"/>}
  set template_xpr(54)  {    <Option Name="SimTypes" Val="rtl"/>}
  set template_xpr(55)  {    <Option Name="SimTypes" Val="bfm"/>}
  set template_xpr(56)  {    <Option Name="SimTypes" Val="tlm"/>}
  set template_xpr(57)  {    <Option Name="SimTypes" Val="tlm_dpi"/>}
  set template_xpr(58)  {    <Option Name="MEMEnableMemoryMapGeneration" Val="TRUE"/>}
  set template_xpr(59)  {    <Option Name="DcpsUptoDate" Val="TRUE"/>}
  set template_xpr(60)  {  </Configuration>}
  set template_xpr(61)  {  <FileSets Version="1" Minor="31">}
  set template_xpr(62)  {  </FileSets>}
  set template_xpr(63)  {  <Simulators>}
  set template_xpr(64)  {    <Simulator Name="XSim">}
  set template_xpr(65)  {      <Option Name="Description" Val="Vivado Simulator"/>}
  set template_xpr(66)  {      <Option Name="CompiledLib" Val="0"/>}
  set template_xpr(67)  {    </Simulator>}
  set template_xpr(68)  {    <Simulator Name="ModelSim">}
  set template_xpr(69)  {      <Option Name="Description" Val="ModelSim Simulator"/>}
  set template_xpr(70)  {    </Simulator>}
  set template_xpr(71)  {    <Simulator Name="Questa">}
  set template_xpr(72)  {      <Option Name="Description" Val="Questa Advanced Simulator"/>}
  set template_xpr(73)  {    </Simulator>}
  set template_xpr(74)  {    <Simulator Name="IES">}
  set template_xpr(75)  {      <Option Name="Description" Val="Incisive Enterprise Simulator (IES)"/>}
  set template_xpr(76)  {    </Simulator>}
  set template_xpr(77)  {    <Simulator Name="Xcelium">}
  set template_xpr(78)  {      <Option Name="Description" Val="Xcelium Parallel Simulator"/>}
  set template_xpr(79)  {    </Simulator>}
  set template_xpr(80)  {    <Simulator Name="VCS">}
  set template_xpr(81)  {      <Option Name="Description" Val="Verilog Compiler Simulator (VCS)"/>}
  set template_xpr(82)  {    </Simulator>}
  set template_xpr(83)  {    <Simulator Name="Riviera">}
  set template_xpr(84)  {      <Option Name="Description" Val="Riviera-PRO Simulator"/>}
  set template_xpr(85)  {    </Simulator>}
  set template_xpr(86)  {  </Simulators>}
  set template_xpr(87)  {  <Runs Version="1" Minor="11">}
  set template_xpr(88)  {    <Run Id="synth_1" Type="Ft3:Synth" SrcSet="sources_1" Part="}
  set template_xpr(89)  {      <Strategy Version="1" Minor="2">}
  set template_xpr(90)  {        <StratHandle Name="Vivado Synthesis Defaults" Flow="Vivado Synthesis 2018"/>}
  set template_xpr(91)  {        <Step Id="synth_design"/>}
  set template_xpr(92)  {      </Strategy>}
  set template_xpr(93)  {      <GeneratedRun Dir="$PRUNDIR" File="gen_run.xml"/>}
  set template_xpr(94)  {      <ReportStrategy Name="Vivado Synthesis Default Reports" Flow="Vivado Synthesis 2018"/>}
  set template_xpr(95)  {      <Report Name="ROUTE_DESIGN.REPORT_METHODOLOGY" Enabled="1"/>}
  set template_xpr(96)  {      <RQSFiles/>}
  set template_xpr(97)  {    </Run>}
  set template_xpr(98)  {    <Run Id="impl_1" Type="Ft2:EntireDesign" Part="}
  set template_xpr(99)  {      <Strategy Version="1" Minor="2">}
  set template_xpr(100)  {        <StratHandle Name="Vivado Implementation Defaults" Flow="Vivado Implementation 2018"/>}
  set template_xpr(101) {        <Step Id="init_design"/>}
  set template_xpr(102) {        <Step Id="opt_design"/>}
  set template_xpr(103) {        <Step Id="power_opt_design"/>}
  set template_xpr(104) {        <Step Id="place_design"/>}
  set template_xpr(105) {        <Step Id="post_place_power_opt_design"/>}
  set template_xpr(106) {        <Step Id="phys_opt_design"/>}
  set template_xpr(107) {        <Step Id="route_design"/>}
  set template_xpr(108) {        <Step Id="post_route_phys_opt_design"/>}
  set template_xpr(109) {        <Step Id="write_bitstream"/>}
  set template_xpr(110) {      </Strategy>}
  set template_xpr(111) {      <GeneratedRun Dir="$PRUNDIR" File="gen_run.xml"/>}
  set template_xpr(112) {      <ReportStrategy Name="Vivado Implementation Default Reports" Flow="Vivado Implementation 2018"/>}
  set template_xpr(113) {      <Report Name="ROUTE_DESIGN.REPORT_METHODOLOGY" Enabled="1"/>}
  set template_xpr(114) {      <RQSFiles/>}
  set template_xpr(115) {    </Run>}
  set template_xpr(116) {  </Runs>}
  set template_xpr(117) {  <Board>}
  set template_xpr(118) {    <Jumpers/>}
  set template_xpr(119) {  </Board>}
  set template_xpr(120) {  <DashboardSummary Version="1" Minor="0">}
  set template_xpr(121) {    <Dashboards>}
  set template_xpr(122) {      <Dashboard Name="default_dashboard">}
  set template_xpr(123) {        <Gadgets>}
  set template_xpr(124) {          <Gadget Name="drc_1" Type="drc" Version="1" Row="2" Column="0">}
  set template_xpr(125) {            <GadgetParam Name="REPORTS" Type="string_list" Value="impl_1#impl_1_route_report_drc_0 "/>}
  set template_xpr(126) {          </Gadget>}
  set template_xpr(127) {          <Gadget Name="gadget_1" Type="timing" Version="1" Row="3" Column="0">}
  set template_xpr(128) {            <GadgetParam Name="REPORTS" Type="string_list" Value="impl_1#impl_1_route_report_timing_summary_0 "/>}
  set template_xpr(129) {            <GadgetParam Name="VIEW.TYPE" Type="string" Value="graph"/>}
  set template_xpr(130) {          </Gadget>}
  set template_xpr(131) {          <Gadget Name="methodology_1" Type="methodology" Version="1" Row="2" Column="1">}
  set template_xpr(132) {            <GadgetParam Name="REPORTS" Type="string_list" Value="impl_1#impl_1_route_report_methodology_0 "/>}
  set template_xpr(133) {          </Gadget>}
  set template_xpr(134) {          <Gadget Name="power_1" Type="power" Version="1" Row="1" Column="0">}
  set template_xpr(135) {            <GadgetParam Name="REPORTS" Type="string_list" Value="impl_1#impl_1_route_report_power_0 "/>}
  set template_xpr(136) {          </Gadget>}
  set template_xpr(137) {          <Gadget Name="timing_1" Type="timing" Version="1" Row="0" Column="1">}
  set template_xpr(138) {            <GadgetParam Name="REPORTS" Type="string_list" Value="impl_1#impl_1_route_report_timing_summary_0 "/>}
  set template_xpr(139) {          </Gadget>}
  set template_xpr(140) {          <Gadget Name="utilization_1" Type="utilization" Version="1" Row="0" Column="0">}
  set template_xpr(141) {            <GadgetParam Name="REPORTS" Type="string_list" Value="synth_1#synth_1_synth_report_utilization_0 "/>}
  set template_xpr(142) {            <GadgetParam Name="RUN.STEP" Type="string" Value="synth_design"/>}
  set template_xpr(143) {            <GadgetParam Name="RUN.TYPE" Type="string" Value="synthesis"/>}
  set template_xpr(144) {          </Gadget>}
  set template_xpr(145) {          <Gadget Name="utilization_2" Type="utilization" Version="1" Row="1" Column="1">}
  set template_xpr(146) {            <GadgetParam Name="REPORTS" Type="string_list" Value="impl_1#impl_1_place_report_utilization_0 "/>}
  set template_xpr(147) {            <GadgetParam Name="VIEW.TYPE" Type="string" Value="graph"/>}
  set template_xpr(148) {          </Gadget>}
  set template_xpr(149) {        </Gadgets>}
  set template_xpr(150) {      </Dashboard>}
  set template_xpr(151) {      <CurrentDashboard>default_dashboard</CurrentDashboard>}
  set template_xpr(152) {    </Dashboards>}
  set template_xpr(153) {  </DashboardSummary>}
 set template_xpr(154) {</Project>}

  set synth_suffix {" ConstrsSet="constrs_1" Description="Vivado Synthesis Defaults" AutoIncrementalCheckpoint="false" WriteIncrSynthDcp="false" State="current" Dir="$PRUNDIR/synth_1" IncludeInArchive="true">}
  set impl_suffix  {" ConstrsSet="constrs_1" Description="Default settings for Implementation." AutoIncrementalCheckpoint="false" WriteIncrSynthDcp="false" State="current" Dir="$PRUNDIR/impl_1" SynthRun="synth_1" IncludeInArchive="true" GenFullBitstream="true">}

# "

# main

  set outfile [open ./golden.xpr w]
  
  for {set i 0} {$i < 155} {incr i} {
    # project name
    if {$i == 5} {
      set entry_prj_name "$template_xpr($i)$prj_name\">"
      puts $outfile $entry_prj_name
      } elseif {$i == 9} {
      set entry_dev_name  "$template_xpr($i)$dev_name\"/>"
      puts $outfile $entry_dev_name
      } elseif {$i == 20} {
      set entry_brd_name  "$template_xpr($i)$brd_name\"/>"
      puts $outfile $entry_brd_name
      } elseif {$i == 88} {
      set entry_dev_synth "$template_xpr($i)$dev_name$synth_suffix"
      puts $outfile $entry_dev_synth
      } elseif {$i == 98} {
      set entry_dev_impl  "$template_xpr($i)$dev_name$impl_suffix"
      puts $outfile $entry_dev_impl
    } else {
      puts $outfile $template_xpr($i)
    }
  }
  close $outfile
}

# parse args
set project [lindex $argv 0]
set prj_name [lindex $argv 1]
set repoPath [lindex $argv 2]
set processor [lindex $argv 3]
set maxThreads [lindex $argv 4]
set startPoint  [lindex $argv 5]
set endPoint  [lindex $argv 6]
set force [lindex $argv 7]

# See https://www.xilinx.com/support/documentation/sw_manuals/xilinx2019_2/ug835-vivado-tcl-commands.pdf#page=1619
set_msg_config -severity INFO -suppress
set_msg_config -severity STATUS -suppress

open_project $project

set_param general.maxThreads $maxThreads

if { $startPoint <= 0 && $endPoint >= 0 && ( $force || [get_property STATUS [get_runs synth_1]] == "Not started" || [get_property NEEDS_REFRESH [get_runs synth_1]] ) } {
    reset_run synth_1
    launch_runs synth_1 -jobs $maxThreads
    wait_on_run synth_1
}

if { [string first "ERROR" [get_property STATUS [get_runs synth_1]]] != -1 } {
    reset_msg_config -severity INFO -suppress
    reset_msg_config -severity STATUS -suppress
    error "FAILURE: SYNTHESIS ERROR!!!"
}

if { $startPoint <= 1 && $endPoint >= 1 && ( $force || [get_property STATUS [get_runs impl_1]] == "Not started" || [get_property NEEDS_REFRESH [get_runs impl_1]] ) } {
    reset_run impl_1
    launch_runs impl_1 -jobs $maxThreads
    wait_on_run impl_1
}

if { [string first "ERROR" [get_property STATUS [get_runs impl_1]]] != -1 } {
    reset_msg_config -severity INFO -suppress
    reset_msg_config -severity STATUS -suppress
    error "FAILURE: IMPLEMENTATION ERROR!!!"
}

if { $startPoint <= 2 && $endPoint >= 2 && ( $force || ([string first "route_design Complete" [get_property STATUS [get_runs impl_1]]] != -1)) } {
    launch_runs impl_1 -to write_bitstream -jobs $maxThreads
    wait_on_run impl_1
}

if { [string first "ERROR" [get_property STATUS [get_runs impl_1]]] != -1 } {
    reset_msg_config -severity INFO -suppress
    reset_msg_config -severity STATUS -suppress
    error "FAILURE: BITSTREAM ERROR!!!"
}

if { $startPoint <= 3 && $endPoint >= 3 && ([get_property STATUS [get_runs impl_1]] == "write_bitstream Complete!") } {
    write_hw_platform -force -fixed -include_bit $prj_name.xsa
    #write_hwdef design.hdf
    hsi::open_hw_design $prj_name.xsa
    hsi::set_repo_path $repoPath
    hsi::create_sw_design sw1 -proc $processor -os device_tree
    set_property CONFIG.dt_overlay true [hsi::get_os]
    hsi::generate_bsp -dir ./device-tree
}

reset_msg_config -severity INFO -suppress
reset_msg_config -severity STATUS -suppress

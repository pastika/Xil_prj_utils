# parse args
set project [lindex $argv 0]
set prj_name [lindex $argv 1]
set repoPath [lindex $argv 2]
set processor [lindex $argv 3]
set maxThreads [lindex $argv 4]

open_project $project

set_param general.maxThreads $maxThreads

reset_run synth_1
launch_runs synth_1 -jobs $maxThreads
wait_on_run synth_1

reset_run impl_1
launch_runs impl_1 -jobs $maxThreads
wait_on_run impl_1

open_run impl_1
write_bitstream $prj_name.bit

write_hw_platform -fixed -include_bit $prj_name.xsa
#write_hwdef design.hdf
hsi::open_hw_design $prj_name.xsa
hsi::set_repo_path $repoPath
hsi::create_sw_design sw1 -proc $processor -os device_tree
set_property CONFIG.dt_overlay true [hsi::get_os]
hsi::generate_bsp -dir ./device-tree

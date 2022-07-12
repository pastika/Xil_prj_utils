# parse args
set project [lindex $argv 0]
set prj_name [lindex $argv 1]
set repoPath [lindex $argv 2]
set processor [lindex $argv 3]
set maxThreads [lindex $argv 4]
set startPoint  [lindex $argv 5]
set endPoint  [lindex $argv 6]
set force [lindex $argv 7]

if { $startPoint <= 3 && $endPoint >= 3 } {
    hsi::open_hw_design $prj_name.xsa
    hsi::set_repo_path $repoPath
    hsi::create_sw_design sw1 -proc $processor -os device_tree
    common::set_property CONFIG.dt_overlay true [hsi::get_os]
    hsi::generate_bsp -dir ./device-tree
}

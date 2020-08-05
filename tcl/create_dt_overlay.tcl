# parse args
set xsa_file [lindex $argv 0]
set repoPath [lindex $argv 1]
set processor [lindex $argv 2]

set hw [hsi::open_hw_design $xsa_file]
hsi::set_repo_path $repoPath
hsi::create_sw_design sw1 -proc $processor -os device_tree
hsi::set_property CONFIG.dt_overlay true [hsi::get_os]
hsi::generate_bsp -dir ./devtree
hsi::close_hw_design $hw

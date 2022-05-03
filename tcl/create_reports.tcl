# parse args
set project [lindex $argv 0]
set prj_name [lindex $argv 1]
set maxThreads [lindex $argv 2]
set run [lindex $argv 3]

# See https://www.xilinx.com/support/documentation/sw_manuals/xilinx2019_2/ug835-vivado-tcl-commands.pdf#page=1619
set_msg_config -severity INFO -suppress
set_msg_config -severity STATUS -suppress

set_param general.maxThreads $maxThreads

open_project $project

puts $run

open_run $run

report_timing_summary -max_paths 10 -file timing_summary.txt
report_utilization -hierarchical -file utilization_summary.txt

report_timing_summary -no_detailed_paths -file timing_short_summary.txt
report_utilization -hierarchical -hierarchical_depth 3 -file utilization_short_summary.txt

## This gets access to the bd correctly but... 
#open_bd_design [get_files -regex .*.bd]
## https://www.xilinx.com/support/documentation/sw_manuals/xilinx2019_2/ug835-vivado-tcl-commands.pdf#page=1780
## ... these two fail with "WARNING: [BD 5-349] write_bd_layout failed. Please run the tool in GUI mode and try again." in `-mode tcl`
#start_gui
#write_bd_layout -format pdf -orientation landscape block_diagram.pdf
#write_bd_layout -format svg -orientation landscape block_diagram.svg
#stop_gui

reset_msg_config -severity INFO -suppress
reset_msg_config -severity STATUS -suppress

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

report_timing_summary -max_paths 10 -file timing_summary.rpt
report_utilization -file utilization_summary.rpt

reset_msg_config -severity INFO -suppress
reset_msg_config -severity STATUS -suppress

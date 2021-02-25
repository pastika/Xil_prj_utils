######################################################################
# project customizaion
######################################################################

# parse args
set project [lindex $argv 0]
set bd_file [lindex $argv 1]

open_project $project

# See https://www.xilinx.com/support/documentation/sw_manuals/xilinx2019_2/ug835-vivado-tcl-commands.pdf#page=1619
set_msg_config -severity INFO -suppress
set_msg_config -severity STATUS -suppress

# Create the top level wrapper for the project
make_wrapper -files [get_files $bd_file] -top -import

reset_msg_config -severity INFO -suppress
reset_msg_config -severity STATUS -suppress
######################################################################


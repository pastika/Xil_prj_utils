# parse args
set project [lindex $argv 0]
set xsa_file [lindex $argv 1]

open_project $project

#create xsa file
write_hw_platform -fixed -force  -include_bit -file $xsa_file

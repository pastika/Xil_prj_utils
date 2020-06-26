#
file copy -force golden.xpr $project
#
#
source ../../../../shared/src/tcl/prj_build_lib.tcl
# syntax : prj_build <project file (without path)> <filelist path> <top entity name>
prj_build $project $projectFolder/filelist.txt $top_entity

######################################################################
# project customizaion
######################################################################
# Set IP repository paths
set wd [pwd]

puts $wd

open_project $project

set ip_repo_list {}
lappend ip_repo_list "[file normalize "$wd/../../../../ip_repo"]"

puts ip_repo_list

set obj [get_filesets sources_1]
set_property "ip_repo_paths" $ip_repo_list $obj

# Rebuild user ip_repo's index before adding any source files
update_ip_catalog -rebuild

# Create the top level wrapper for the project - make this not hard coded!!!
make_wrapper -files [get_files tester.bd] -top -import

set_property -name "top_auto_set" -value "0" -objects $obj
######################################################################


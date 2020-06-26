# add source files to project file
set project tileboard-tester.xpr
set top_entity tester_wrapper

set projectFolder ../tileboardTester
#

source $projectFolder/create.tcl
###
### initial synthesis to generate ip and block diagram files
##open_project $project
###
##set_param general.maxThreads 6
##reset_run synth_1
##launch_runs synth_1 -jobs 6
##wait_on_run synth_1 
##reset_run synth_1
###
### # copy golden to working project file (cleanup polluted working project file)
##file copy -force golden.xpr $project
### # recreate the working project file from a clean basis
##source create.tcl


exit

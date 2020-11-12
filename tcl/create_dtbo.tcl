# Should be run within vivado
# set parameters
set prj_name [get_property NAME [current_project]]
set prj_dir [get_property DIRECTORY [current_project]]
set repo_path "$prj_dir/../shared/device-tree-xlnx/"
set xsa_file "$prj_dir/dtbuild/$prj_name.xsa"
set processor psu_cortexa53_0
# create directory if necessary
if {[expr {![file exists "$prj_dir/dtbuild"]} ]}  { 
   file mkdir "$prj_dir/dtbuild" }
cd "$prj_dir/dtbuild"
   
# create bitfile
open_run [current_run]
write_bitstream -force "$prj_dir/dtbuild/$prj_name.bit"

#create xsa file
#write_hw_platform -fixed -force  -include_bit -file $xsa_file

#create dtsi 
#set hw [hsi::open_hw_design $xsa_file]
#set hw [hsi::current_hw_design]
hsi::current_hw_design [hsi::current_hw_design]
hsi::set_repo_path $repo_path
hsi::create_sw_design sw1 -proc $processor -os device_tree
set_property CONFIG.dt_overlay true [hsi::get_os]
hsi::generate_bsp -dir ./devtree
hsi::close_sw_design sw1
#hsi::close_hw_design $hw

# process dtsi
# set sed_str "s/bit.bin/bit/g"
exec sed -i "/firmware-name/c\\    firmware-name = \"$prj_name.bit\";" ./devtree/pl.dtsi

# create dtbo
exec dtc -O dtb -o ./devtree/pl.dtbo -b 0 -@ ./devtree/pl.dtsi
exec mv ./devtree/pl.dtbo "$prj_name.dtbo"
exec mv ./devtree/pl.dtsi "$prj_name.dtsi"


#if @Transient@ == 0
#noexec
#endif

set N     @node@
set i     @node:index@
set Temp  @Temp@

#- Automatic alternating color assignment tied to node index
#----------------------------------------------------------------------#
set COLORS  [list green blue red orange magenta violet brown]
set NCOLORS [llength $COLORS]
set color   [lindex  $COLORS [expr $i%$NCOLORS]]

#----------------------------------------------------------------------#
load_file TransientIGBT_@plot@ -name PLT($N)

#----------------------------------------------------------------------#
echo "plotting collector current response"
if {[lsearch [list_plots] Plot_Ict] == -1} {
	create_plot -1d -name Plot_Ict
	set_plot_prop -title "Ic Vs t curve" -title_font_size 20 	
	set_axis_prop -axis x -title {Time [s]} \
		-title_font_size 16 -label_font_size 14 -type linear	
	set_axis_prop -axis y -title {Collector Current [A]} \
		-title_font_size 16 -label_font_size 14 -type linear
	set_axis_prop -axis y2 -title {Gate Voltage [V]} \
		-title_font_size 16 -label_font_size 14 -type linear	
	set_legend_prop -label_font_size 12 -location top_left -label_font_att bold	
}
select_plots Plot_Ict

create_curve -name Ic($N) -dataset PLT($N) \
	-axisX "time" -axisY "Collector TotalCurrent"
create_curve -name Vg($N) -dataset PLT($N) \
	-axisX "time" -axisY2 "Gate OuterVoltage"	
set_curve_prop Ic($N) -label "Ic Temp= $Temp" \
	-color $color -line_style solid -line_width 3 
set_curve_prop Vg($N) -label "Vg" \
	-color black -line_style solid -line_width 3

#----------------------------------------------------------------------#
echo "plotting collector voltage response"
if {[lsearch [list_plots] Plot_Vct] == -1} {
	create_plot -1d -name Plot_Vct
	set_plot_prop -title "Vc Vs t curve" -title_font_size 20 	
	set_axis_prop -axis x -title {Time [s]} \
		-title_font_size 16 -label_font_size 14 -type linear	
	set_axis_prop -axis y -title {Collector Voltage [V]} \
		-title_font_size 16 -label_font_size 14 -type linear
	set_axis_prop -axis y2 -title {Gate Voltage [V]} \
		-title_font_size 16 -label_font_size 14 -type linear	
	set_legend_prop -label_font_size 12 -location top_left -label_font_att bold	
}
select_plots Plot_Vct

create_curve -name Vc($N) -dataset PLT($N) \
	-axisX "time" -axisY "Collector InnerVoltage"
create_curve -name Vg($N) -dataset PLT($N) \
	-axisX "time" -axisY2 "Gate OuterVoltage"	
set_curve_prop Vc($N) -label "Vc Temp= $Temp" \
	-color $color -line_style solid -line_width 3 
set_curve_prop Vg($N) -label "Vg" \
	-color black -line_style solid -line_width 3

#----------------------------------------------------------------------#
echo "plotting power dissipation as a function of time"
if {[lsearch [list_plots] Plot_Pt] == -1} {
	create_plot -1d -name Plot_Pt
	set_plot_prop -title "P Vs t curve" -title_font_size 20 	
	set_axis_prop -axis x -title {Time [s]} \
		-title_font_size 16 -label_font_size 14 -type linear	
	set_axis_prop -axis y -title {Power Dissipation [W]} \
		-title_font_size 16 -label_font_size 14 -type linear
	set_axis_prop -axis y2 -title {Gate Voltage [V]} \
		-title_font_size 16 -label_font_size 14 -type linear	
	set_legend_prop -label_font_size 12 -location top_left -label_font_att bold	
}
select_plots Plot_Pt

create_curve -name Ic($N) -dataset PLT($N) \
	-axisX "time" -axisY "Collector TotalCurrent"
create_curve -name Vc($N) -dataset PLT($N) \
	-axisX "time" -axisY "Collector InnerVoltage"
create_curve -name Power($N) -function "<Ic($N)>*<Vc($N)>"	
create_curve -name Vg($N) -dataset PLT($N) \
	-axisX "time" -axisY2 "Gate OuterVoltage"	
set_curve_prop Power($N) -label "Power Temp= $Temp" \
	-color $color -line_style solid -line_width 3 
	
set_curve_prop Vg($N) -label "Vg" \
	-color black -line_style solid -line_width 3

remove_curves "Ic($N) Vc($N)"
windows_style -style grid

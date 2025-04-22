#if @IcVc@ == 0
#noexec
#endif

#----------------------------------------------------------------------#
load_library extract
lib::SetInfoDef 1
#----------------------------------------------------------------------#
set N     @node@
set i 	  @node:index@
set Temp  @Temp@

#- Automatic alternating color assignment tied to node index
#----------------------------------------------------------------------#
set COLORS  [list green blue red orange magenta violet brown]
set NCOLORS [llength $COLORS]

set STYLES  [list dash dot solid]
set NSTYLES [llength $STYLES]
set style [lindex $STYLES [expr $i%$NSTYLES]]

#----------------------------------------------------------------------#
# Plotting Ic vs Vc curves
if {[lsearch [list_plots] Plot_IcVc] == -1} {
	create_plot -1d -name Plot_IcVc
	set_plot_prop -title "I<sub>c</sub>-V<sub>cs</sub> Characteristics" -title_font_size 20	
	set_axis_prop -axis x -title {Collector Voltage [V]} \
		-title_font_size 16 -label_font_size 14 -type linear
	set_axis_prop -axis y -title {Collector Current [A/<greek>m</greek>m]} \
		-title_font_size 16 -label_font_size 14 -type linear
	set_legend_prop -label_font_size 12 -location top_left -label_font_att bold		
}
select_plots Plot_IcVc

set IcVcs [lsort [glob IcVc_?_@plot@]]

set i 0
foreach IcVc $IcVcs {
	load_file $IcVc -name PLT($N,$i)
	set color   [lindex  $COLORS [expr $i%$NCOLORS]]
	set Vgs [get_variable_data "Gate OuterVoltage" -dataset PLT($N,$i)]	
	set Vg [lindex $Vgs 0]
	set NAME IGBT_${Vg}_$N
	
	set Vcs [get_variable_data "Collector OuterVoltage" -dataset PLT($N,$i)]
	set Ics [get_variable_data "Collector TotalCurrent" -dataset PLT($N,$i)]
	ext::AbsList -out absIcs -x $Ics ;# Compute absolute value of drain currents
	create_variable -name absIc -dataset PLT($N,$i) -values $absIcs
	create_curve -name $NAME -dataset PLT($N,$i) \
		-axisX "Collector OuterVoltage" -axisY "absIc"
	set_curve_prop $NAME -label "IcVc Vg=[lindex $Vgs $i] (Temp= $Temp)" \
		-color $color -line_style $style -line_width 3
	incr i
}

#if @IcVg@ == 0
#noexec
#endif
#----------------------------------------------------------------------#
#set Ic   x
#----------------------------------------------------------------------#
load_library extract
lib::SetInfoDef 1
#----------------------------------------------------------------------#

set N     @node@
set i     @node:index@
set Temp  @Temp@

#- Automatic alternating color assignment tied to node index
#----------------------------------------------------------------------#
set COLORS  [list green blue red orange magenta violet brown]
set NCOLORS [llength $COLORS]
set color   [lindex  $COLORS [expr $i%$NCOLORS]]

#- IcVg plotting
#----------------------------------------------------------------------#
load_file IcVg_@plot@ -name PLT($N)

if {[lsearch [list_plots] Plot_IcVg] == -1} {
	create_plot -1d -name Plot_IcVg
	set_plot_prop -title "I<sub>c</sub>-V<sub>gs</sub> Characteristics" -title_font_size 20 
	set_axis_prop -axis x -title {Gate Voltage [V]} \
		-title_font_size 16 -label_font_size 14 -type linear
	set_axis_prop -axis y -title {Collector Current [A/<greek>m</greek>m]} \
		-title_font_size 16 -label_font_size 14 -type log	
	set_legend_prop -label_font_size 12 -location top_left -label_font_att bold	
}
select_plots Plot_IcVg

create_curve -name IcVg($N) -dataset PLT($N) \
	-axisX "Gate OuterVoltage" -axisY "Collector TotalCurrent"
set_curve_prop IcVg($N) -label "IcVg Temp= $Temp" \
	-color $color -line_style solid -line_width 3

#- Extraction
#----------------------------------------------------------------------#
set Vgs [get_variable_data "Gate OuterVoltage" -dataset PLT($N)]
set Ics [get_variable_data "Collector TotalCurrent" -dataset PLT($N)]

ext::ExtractExtremum -out Icmax -name Ic -x $Vgs -y $Ics -type max
echo "Max Ic is [format %.3e $Icmax] A/um"

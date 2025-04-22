#if @Transient@ == 0
#noexec
#endif
 
Dessis IGBT {
*----------------------------------------------------------------------*
File {
   Grid= "@tdr@" 
   Parameters= "@parameter@"
   Plot= "@tdrdat@"
   Current= "@plot@" 
}	

Electrode {
   { Name="Gate"      Voltage= 0 Resist= 1e-3 }
   { Name="Emitter"   Voltage= 0 Resist= 1e-3 }
   { Name="Collector" Voltage= 0 Resist= 1e-3 }
}

Thermode {
   { Name="Gate"      Temperature= @Temp@ }
   { Name="Emitter"   Temperature= @Temp@ }
   { Name="Collector" Temperature= @Temp@ }
}

Physics {
   AreaFactor= 1e5	
   Temperature= @Temp@
   EffectiveIntrinsicDensity(BandGapNarrowing (Slotboom))
   Thermodynamic
   AnalyticTEP
}

Physics(Material="Silicon"){
   Mobility ( 
      Enormal(IALMob)
      HighFieldSaturation      
   )
   Recombination (
      SRH(DopingDependence TempDependence)
      Auger
      Avalanche (Lackner)
   )      
}

*----------------------------------------------------------------------*
}

File {
   Output= "@log@"	
}

Insert= "PlotSection_des.cmd"
#include "MathSection_des.cmd"

System {
   IGBT IGBT (Emitter=0 Gate=2 Collector=3)
   Vsource_pset vc  (4 0) { dc= 0 }
   Vsource_pset vg  (2 0) { pwl= (0 0 2e-7 0 2.01e-7 15 1e-6 15 1.2e-6 -15 1 -15)}
   Resistor_pset rc (4 3) { resistance= 100 }
   Plot "n@node@_1" (time() v(2) v(3) v(4) i(rc 3))
}

Solve {
   Poisson
   Coupled { Poisson Electron Hole }

   Quasistationary (
      InitialStep= 1e-5 Increment= 2.0 Decrement= 1.5
      MinStep= 1e-11 MaxStep= 0.05
      Goal { Parameter= vc.dc Value=@VcT@ }
   ){ Coupled { Poisson Electron Hole Temperature } }
	
   NewCurrentPrefix="Transient"
   Transient (
      InitialTime= 0 FinalTime= 3e-6 
      InitialStep= 1e-8 Increment= 2.0 Decrement= 1.5
      MinStep= 1e-14 MaxStep= 1e-7
   ){ Coupled { Poisson Electron Hole Temperature }
   }

}


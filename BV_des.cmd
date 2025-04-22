File {
	Grid="@tdr@"
	Parameter="@parameter@"
	Output="@log"
	Current="@plot@"
	Plot="@tdrdat@"
}

Electrode{
	{Name="Gate"  Voltage=0.0}
	{Name="Emitter"  Voltage=0.0}
	{Name="Collector"  Voltage=0.0 Resistor=1e12}
}

Physics {
   AreaFactor =@<1e8/Xmax>@
   Temperature= 300
   EffectiveIntrinsicDensity (oldSlotboom)
}


Physics(Material="Silicon"){
  Mobility(
   DopingDep
   HighFieldSaturation
   Enormal
  )
    Recombination (
    SRH ( DopingDependence )
    Auger
    Avalanche (Lackner)
  )
	
}



Math{ 
	Transient = BE
     Method= Super 
     Extrapolate
	Notdamped=50
	Iterations=25
	ExitOnFailure
    Number_of_threads = 8
    BreakCriteria{ Current (Contact = "Collector" Absval = 1e-4)}
}


Plot{
  *- Carrier Densities:
  eDensity hDensity
  # EffectiveIntrinsicDensity IntrinsicDensity
  # eEquilibriumDensity hEquilibriumDensity
  *- Currents and current components:
  Current/Vector eCurrent/Vector hCurrent/Vector
  # ConductionCurrent/Vector DisplacementCurrent/Vector
  eMobility hMobility
  eVelocity hVelocity
  *- Fields, Potentials and Charge distributions
  ElectricField/Vector
  Potential
  eQuasiFermi hQuasiFermi
  SpaceCharge
  *- Driving forces
  eGradQuasiFermi/Vector hGradQuasiFermi/Vector
  eEparallel hEparallel 
  eENormal hENormal
  # eEffectiveField hEffectiveField
  *- Temperatures
  LatticeTemperature
  eTemperature hTemperature
  *- Generation/Recombination
  SRHRecombination Band2BandGeneration AugerRecombination RadiativeRecombination
  AvalancheGeneration eAvalancheGeneration hAvalancheGeneration
  TotalRecombination
  eLifeTime hLifeTime
  SurfaceRecombination
  # CDL CDL1 CDL2 CDL3
  # eCDL1lifetime eCDL2lifetime hCDL1lifetime hCDL2lifetime
  # SurfaceMultRecombination
  *- Doping Profiles
  Doping 
  DonorConcentration AcceptorConcentration
  # AntimonyConcentration ArsenicConcentration BoronConcentration 
  # IndiumConcentration NitrogenConcentration PhosphorusConcentration
  # NDopantConcentration PDopantConcentration
  *- Incomplete ionization
  # AsPlus PhPlus SbPlus NitrogenPlus
  # BMinus InMinus 
  # NDopantPlus PDopantMinus 

  *- Band structure
  BandGap 
  BandGapNarrowing
  ElectronAffinity
  ConductionBandEnergy ValenceBand
  eQuantumPotential hQuantumPotential
  *- Composition
  # xMoleFraction yMoleFraction
  *- Traps
  # eTrappedCharge hTrappedCharge
  # eGapStatesRecombination hGapStatesRecombination
  *- Optical Generation
  # ComplexRefractiveIndex AbsorbedPhotonDensity OpticalGeneration
  # OpticalAbsorptionHeat QuantumYield
  *- Generation due to Ion Strikes
  # AlphaCharge HeavyIonChargeDensity
  *- Gate Tunneling/Hot carrier injection
  # FowlerNordheim 
  # HotElectronInjection HotHoleInjection
  *- Tunneling
  # BarrierTunneling eBarrierTunneling hBarrierTunneling
  # eDirectTunnelCurrent hDirectTunnelCurrent
  *- Ionization Integrals
  # MeanIonIntegral eIonIntegral hIonIntegral 
  *- Heat flow
  # TotalHeat eJouleHeat hJouleHeat
  # PeltierHeat ThomsonHeat RecombinationHeat
  # ThermalConductivity 
  *- Stress-Tensor
  # Stressxx Stressxy Stressxz Stressyy Stressyz Stresszz
  *- Ferro-electrical Polarization
  # Polarization/Vector
  *- Piezo
  # PiezoCharge ConversePiezoelectricField
  # ConversePiezoelectricFieldXX ConversePiezoelectricFieldXY ConversePiezoelectricFieldXZ
  # ConversePiezoelectricFieldYY ConversePiezoelectricFieldYZ ConversePiezoelectricFieldZZ


}

Solve{
  Poisson
  Coupled{ Poisson Electron}
  Coupled{ Poisson Electron Hole} 
  
     NewCurrentFile="BV_" 
  Quasistationary ( 
    InitialStep= 1e-8 Increment= 1.41 Decrement=2.0
    MinStep= 1e-20     MaxStep= 0.005
     Goal { Name="Collector" Voltage= 2400}
  ){
    Coupled { Poisson Electron Hole }
    #Plot(FilePrefix="Profile_n@node@" Time=(Range=(0.0 1.0) Intervals=80) noOverwrite)
  }
  
     
  }
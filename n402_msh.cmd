Title "Untitled"

Controls {
}

IOControls {
	EnableSections
}

Definitions {
	Constant "Constant.Substrate" {
		Species = "PhosphorusActiveConcentration"
		Value = 5e+13
	}
	Constant "Constant.PolySilicon" {
		Species = "PhosphorusActiveConcentration"
		Value = 1e+21
	}
	AnalyticalProfile "Gauss.Pbase" {
		Species = "BoronActiveConcentration"
		Function = Gauss(PeakPos = 0, PeakVal = 2.5e+17, ValueAtDepth = 5e+13, Depth = 3)
		LateralFunction = Gauss(Factor = 0.7)
	}
	AnalyticalProfile "GAUSS.Pplus_0" {
		Species = "BoronActiveConcentration"
		Function = Gauss(PeakPos = 0, PeakVal = 1e+19, ValueAtDepth = 2.5e+17, Depth = 0.5)
		LateralFunction = Gauss(Factor = 0.7)
	}
	AnalyticalProfile "GAUSS.Nplus_0" {
		Species = "PhosphorusActiveConcentration"
		Function = Gauss(PeakPos = 0, PeakVal = 1e+19, ValueAtDepth = 2.5e+17, Depth = 0.5)
		LateralFunction = Gauss(Factor = 0.7)
	}
	AnalyticalProfile "Gauss.Nbuffer" {
		Species = "ArsenicActiveConcentration"
		Function = Gauss(PeakPos = 0, PeakVal = 5e+15, ValueAtDepth = 5e+13, Depth = 4)
		LateralFunction = Gauss(Factor = 0.7)
	}
	AnalyticalProfile "Gauss.Pcollector" {
		Species = "BoronActiveConcentration"
		Function = Gauss(PeakPos = 0, PeakVal = 1e+17, ValueAtDepth = 5e+15, Depth = 0.5)
		LateralFunction = Gauss(Factor = 0.7)
	}
	Refinement "RS.Global" {
		MaxElementSize = ( 1 1 )
		MinElementSize = ( 0.01 0.01 )
	}
	Refinement "RS.Silicon" {
		MaxElementSize = ( 0.8 0.8 )
		MinElementSize = ( 0.01 0.01 )
		RefineFunction = MaxTransDiff(Variable = "DopingConcentration",Value = 1)
	}
}

Placements {
	Constant "PLConstant.Substrate" {
		Reference = "Constant.Substrate"
		EvaluateWindow {
			Element = material ["Silicon"]
		}
	}
	Constant "PLConstant.PolySilicon" {
		Reference = "Constant.PolySilicon"
		Replace
		EvaluateWindow {
			Element = material ["PolySilicon"]
		}
	}
	AnalyticalProfile "PLGauss.Pbase" {
		Reference = "Gauss.Pbase"
		ReferenceElement {
			Element = Line [(0 0) (6 0)]
		}
	}
	AnalyticalProfile "PLGauss.LeftPplus_0" {
		Reference = "GAUSS.Pplus_0"
		ReferenceElement {
			Element = Line [(0 0) (1.5 0)]
		}
	}
	AnalyticalProfile "PLGauss.RightPplus_0" {
		Reference = "GAUSS.Pplus_0"
		ReferenceElement {
			Element = Line [(4.5 0) (6 0)]
		}
	}
	AnalyticalProfile "PLGauss.LeftNplus_0" {
		Reference = "GAUSS.Nplus_0"
		ReferenceElement {
			Element = Line [(1.5 0) (2 0)]
		}
	}
	AnalyticalProfile "PLGauss.RightNplus_0" {
		Reference = "GAUSS.Nplus_0"
		ReferenceElement {
			Element = Line [(4 0) (4.5 0)]
		}
	}
	AnalyticalProfile "PLGauss.Nbuffer" {
		Reference = "Gauss.Nbuffer"
		ReferenceElement {
			Element = Line [(0 99.5) (6 99.5)]
		}
	}
	AnalyticalProfile "PLGauss.Pcollector" {
		Reference = "Gauss.Pcollector"
		ReferenceElement {
			Element = Line [(0 100) (6 100)]
		}
	}
	Refinement "RP.Global" {
		Reference = "RS.Global"
		RefineWindow = Rectangle [(0 0) (1000 500)]
	}
	Refinement "RP.Silicon" {
		Reference = "RS.Silicon"
		RefineWindow = material ["Silicon"]
	}
}

Offsetting {

	noffset material "Silicon" {
		maxlevel=10
	}

	noffset region "R.Si" "region2.0" {
		hlocal=0.001
		factor=1.2
	}

	noffset region "region2.0" "region1.0" {
		hlocal=0.01
		factor=1.2
	}

	noffset region "region2.0" "R.Si" {
		hlocal=0.003
		factor=1.2
	}

}


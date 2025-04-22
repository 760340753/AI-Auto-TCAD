;; UCS
;----------------------------------------------------------------------
; Structure definition
;----------------------------------------------------------------------;
(sdegeo:set-default-boolean "BAB")

(sdegeo:create-polygon (list
  (position 0.0 2.0 0)
  (position 3.13 2.1 0)
  (position 3.13 2.7 0)
  (position 0.0 2.8 0)
  (position 0.0 2.0 0))
  "PolySi" "R.PolyGate")

(sdegeo:fillet-2d (find-vertex-id (position 3.13 2.1 0)) 0.2)
(sdegeo:fillet-2d (find-vertex-id (position 3.13 2.7 0)) 0.2)

(sdegeo:create-polygon (list
  (position 0.00 1.98 0)
  (position 3.22 2.08 0)
  (position 3.22 2.72 0)
  (position 0.00 2.82 0)
  (position 0.00 1.98 0))
  "Oxide" "R.Gox")
(sdegeo:fillet-2d (find-vertex-id (position 3.22 2.08 0)) 0.2)
(sdegeo:fillet-2d (find-vertex-id (position 3.22 2.72 0)) 0.2)

(sdegeo:create-polygon (list
  (position 0.02 2.00  0)
  (position 0.02 1.50  0)
  (position 0.22 1.30  0)
  (position 0.22 0.00  0)
  (position -0.18 0.00 0)
  (position -0.18 1.30 0)
  (position 0.00 1.50  0)
  (position 0.00 2.00  0)
  (position 0.02 2.00  0))
  "Oxide" "R.LOCOS")

(sdegeo:fillet-2d (find-vertex-id (position 0.22  1.3 0)) 0.15)
(sdegeo:fillet-2d (find-vertex-id (position -0.18 1.3 0)) 0.15)
(define xmin 0.0)
(define ymin 0.0)
(define xmax 4.8)
(define ymax 70.0)
(sdegeo:create-rectangle
  (position -0.3 2.8 0.0 )  (position 0.0 3.1 0.0 ) "Oxide"  "R.Spacer" )
(sdegeo:create-rectangle
  (position 0.0 0.0  0.0 )  (position -0.3 2.8 0.0 ) "PolySi"  "R.PolyCont" )
(sdegeo:create-rectangle
  (position 0.0  0.0 0.0 )  (position ymax xmax 0.0 ) "Silicon" "R.Si" )

(sdegeo:define-contact-set "Emitter"   4  (color:rgb 1 0 0 ) "##" )
(sdegeo:define-contact-set "Collector" 4  (color:rgb 1 0 0 ) "##" )
(sdegeo:define-contact-set "Gate"      4  (color:rgb 1 0 0 ) "##" )

(sdegeo:define-2d-contact (find-edge-id (position 0.0 3.5  0.0)) "Emitter")
(sdegeo:define-2d-contact (find-edge-id (position ymax 3.5 0.0)) "Collector")
(sdegeo:define-2d-contact (find-edge-id (position -0.3 1.0 0.0)) "Gate")

;----------------------------------------------------------------------
; Profiles
;----------------------------------------------------------------------;
; - Substrate
(sdedr:define-constant-profile "Const.Substrate"
 "PhosphorusActiveConcentration" 1e+15 )
(sdedr:define-constant-profile-material "PlaceCD.Substrate"
 "Const.Substrate" "Silicon" )

(sdedr:define-constant-profile "Const.PolyGate"
 "PhosphorusActiveConcentration" 1e+21 )
(sdedr:define-constant-profile-material "PlaceCD.PolyGate"
 "Const.PolyGate" "PolySi" )

(sdedr:define-refeval-window "BaseLine.pbody" "Line"
 (position 0.0 3.0 0.0)
 (position 0.0 5.0 0.0) )
(sdedr:define-gaussian-profile "Impl.pbodyprof"
 "BoronActiveConcentration"
 "PeakPos" 0.1  "PeakVal" 1e20
 "ValueAtDepth" 1e17  "Depth" 2
 "Erf"  "Length" 0.1)
(sdedr:define-analytical-profile-placement "Impl.pbody"
 "Impl.pbodyprof" "BaseLine.pbody" "Negative" "NoReplace" "Eval")

(sdedr:define-refeval-window "BaseLine.nplus" "Line"
 (position 0.0 3.0 0.0)
 (position 0.0 3.7 0.0) )
(sdedr:define-gaussian-profile "Impl.nplusprof"
 "ArsenicActiveConcentration"
 "PeakPos" 0.0  "PeakVal" 1e21
 "ValueAtDepth" 1e17  "Depth" 0.5
 "Erf"  "Length" 0.1)
(sdedr:define-analytical-profile-placement "Impl.nplus"
 "Impl.nplusprof" "BaseLine.nplus" "Negative" "NoReplace" "Eval")

(sdedr:define-refeval-window "BaseLine.fieldstop" "Line"
 (position 70.0 0.0 0.0)
 (position 70.0 5.0 0.0) )
(sdedr:define-gaussian-profile "Impl.fieldstopprof"
 "ArsenicActiveConcentration"
 "PeakPos" 0.0  "PeakVal" 1e19
 "ValueAtDepth" 1e15  "Depth" 3.0
 "Erf"  "Length" 0.1)
(sdedr:define-analytical-profile-placement "Impl.fieldstop"
 "Impl.fieldstopprof" "BaseLine.fieldstop" "Positive" "NoReplace" "Eval")

(sdedr:define-refeval-window "BaseLine.collector" "Line"
 (position 70.0 0.0 0.0)
 (position 70.0 5.0 0.0) )
(sdedr:define-gaussian-profile "Impl.collectorprof"
 "BoronActiveConcentration"
 "PeakPos" 0.1  "PeakVal" 1e20
 "ValueAtDepth" 1e17  "Depth" 0.5
 "Erf"  "Length" 0.1)
(sdedr:define-analytical-profile-placement "Impl.collector"
 "Impl.collectorprof" "BaseLine.collector" "Positive" "NoReplace" "Eval")

;----------------------------------------------------------------------
; Meshing
;----------------------------------------------------------------------;
(define ds 1)
(sdedr:define-refinement-size "global" (/ 10.0 ds) (/ 2.5 ds) (/ 2.5 ds) 0.1 0.1 0.1 )
(sdedr:define-refeval-window "global" "Rectangle"  (position -1e5 -1e5 0)  (position 1e5 1e5 0.0) )
(sdedr:define-refinement-placement "global" "global" (list "window" "global" ) )


(sdedr:define-refinement-size "active_domain" 5.0 2.0 0.5 0.02 0.02 0.05 )
(sdedr:define-refinement-material "active_domain" "active_domain" "Silicon")
(sdedr:define-refinement-function "active_domain" "DopingConcentration" "MaxTransDiff" 1)
(sdedr:define-refinement-function "active_domain" "MaxLenInt" "R.Si" "emitter" 0.002 2 "UseRegionNames")
(sdedr:define-refinement-function "active_domain" "MaxLenInt" "R.Si" "thermo_left" 0.025 2 "UseRegionNames")

(sdedr:define-refinement-function "active_domain" "MaxLenInt" "R.Si" "thermo_right" 0.025 2 "UseRegionNames")

(sdedr:define-refeval-window "active" "Rectangle"  (position ymin xmin 0.0)  (position ymax xmax 0.0) )
(sdedr:define-refinement-size "active" 5.0 1.0 1.0 0.02 0.03 0.5)
(sdedr:define-refinement-placement "active" "active" "active")
(sdedr:define-refinement-function "active" "DopingConcentration" "MaxTransDiff" 1)

;; Trench Bottom
(sdedr:define-refeval-window "RW.TrBot"
 "Rectangle"
 (position 1.8 1.0 0.0 )
 (position 4.0 3.0 0.0 ))
(sdedr:define-refinement-size "Ref.TrBot"
  0.5  0.1
  0.05 0.05)
(sdedr:define-refinement-function "Ref.TrBot"
 "DopingConcentration" "MaxTransDiff" 1)
(sdedr:define-refinement-placement "RefPlace.TrBot"
 "Ref.TrBot" "RW.TrBot" )


;----------------------------------------------------------------------
; Meshing Offseting
;----------------------------------------------------------------------;

(define nlevels 10)
(define factor 1.5)


(sdedr:offset-block "material" "Silicon"  "maxlevel" nlevels)
(sdedr:offset-interface "region" "R.Si" "R.Gox" "hlocal" 0.0015 "factor" factor)
(sdedr:offset-interface "region" "R.Gox" "R.PolyGate" "hlocal" 0.01 "factor" factor)
(sdedr:offset-interface "region" "R.Gox" "R.Si" "hlocal" 0.003 "factor" factor)


;----------------------------------------------------------------------
; Saving BND file
(sdeio:save-tdr-bnd (get-body-list) "@tdrboundary/o@")

; Save CMD file
(sdedr:write-cmd-file "@commands/o@")
(system:command "snmesh -offset n@node@_msh")


;; Defined Parameters:

;; Contact Sets:
(sdegeo:define-contact-set "Emitter" 4 (color:rgb 1 0 0 )"##" )
(sdegeo:define-contact-set "Gate" 4 (color:rgb 0 1 0 )"##" )
(sdegeo:define-contact-set "Collector" 4 (color:rgb 0 0 1 )"##" )

;; Work Planes:
(sde:workplanes-init-scm-binding)

;; Defined ACIS Refinements:
(sde:refinement-init-scm-binding)

;; Reference/Evaluation Windows:
(sdedr:define-refeval-window "RW.BaselinePbase" "Line" (position 0 0 0) (position 6 0 0))
(sdedr:define-refeval-window "RW.BaseLineLeftPplus_0" "Line" (position 0 0 0) (position 1.5 0 0))
(sdedr:define-refeval-window "RW.BaseLineRightPplus_0" "Line" (position 4.5 0 0) (position 6 0 0))
(sdedr:define-refeval-window "RW.BaseLineLeftNplus_0" "Line" (position 1.5 0 0) (position 2 0 0))
(sdedr:define-refeval-window "RW.BaseLineRightNplus_0" "Line" (position 4 0 0) (position 4.5 0 0))
(sdedr:define-refeval-window "RW.BaselineNbuffer" "Line" (position 0 99.5 0) (position 6 99.5 0))
(sdedr:define-refeval-window "RW.BaselinePcollector" "Line" (position 0 100 0) (position 6 100 0))
(sdedr:define-refeval-window "RW.Global" "Rectangle" (position 0 0 0) (position 1000 500 0))

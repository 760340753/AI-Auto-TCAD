Math {
   Extrapolate
   Transient= BE
   Notdamped= 50
   Iterations= 15
   ExitOnFailure
   
   Digits= 5
   * Temperature dependent ni value
   ErrRef(electron)= @<ni*1.0>@
   ErrRef(hole)= @<ni*1.0>@
}

!macro customInstall
  ; Create startup registry entry
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Run" "BuiltByRaysCFOOS" "$INSTDIR\${APP_EXECUTABLE}"
  
  ; Create uninstall registry entry
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\BuiltByRaysCFOOS" "DisplayName" "BuiltByRays™ CFO OS"
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\BuiltByRaysCFOOS" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\BuiltByRaysCFOOS" "DisplayIcon" "$INSTDIR\${APP_EXECUTABLE}"
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\BuiltByRaysCFOOS" "Publisher" "BuiltByRays™"
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\BuiltByRaysCFOOS" "DisplayVersion" "${VERSION}"
  WriteRegDWORD HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\BuiltByRaysCFOOS" "NoModify" 1
  WriteRegDWORD HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\BuiltByRaysCFOOS" "NoRepair" 1
  
  ; Set application to run as administrator
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" "$INSTDIR\${APP_EXECUTABLE}" "RUNASADMIN"
!macroend

!macro customUnInstall
  ; Remove startup registry entry
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Run" "BuiltByRaysCFOOS"
  
  ; Remove uninstall registry entry
  DeleteRegKey HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\BuiltByRaysCFOOS"
  
  ; Remove compatibility settings
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" "$INSTDIR\${APP_EXECUTABLE}"
!macroend 
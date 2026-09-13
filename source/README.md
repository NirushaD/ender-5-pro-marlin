# Complete Marlin source snapshot

The complete configured source is stored as a split ZIP archive in this directory because the GitHub connector cannot upload a single 9.5 MB blob. Download every `source.zip.part01` through `source.zip.part14` and concatenate them in numeric order to reconstruct `source.zip` (the archive is the exact source snapshot used for r3).

Windows PowerShell:

``
powershell
Get-ChildItem source.zip.part* | Sort-Object Name | ForEach-Object { [IO.File]::ReadAllBytes($_.FullName) } | Set-Content -Encoding Byte source.zip
```

Then extract `source.zip` and build with PlatformIO using `STM32F103RE_creality`.

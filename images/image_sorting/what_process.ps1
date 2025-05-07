Get-Process | ForEach-Object {
    $procId = $_.Id
    $procName = $_.Name
    try {
        $handles = Get-CimInstance -ClassName Win32_ProcessHandle -Filter "ProcessId = $procId" -ErrorAction SilentlyContinue
        foreach ($handle in $handles) {
            $file = Get-CimInstance -ClassName CIM_DataFile -Filter "Handle = '$($handle.Handle)'" -ErrorAction SilentlyContinue
            if ($file.Name -like "*webp_20180716_151253.webp*") {
                Write-Output "Process: $procName, PID: $procId, File: $($file.Name)"
            }
        }
    } catch {}
}
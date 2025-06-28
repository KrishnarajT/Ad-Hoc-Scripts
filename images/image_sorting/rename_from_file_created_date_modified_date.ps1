<#
.SYNOPSIS
    Renames files in a specified folder based on their creation or modified timestamp, with optional recursion and extension filtering.

.DESCRIPTION
    This script renames files in the specified folder (and optionally its subdirectories) using the selected timestamp (creation or modified time) in milliseconds since the Unix epoch.
    It supports a customizable list of file extensions and includes a recursion option to process subdirectories. Detailed logging can be enabled with the -LogToConsole switch.

.PARAMETER FolderPath
    The full path to the folder containing files to rename. Required.

.PARAMETER TimeType
    Specifies which timestamp to use for renaming: 1 for CreationTime, 2 for LastWriteTime. Required.

.PARAMETER Extensions
    Comma-separated list of file extensions to process (e.g., .jpg,.png). If omitted, defaults to a predefined list of image and media extensions.

.PARAMETER Recurse
    Switch to recursively process all subdirectories. If omitted, only the specified folder is processed.

.PARAMETER LogToConsole
    Switch to enable detailed logging to the terminal. If omitted, only rename operations and errors are displayed.

.EXAMPLE
    Rename files in a folder using modified time, non-recursive, with logging:
    .\RenameFilesByTimestamp.ps1 -FolderPath "C:\Photos" -TimeType 2 -LogToConsole

.EXAMPLE
    Rename files recursively with specific extensions and logging:
    .\RenameFilesByTimestamp.ps1 -FolderPath "\\KRISH-HOME-NAS\Photos" -TimeType 2 -Extensions ".jpg,.png" -Recurse -LogToConsole
#>

param (
    [Parameter(Mandatory=$true, HelpMessage="Enter the folder path containing files")]
    [string]$FolderPath,

    [Parameter(Mandatory=$true, HelpMessage="Use creation time (1) or modified time (2)")]
    [ValidateSet("1", "2")]
    [string]$TimeType,

    [Parameter(Mandatory=$false, HelpMessage="Comma-separated list of file extensions (e.g., .png,.jpg)")]
    [string]$Extensions,

    [Parameter(Mandatory=$false, HelpMessage="Recursively process all subdirectories")]
    [switch]$Recurse,

    [Parameter(Mandatory=$false, HelpMessage="Enable detailed logging to the terminal")]
    [switch]$LogToConsole
)

# Function to write to console based on LogToConsole switch
function Write-Log {
    param (
        [string]$Message,
        [string]$Level = "INFO"
    )
    if ($LogToConsole) {
        switch ($Level) {
            "INFO" { Write-Output $Message }
            "WARNING" { Write-Warning $Message }
            "ERROR" { Write-Error $Message }
        }
    }
}

# Validate folder path
if (-not (Test-Path -Path $FolderPath -PathType Container)) {
    Write-Error "The provided path '$FolderPath' is not a valid directory."
    exit 1
}

# Log PowerShell version for debugging
Write-Log -Message "PowerShell Version: $($PSVersionTable.PSVersion)" -Level "INFO"

# Log the scanning mode
Write-Log -Message "Scanning $(if ($Recurse) { 'recursively' } else { 'non-recursively' }) in $FolderPath for files" -Level "INFO"

# Default extensions if none provided
$defaultExtensions = @(".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".mp4", ".avi", ".mov", ".mkv", ".3gp", ".amr", ".3gpp", ".aac", ".m4a", ".mp3")
$fileExtensions = if ($Extensions) { $Extensions -split "," | ForEach-Object { $_.Trim().ToLower() } } else { $defaultExtensions }
# Convert extensions to wildcard patterns for Get-ChildItem
$extensionPatterns = $fileExtensions | ForEach-Object { "*$_" }

# Get all files in the folder with matching extensions
Write-Log -Message "Starting file enumeration with extensions: $($fileExtensions -join ', ')" -Level "INFO"
$files = if ($Recurse) {
    Get-ChildItem -Path $FolderPath -File -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Extension.ToLower() -in $fileExtensions }
} else {
    Get-ChildItem -Path $FolderPath -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension.ToLower() -in $fileExtensions }
}

# Log directories scanned when recursing
if ($Recurse) {
    $directories = Get-ChildItem -Path $FolderPath -Directory -Recurse -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
    if ($directories) {
        Write-Log -Message "Subdirectories scanned: $($directories -join ', ')" -Level "INFO"
    } else {
        Write-Log -Message "No subdirectories found in $FolderPath" -Level "INFO"
    }
}

# Check if any files were found
if ($null -eq $files -or $files.Count -eq 0) {
    Write-Warning "No files with extensions [$($fileExtensions -join ', ')] found in $FolderPath$(if ($Recurse) { ' or its subfolders' })."
    if (-not $Recurse) {
        $rootFiles = Get-ChildItem -Path $FolderPath -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name
        if ($rootFiles) {
            Write-Log -Message "Files found in root folder ($FolderPath): $($rootFiles -join ', ')" -Level "INFO"
        } else {
            Write-Log -Message "No files found in root folder ($FolderPath)." -Level "INFO"
        }
    }
    exit 0
}

# Initialize counters
$totalFiles = $files.Count
$currentFile = 0

# Iterate through files
foreach ($file in $files) {
    $currentFile++
    $percentComplete = ($currentFile / $totalFiles) * 100
    Write-Progress -Activity "Renaming Files" -Status "Processing $($file.Name)" -PercentComplete $percentComplete

    Write-Log -Message "Processing file: $($file.FullName)" -Level "INFO"

    # Get the selected timestamp
    $timestamp = if ($TimeType -eq "1") { $file.CreationTime } else { $file.LastWriteTime }
    $timestampMs = [int64](($timestamp - (Get-Date "1970-01-01")).TotalMilliseconds)

    # Get file extension
    $ext = $file.Extension.ToLower()

    # Create new filename with timestamp
    $newFilename = "$timestampMs$ext"
    $newFilePath = Join-Path -Path (Split-Path -Path $file.FullName -Parent) -ChildPath $newFilename

    # Check if the new file name is the same as the old one
    if ($newFilePath -eq $file.FullName) {
        Write-Host "File $($file.Name) already has the correct name."
        continue
    }

    # Handle duplicate timestamps
    $counter = 1
    while (Test-Path -Path $newFilePath) {
        $newTimestampMs = $timestampMs + $counter
        $newFilename = "$newTimestampMs$ext"
        $newFilePath = Join-Path -Path (Split-Path -Path $file.FullName -Parent) -ChildPath $newFilename
        $counter++
    }

    # Rename the file
    try {
        Rename-Item -Path $file.FullName -NewName $newFilename -ErrorAction Stop
        Write-Host "Renamed: $($file.Name) -> $newFilename"
    }
    catch {
        Write-Error "Error renaming $($file.Name): $_"
    }
}

Write-Progress -Activity "Renaming Files" -Completed
Write-Host "File renaming completed."
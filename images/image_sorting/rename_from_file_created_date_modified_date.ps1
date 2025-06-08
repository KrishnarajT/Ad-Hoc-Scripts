# RenameFilesByTimestamp.ps1
param (
    [Parameter(Mandatory=$true, HelpMessage="Enter the folder path containing files")]
    [string]$FolderPath,

    [Parameter(Mandatory=$true, HelpMessage="Use creation time (1) or modified time (2)")]
    [ValidateSet("1", "2")]
    [string]$TimeType,

    [Parameter(Mandatory=$false, HelpMessage="Comma-separated list of file extensions (e.g., .png,.jpg)")]
    [string]$Extensions
)

# Validate folder path
if (-not (Test-Path -Path $FolderPath -PathType Container)) {
    Write-Error "The provided path '$FolderPath' is not a valid directory."
    exit 1
}

# Default extensions if none provided
$defaultExtensions = @(".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".mp4", ".avi", ".mov", ".mkv", ".3gp", ".amr", ".3gpp", ".aac", ".m4a", ".mp3")
$fileExtensions = if ($Extensions) { $Extensions -split "," | ForEach-Object { $_.Trim().ToLower() } } else { $defaultExtensions }

# Get all files in the folder with matching extensions
$files = Get-ChildItem -Path $FolderPath | Where-Object { $_.Extension -in $fileExtensions }
$totalFiles = $files.Count
$currentFile = 0

# Iterate through files
foreach ($file in $files) {
    $currentFile++
    $percentComplete = ($currentFile / $totalFiles) * 100
    Write-Progress -Activity "Renaming Files" -Status "Processing $($file.Name)" -PercentComplete $percentComplete

    # Get the selected timestamp
    $timestamp = if ($TimeType -eq "1") { $file.CreationTime } else { $file.LastWriteTime }
    $timestampMs = [int64](($timestamp - (Get-Date "1970-01-01")).TotalMilliseconds)

    # Get file extension
    $ext = $file.Extension

    # Create new filename with timestamp
    $newFilename = "$timestampMs$ext"
    $newFilePath = Join-Path -Path $FolderPath -ChildPath $newFilename

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
        $newFilePath = Join-Path -Path $FolderPath -ChildPath $newFilename
        $counter++
    }

    # Rename the file
    try {
        Rename-Item -Path $file.FullName -NewName $newFilename -ErrorAction Stop
        Write-Host "Renamed: $($file.Name) -> $newFilename"
    }
    catch {
        Write-Host "Error renaming $($file.Name): $_"
    }
}

Write-Progress -Activity "Renaming Files" -Completed
Write-Host "File renaming completed."
# Set-VideoMetadata.ps1
# Processes all video files in a user-specified folder, setting each filename as the metadata description

# Check if ffmpeg is installed
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Error "ffmpeg not found. Please install ffmpeg and add it to your PATH."
    exit 1
}

# Prompt for the folder path
$folderPath = Read-Host "Enter the full path to the folder containing video files"

# Normalize and validate folder path
$folderPath = [System.IO.Path]::GetFullPath($folderPath.Trim())
Write-Host "Scanning folder: $folderPath"

if (-not (Test-Path $folderPath -PathType Container)) {
    Write-Error "The specified folder does not exist."
    exit 1
}

# Define common video file extensions
$videoExtensions = @("*.mp4", "*.mkv", "*.avi", "*.mov", "*.wmv", "*.flv")

# Get all video files in the folder
$videoFiles = @()
foreach ($ext in $videoExtensions) {
    $videoFiles += Get-ChildItem -Path $folderPath -Filter $ext -File -ErrorAction SilentlyContinue
}

# Debug: List found files
Write-Host "Found $($videoFiles.Count) video file(s):"
$videoFiles | ForEach-Object { Write-Host " - $($_.Name)" }

if ($videoFiles.Count -eq 0) {
    Write-Host "No video files found in the specified folder. Ensure the folder contains files with extensions: $($videoExtensions -join ', ')"
    exit 0
}

# Process each video file
foreach ($file in $videoFiles) {
    $filename = $file.BaseName # Filename without extension
    $directory = $file.DirectoryName
    $extension = $file.Extension
    $outputFile = Join-Path $directory "temp_output$extension"

    Write-Host "Processing: $($file.Name)"

    # Use ffmpeg to set the metadata description to the filename
    $ffmpegCommand = "ffmpeg -i `"$($file.FullName)`" -c copy -metadata description=`"$filename`" `"$outputFile`" -y"
    Invoke-Expression $ffmpegCommand

    # Check if ffmpeg was successful
    if ($LASTEXITCODE -eq 0) {
        # Replace original file with the new one
        Remove-Item $file.FullName
        Rename-Item $outputFile $file.Name
        Write-Host "Metadata updated for $($file.Name). Description set to: $filename"
    } else {
        Write-Error "Failed to update metadata for $($file.Name)."
        if (Test-Path $outputFile) { Remove-Item $outputFile }
    }
}

Write-Host "Processing complete."
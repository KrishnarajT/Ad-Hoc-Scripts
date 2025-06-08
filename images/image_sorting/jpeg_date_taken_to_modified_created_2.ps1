<#
.SYNOPSIS
    Updates the Date Modified and Date Created timestamps of JPEG images in a user-specified folder and its subfolders based on their EXIF Date Taken metadata, with an optional time offset.

.DESCRIPTION
    This script prompts the user for a folder path and an optional time offset in hours (e.g., +5.5 or -5.5). It recursively scans the folder for .jpg and .jpeg files, extracts the Date Taken from the EXIF metadata,
    applies the specified offset, and sets the file's Date Modified and Date Created to the adjusted time. Uses multiple date parsing methods for robustness. Displays a progress bar during processing.

.PARAMETER OffsetHours
    Optional. The number of hours to add (positive) or subtract (negative) from the EXIF Date Taken timestamp. Defaults to 0.

.EXAMPLE
    Run the script in PowerShell, enter the folder path (e.g., "\\KRISH-HOME-NAS\Photos"), and specify an offset (e.g., 5.5 for +5.5 hours).
#>

# Log PowerShell version for debugging
Write-Output "PowerShell Version: $($PSVersionTable.PSVersion)"

# Prompt user for folder path
$FolderPath = Read-Host "Please enter the full path to the folder containing JPEG images"

# Check if the folder exists
if (-not (Test-Path -Path $FolderPath -PathType Container)) {
    Write-Error "The specified folder does not exist or is not a directory: $FolderPath"
    exit
}

# Prompt user for time offset in hours
$offsetInput = Read-Host "Enter time offset in hours (e.g., +5.5 or -5.5, default is 0)"
if ($offsetInput -eq "") {
    $OffsetHours = 0
} else {
    try {
        $OffsetHours = [double]::Parse($offsetInput)
    } catch {
        Write-Error "Invalid offset value: $offsetInput. Please enter a valid number (e.g., +5.5 or -5.5)."
        exit
    }
}

# Load Windows Shell for accessing EXIF data
try {
    $shell = New-Object -ComObject Shell.Application
} catch {
    Write-Error "Failed to initialize Shell.Application COM object: $_"
    exit
}

# Define common EXIF date formats
$dateFormats = @(
    "MM/dd/yyyy HH:mm:ss",
    "yyyy:MM:dd HH:mm:ss",
    "dd/MM/yyyy HH:mm:ss",
    "yyyy-MM-dd HH:mm:ss",
    "yyyy-MM-dd HH:mm",
    "MM/dd/yyyy HH:mm"
)

# Get all .jpg and .jpeg files recursively
$images = Get-ChildItem -Path $FolderPath -Include *.jpg,*.jpeg -File -Recurse -ErrorAction SilentlyContinue

# Check if any images were found
if ($images.Count -eq 0) {
    Write-Warning "No .jpg or .jpeg files found in $FolderPath or its subfolders."
    exit
}

# Initialize counters
$processedCount = 0
$skippedCount = 0
$errorCount = 0
$totalFiles = $images.Count
$currentFile = 0

# Process each image
foreach ($image in $images) {
    $currentFile++
    Write-Progress -Activity "Processing JPEG files" -Status "File $currentFile of $totalFiles" -PercentComplete (($currentFile / $totalFiles) * 100)
    
    try {
        # Get the folder for the current file's directory
        $fileDir = Split-Path -Path $image.FullName -Parent
        $folder = $shell.NameSpace($fileDir)
        $file = $folder.ParseName($image.Name)
        
        if ($null -eq $file) {
            Write-Warning "Unable to access file $($image.FullName) via Shell interface."
            $skippedCount++
            continue
        }

        # Get the Date Taken property
        $dateTakenString = $file.ExtendedProperty("System.Photo.DateTaken")
        
        if ($dateTakenString) {
            $parsed = $false
            $dateTaken = $null
            $dateTakenString = $dateTakenString -replace '[^\x20-\x7E]', ''
            
            # Try each date format
            foreach ($format in $dateFormats) {
                try {
                    if ([DateTime]::TryParseExact($dateTakenString, $format, [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::None, [ref]$dateTaken)) {
                        $adjustedDate = $dateTaken.AddHours($OffsetHours)
                        $image.CreationTime = $adjustedDate
                        $image.LastWriteTime = $adjustedDate
                        
                        Write-Output "Updated $($image.FullName): Set CreationTime and LastWriteTime to $adjustedDate (Format: $format, Offset: $OffsetHours hours)"
                        $processedCount++
                        $parsed = $true
                        break
                    }
                } catch {
                    Write-Warning "Failed to parse date for $($image.FullName) with format '$format'. Date string: '$dateTakenString'. Error: $_"
                    continue
                }
            }
            
            # Fallback to DateTime.Parse
            if (-not $parsed) {
                try {
                    $dateTaken = [DateTime]::Parse($dateTakenString)
                    $adjustedDate = $dateTaken.AddHours($OffsetHours)
                    $image.CreationTime = $adjustedDate
                    $image.LastWriteTime = $adjustedDate
                    
                    Write-Output "Updated $($image.FullName): Set CreationTime and LastWriteTime to $adjustedDate (Fallback: DateTime.Parse, Offset: $OffsetHours hours)"
                    $processedCount++
                    $parsed = $true
                } catch {
                    Write-Warning "Fallback parse failed for $($image.FullName). Date string: '$dateTakenString'. Error: $_"
                }
            }
            
            if (-not $parsed) {
                Write-Warning "Invalid Date Taken format for $($image.FullName). Date string: '$dateTakenString'. Tried formats: $($dateFormats -join ', ')"
                $skippedCount++
            }
        } else {
            Write-Warning "No Date Taken metadata found for $($image.FullName)"
            $skippedCount++
        }
    } catch {
        Write-Error "Failed to process $($image.FullName): $_"
        $errorCount++
    }
}

# Complete progress bar
Write-Progress -Activity "Processing JPEG files" -Completed

# Summary
$summary = @"
Processing Summary:
Time offset applied: $OffsetHours hours
Total files processed: $processedCount
Files skipped (no/invalid Date Taken): $skippedCount
Files with errors: $errorCount
Processing complete.
"@
Write-Output $summary
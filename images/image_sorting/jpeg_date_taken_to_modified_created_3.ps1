# UpdateJpegTimestamps.ps1
<#
.SYNOPSIS
    Updates the Date Modified and Date Created timestamps of JPEG images in a specified folder based on their EXIF Date Taken metadata, with an optional time offset.
... (rest of the header remains the same)
#>

param (
    [Parameter(Mandatory=$true, HelpMessage="Enter the full path to the folder containing JPEG images")]
    [string]$FolderPath,

    [Parameter(Mandatory=$false, HelpMessage="Enter time offset in hours (e.g., +5.5 or -5.5, default is 0)")]
    [double]$OffsetHours = 0,

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

# Log PowerShell version for debugging
Write-Log -Message "PowerShell Version: $($PSVersionTable.PSVersion)" -Level "INFO"

# Check if the folder exists
if (-not (Test-Path -Path $FolderPath -PathType Container)) {
    Write-Log -Message "The specified folder does not exist or is not a directory: $FolderPath" -Level "ERROR"
    exit 1
}

# Log the scanning mode
Write-Log -Message "Scanning $(if ($Recurse) { 'recursively' } else { 'non-recursively' }) in $FolderPath for .jpg and .jpeg files" -Level "INFO"

# Load Windows Shell for accessing EXIF data
try {
    $shell = New-Object -ComObject Shell.Application
} catch {
    Write-Log -Message "Failed to initialize Shell.Application COM object: $_" -Level "ERROR"
    exit 1
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

# Get all .jpg and .jpeg files
Write-Log -Message "Starting file enumeration..." -Level "INFO"
$images = if ($Recurse) {
    Get-ChildItem -Path $FolderPath -File -Recurse -ErrorAction SilentlyContinue -Include "*.jpg","*.jpeg"
} else {
    Get-ChildItem -Path $FolderPath -File -ErrorAction SilentlyContinue -Include "*.jpg","*.jpeg"
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

# Check if any images were found
if ($null -eq $images -or $images.Count -eq 0) {
    Write-Log -Message "No .jpg or .jpeg files found in $FolderPath$(if ($Recurse) { ' or its subfolders' })." -Level "WARNING"
    # Diagnostic: List files in the root folder to help troubleshoot
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
$processedCount = 0
$skippedCount = 0
$errorCount = 0
$totalFiles = $images.Count
$currentFile = 0

# Process each image
foreach ($image in $images) {
    $currentFile++
    Write-Progress -Activity "Processing JPEG files" -Status "File $currentFile of $totalFiles" -PercentComplete (($currentFile / $totalFiles) * 100)

    # Validate image object
    if ($null -eq $image -or [string]::IsNullOrEmpty($image.FullName)) {
        Write-Log -Message "Invalid file object encountered at index $currentFile." -Level "ERROR"
        $errorCount++
        continue
    }

    Write-Log -Message "Processing file: $($image.FullName)" -Level "INFO"

    try {
        # Get the folder for the current file's directory
        $fileDir = Split-Path -Path $image.FullName -Parent
        $folder = $shell.NameSpace($fileDir)
        if ($null -eq $folder) {
            Write-Log -Message "Unable to access directory for file $($image.FullName) via Shell interface." -Level "WARNING"
            $skippedCount++
            continue
        }

        $file = $folder.ParseName($image.Name)
        if ($null -eq $file) {
            Write-Log -Message "Unable to access file $($image.FullName) via Shell interface." -Level "WARNING"
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

                        Write-Log -Message "Updated $($image.FullName): Set CreationTime and LastWriteTime to $adjustedDate (Format: $format, Offset: $OffsetHours hours)" -Level "INFO"
                        $processedCount++
                        $parsed = $true
                        break
                    }
                } catch {
                    Write-Log -Message "Failed to parse date for $($image.FullName) with format '$format'. Date string: '$dateTakenString'. Error: $_" -Level "WARNING"
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

                    Write-Log -Message "Updated $($image.FullName): Set CreationTime and LastWriteTime to $adjustedDate (Fallback: DateTime.Parse, Offset: $OffsetHours hours)" -Level "INFO"
                    $processedCount++
                    $parsed = $true
                } catch {
                    Write-Log -Message "Fallback parse failed for $($image.FullName). Date string: '$dateTakenString'. Error: $_" -Level "WARNING"
                }
            }

            if (-not $parsed) {
                Write-Log -Message "Invalid Date Taken format for $($image.FullName). Date string: '$dateTakenString'. Tried formats: $($dateFormats -join ', ')" -Level "WARNING"
                $skippedCount++
            }
        } else {
            Write-Log -Message "No Date Taken metadata found for $($image.FullName)" -Level "WARNING"
            $skippedCount++
        }
    } catch {
        Write-Log -Message "Failed to process $($image.FullName): $_" -Level "ERROR"
        $errorCount++
    }
}

# Complete progress bar
Write-Progress -Activity "Processing JPEG files" -Completed

# Summary (always displayed, regardless of LogToConsole)
$summary = @"
Processing Summary:
Time offset applied: $OffsetHours hours
Total files processed: $processedCount
Files skipped (no/invalid Date Taken): $skippedCount
Files with errors: $errorCount
Processing complete.
"@
Write-Output $summary
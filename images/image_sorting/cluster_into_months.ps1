# Simplify the PowerShell prompt to show only the current directory
function prompt {
    $currentDir = (Get-Location).Path
    "PS $currentDir> "
}

# Store the original directory to return to it later
$originalDir = (Get-Location).Path

# Prompt the user for the root folder path, defaulting to current directory if empty
$rootFolder = Read-Host "Please enter the path to the root folder containing the files (press Enter for current directory)"
if ([string]::IsNullOrWhiteSpace($rootFolder)) {
    $rootFolder = $originalDir
}

# Check if the provided folder exists
if (-not (Test-Path -Path $rootFolder -PathType Container)) {
    Write-Host "Error: The folder '$rootFolder' does not exist. Please provide a valid folder path."
    exit
}

# Prompt the user to choose organization method
$orgMethod = Read-Host "Organize files by 'month' (e.g., months/january/file) or by 'year' (e.g., years/2011/months/january/file)? Enter 'month' or 'year'"
$orgMethod = $orgMethod.ToLower()

# Validate organization method
if ($orgMethod -ne 'month' -and $orgMethod -ne 'year') {
    Write-Host "Error: Invalid input. Please enter 'month' or 'year'."
    exit
}

# Change to the specified directory
Set-Location -Path $rootFolder

# Get all files in the specified directory
$files = Get-ChildItem -File

# Initialize progress bar variables
$totalFiles = $files.Count
$currentFile = 0

# Array of month names in lowercase for folder creation
$monthNames = @("january", "february", "march", "april", "may", "june", 
                "july", "august", "september", "october", "november", "december")

# Create the root directory for organization
$baseDir = if ($orgMethod -eq 'month') { "months" } else { "years" }
$basePath = Join-Path $rootFolder $baseDir
if (-not (Test-Path $basePath)) {
    New-Item -ItemType Directory -Path $basePath | Out-Null
}

foreach ($file in $files) {
    $currentFile++
    $percentComplete = ($currentFile / $totalFiles) * 100

    # Update progress bar
    Write-Progress -Activity "Organizing files by $orgMethod" `
                   -Status "Processing file $currentFile of $totalFiles" `
                   -PercentComplete $percentComplete `
                   -CurrentOperation $file.Name

    # Try to parse the filename (without extension) as a Unix timestamp in milliseconds
    $filename = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
    
    if ($filename -match '^\d+$') {
        try {
            # Convert Unix timestamp (ms) to DateTime in system timezone
            $epoch = [DateTimeOffset]::FromUnixTimeMilliseconds([long]$filename)
            $date = $epoch.ToLocalTime().DateTime

            # Get the month name and year
            $monthName = $monthNames[$date.Month - 1]
            $year = $date.Year

            # Determine the destination path based on organization method
            if ($orgMethod -eq 'month') {
                $monthPath = Join-Path $basePath $monthName
                $destination = Join-Path $monthPath $file.Name
            } else {
                $yearPath = Join-Path $basePath $year
                $monthDir = Join-Path $yearPath "months"
                $monthPath = Join-Path $monthDir $monthName
                $destination = Join-Path $monthPath $file.Name
            }

            # Create the necessary folders if they don't exist
            $parentPath = [System.IO.Path]::GetDirectoryName($destination)
            if (-not (Test-Path $parentPath)) {
                # Explicitly create each directory level for year-based organization
                if ($orgMethod -eq 'year') {
                    if (-not (Test-Path $yearPath)) {
                        New-Item -ItemType Directory -Path $yearPath | Out-Null
                    }
                    if (-not (Test-Path $monthDir)) {
                        New-Item -ItemType Directory -Path $monthDir | Out-Null
                    }
                    if (-not (Test-Path $monthPath)) {
                        New-Item -ItemType Directory -Path $monthPath | Out-Null
                    }
                } else {
                    New-Item -ItemType Directory -Path $parentPath -Force | Out-Null
                }
            }

            # Move the file to the corresponding folder
            Move-Item -Path $file.FullName -Destination $destination -Force
            Write-Host "Moved $($file.Name) to $destination"
        }
        catch {
            Write-Host "Skipping $($file.Name): Invalid Unix timestamp - $_"
        }
    }
    else {
        Write-Host "Skipping $($file.Name): Filename is not a valid Unix timestamp"
    }
}

# Complete the progress bar
Write-Progress -Activity "Organizing files by $orgMethod" -Completed

# Return to the original directory
Set-Location -Path $originalDir
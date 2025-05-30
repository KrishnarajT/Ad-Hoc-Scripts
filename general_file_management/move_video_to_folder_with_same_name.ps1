# PowerShell script to organize video files into folders named after the files
param (
    [Parameter(Mandatory=$true)]
    [string]$FolderPath,
    [switch]$Recurse = $false
)

# Validate if the folder exists
if (-not (Test-Path -Path $FolderPath -PathType Container)) {
    Write-Error "The specified folder path does not exist or is not a directory: $FolderPath"
    exit 1
}

# Resolve the full path to handle relative paths
$FolderPath = Resolve-Path -Path $FolderPath
Write-Host "Processing folder: $FolderPath"

# Define common video file extensions (case-insensitive)
$videoExtensions = @(".avi", ".mp4", ".mkv", ".m4a", ".mov", ".wmv", ".flv", ".mpeg", ".mpg", ".m4v", ".webm", ".ogv", ".3gp")

# Get all files in the specified folder and filter for video extensions
$searchParams = @{
    Path = "$FolderPath\*"
    File = $true
}
if ($Recurse) {
    $searchParams.Recurse = $true
}

$allFiles = Get-ChildItem @searchParams
$videoFiles = $allFiles | Where-Object { $videoExtensions -contains $_.Extension.ToLower() }

# Check if any video files were found
if ($videoFiles.Count -eq 0) {
    Write-Host "No video files found in '$FolderPath' with extensions: $($videoExtensions -join ', ')"
    Write-Host "Recurse option enabled: $Recurse"
    Write-Host "Listing all files in the folder for debugging:"
    $allFiles | ForEach-Object {
        Write-Host " - $($_.Name) (Extension: $($_.Extension))"
    }
    exit 0
}

# Process each video file
foreach ($file in $videoFiles) {
    # Get the file name without extension
    $fileNameWithoutExtension = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
    
    # Define the new folder path (in the same directory as the file)
    $newFolderPath = Join-Path -Path $file.DirectoryName -ChildPath $fileNameWithoutExtension
    
    try {
        # Create the new folder if it doesn't exist
        if (-not (Test-Path -Path $newFolderPath)) {
            New-Item -Path $newFolderPath -ItemType Directory | Out-Null
            Write-Host "Created folder: $newFolderPath"
        }
        
        # Define the destination path for the file
        $destinationPath = Join-Path -Path $newFolderPath -ChildPath $file.Name
        
        # Check if the file is already in the correct folder
        if ($file.FullName -eq $destinationPath) {
            Write-Host "File '$($file.Name)' is already in correct folder: $newFolderPath"
            continue
        }
        
        # Move the file to the new folder
        Move-Item -Path $file.FullName -Destination $destinationPath -ErrorAction Stop
        Write-Host "Moved '$($file.Name)' to '$newFolderPath'"
    }
    catch {
        Write-Error "Error processing '$($file.Name)': $_"
    }
}

Write-Host "Video file organization completed."
# Prompt user for the root folder path
$rootPath = Read-Host "Enter the full path of the root folder"

# Check if path exists
if (-Not (Test-Path -Path $rootPath)) {
    Write-Host "The path you entered does not exist. Exiting script."
    exit
}

# Get all files from subfolders (excluding the root folder itself)
$files = Get-ChildItem -Path $rootPath -Recurse -File | Where-Object { $_.DirectoryName -ne $rootPath }

# Initialize progress bar variables
$totalFiles = $files.Count
$currentFile = 0

# Move each file to the root folder
foreach ($file in $files) {
    $currentFile++
    $percentComplete = ($currentFile / $totalFiles) * 100

    # Update progress bar
    Write-Progress -Activity "Moving files to root folder" `
                   -Status "Processing file $currentFile of $totalFiles" `
                   -PercentComplete $percentComplete `
                   -CurrentOperation $file.Name

    $destination = Join-Path -Path $rootPath -ChildPath $file.Name

    # If file with the same name exists, add a unique suffix
    if (Test-Path -Path $destination) {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
        $extension = $file.Extension
        $counter = 1
        do {
            $newName = "$baseName`_copy$counter$extension"
            $destination = Join-Path -Path $rootPath -ChildPath $newName
            $counter++
        } while (Test-Path -Path $destination)
    }

    # Move the file
    Move-Item -Path $file.FullName -Destination $destination
}

# Complete the progress bar
Write-Progress -Activity "Moving files to root folder" -Completed
Write-Host "✅ All files have been moved to the root folder."
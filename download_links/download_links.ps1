# Define the input file containing links
$inputFile = "links.txt"

# Define the download folder
$outputFolder = "."

# Create the folder if it doesn't exist
if (!(Test-Path -Path $outputFolder)) {
    New-Item -ItemType Directory -Path $outputFolder | Out-Null
}

# Read URLs from the file
$urls = Get-Content $inputFile

# Loop through each URL and download
foreach ($url in $urls) {
    try {
        # Extract filename from URL
        $fileName = [System.IO.Path]::GetFileName($url)
        $outputPath = Join-Path -Path $outputFolder -ChildPath $fileName

        # Download the file
        Invoke-WebRequest -Uri $url -OutFile $outputPath

        Write-Host "Downloaded: $url -> $outputPath"
    }
    catch {
        Write-Host "Failed to download: $url" -ForegroundColor Red
    }
}

Write-Host "Download process completed."

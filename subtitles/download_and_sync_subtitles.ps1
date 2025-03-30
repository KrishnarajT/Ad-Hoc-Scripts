# Define the subtitle language
$language = "en"

# Ask the user for action preference
$action = Read-Host "Enter '1' to only download subtitles or '2' to download and sync"

# Get all video files in subdirectories
$videoFiles = Get-ChildItem -Path . -Recurse -File | Where-Object { $_.Extension -match "\.mp4|\.mkv|\.avi|\.mov|\.wmv" }

foreach ($video in $videoFiles) {
    # Construct the command to download subtitles
    $command = "subliminal download -l $language `"$($video.FullName)`""

    # Run the command to download subtitles
    Write-Host "Downloading subtitles for: $($video.FullName)"
    Invoke-Expression $command

    if ($action -eq "2") {
        # Get the expected subtitle file name (assuming .srt format)
        $subtitleFile = [System.IO.Path]::ChangeExtension($video.FullName, ".$language.srt")

        # Check if subtitle file exists before syncing
        if (Test-Path $subtitleFile) {
            Write-Host "Synchronizing subtitles for: $($video.FullName)"
            
            # Construct the ffsubsync command
            $syncCommand = "ffsubsync `"$($video.FullName)`" -i `"$subtitleFile`" -o `"$subtitleFile`""
            
            # Run ffsubsync to sync subtitles
            Invoke-Expression $syncCommand
            Write-Host "Subtitle synchronization completed for: $($video.FullName)"
        } else {
            Write-Host "No subtitles found for: $($video.FullName), skipping sync."
        }
    }
}

param (
    [string]$musicDir
)

# If no directory is provided, prompt the user
if (-not $musicDir) {
    $musicDir = Read-Host "Enter the full path to your music folder"
}

# Verify directory exists
if (-not (Test-Path $musicDir)) {
    Write-Host "The specified directory does not exist." -ForegroundColor Red
    exit
}

# Get all supported audio files
$songs = Get-ChildItem -Path $musicDir -Include *.mp3, *.flac, *.wav -Recurse

if ($songs.Count -eq 0) {
    Write-Host "No supported audio files found in $musicDir" -ForegroundColor Yellow
    exit
}

foreach ($song in $songs) {
    Write-Host "Processing: $($song.FullName)" -ForegroundColor Cyan
    
    # Run beets import in pretend mode
    $result = beet import --pretend --autotag --quiet "`"$($song.FullName)`""
    
    Write-Host $result -ForegroundColor Green
    Write-Host "`n-------------------------------`n"
}

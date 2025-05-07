# PowerShell script to prompt user for playlists.txt, read playlists, fetch songs using yt-dlp, and create M3U files in an output folder
# doesnt add songs that it wont find on youtube. 
# Parameters
param (
    [string]$OutputFolder = "M3UPlaylists"
)

# Check if yt-dlp is installed
if (-not (Get-Command yt-dlp -ErrorAction SilentlyContinue)) {
    Write-Error "yt-dlp is not installed or not found in PATH. Please install yt-dlp first."
    exit 1
}

# Prompt user for playlist file path
$defaultPlaylistFile = "playlists.txt"
$playlistFile = Read-Host "Enter path to playlists.txt (or press Enter for default: $defaultPlaylistFile)"
if ([string]::IsNullOrWhiteSpace($playlistFile)) {
    $playlistFile = $defaultPlaylistFile
}

# Check if playlists.txt exists
if (-not (Test-Path $playlistFile)) {
    Write-Error "Playlist file '$playlistFile' not found."
    exit 1
}

# Create output folder if it doesn't exist
if (-not (Test-Path $OutputFolder)) {
    New-Item -ItemType Directory -Path $OutputFolder | Out-Null
}

try {
    # Read playlist URLs from file
    $playlists = Get-Content $playlistFile | Where-Object { $_ -match '\S' } | ForEach-Object { $_.Trim() }

    foreach ($playlistUrl in $playlists) {
        # Skip empty or invalid URLs
        if (-not ($playlistUrl -match '^https?://')) {
            Write-Warning "Skipping invalid URL: $playlistUrl"
            continue
        }

        # Get playlist information using yt-dlp
        $playlistData = yt-dlp --flat-playlist --dump-json $playlistUrl | ConvertFrom-Json

        $safeTitle = $playlistUrl -replace '[<>:\"/\\|?*]', '_'
        $outputM3U = Join-Path $OutputFolder "$safeTitle.m3u"

        # Create M3U file
        "#EXTM3U" | Out-File -FilePath $outputM3U -Encoding UTF8

        Write-Output "Processing playlist: $playlistTitle"

        # Process each video/song in the playlist
        foreach ($item in $playlistData) {
            if ($item.title) {
                $songTitle = $item.title

                # Write song title to M3U file (just the name, no path)
                "#EXTINF:-1,$songTitle" | Out-File -FilePath $outputM3U -Append -Encoding UTF8
                "$songTitle" | Out-File -FilePath $outputM3U -Append -Encoding UTF8

                # Output the song title to console
                Write-Output "  $songTitle"
            }
        }

        Write-Output "M3U playlist saved to $outputM3U`n"
    }
}
catch {
    Write-Error "An error occurred: $_"
    exit 1
}
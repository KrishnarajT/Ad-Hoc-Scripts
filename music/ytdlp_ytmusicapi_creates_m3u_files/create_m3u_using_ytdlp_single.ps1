# PowerShell script to list songs from a YouTube playlist using yt-dlp and create an M3U file with song names
# only one playlist
# Parameters
param (
    [Parameter(Mandatory=$true)]
    [string]$PlaylistURL,
    [string]$OutputM3U = "playlist.m3u"
)

# Check if yt-dlp is installed
if (-not (Get-Command yt-dlp -ErrorAction SilentlyContinue)) {
    Write-Error "yt-dlp is not installed or not found in PATH. Please install yt-dlp first."
    exit 1
}

try {
    # Get playlist information using yt-dlp
    $playlistData = yt-dlp --flat-playlist --dump-json $PlaylistURL | ConvertFrom-Json

    # Create M3U file
    "#EXTM3U" | Out-File -FilePath $OutputM3U -Encoding UTF8

    # Process each video/song in the playlist
    foreach ($item in $playlistData) {
        # Get the song title
        $songTitle = $item.title
        
        # Write song title to M3U file (just the name, no path)
        "#EXTINF:-1,$songTitle" | Out-File -FilePath $OutputM3U -Append -Encoding UTF8
        "$songTitle" | Out-File -FilePath $OutputM3U -Append -Encoding UTF8

        # Output the song title to console
        Write-Output $songTitle
    }

    Write-Output "`nM3U playlist saved to $OutputM3U"
}
catch {
    Write-Error "An error occurred: $_"
    exit 1
}
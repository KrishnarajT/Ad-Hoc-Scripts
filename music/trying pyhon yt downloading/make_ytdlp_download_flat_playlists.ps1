# Define input and output paths
$inputFile = "youtube_playlists.txt"
$outputFile = "playlist_links.json"

# Create an empty hashtable to store results
$allPlaylists = @{}

# Read each playlist URL
Get-Content $inputFile | ForEach-Object {
    $playlistUrl = $_.Trim()
    if (-not $playlistUrl) { return }

    Write-Host "`n🎧 Processing: $playlistUrl"

    # Use yt-dlp to extract video URLs from playlist
    $trackUrls = yt-dlp --flat-playlist --print "%(url)s" $playlistUrl 2>$null

    if ($trackUrls) {
        $allPlaylists[$playlistUrl] = $trackUrls
        Write-Host "✅ Found $($trackUrls.Count) tracks"
    } else {
        Write-Host "⚠️ Failed to extract from $playlistUrl"
    }
}

# Convert hashtable to JSON and save
$allPlaylists | ConvertTo-Json -Depth 3 | Set-Content $outputFile -Encoding UTF8

Write-Host "`n Done. Output saved to $outputFile"

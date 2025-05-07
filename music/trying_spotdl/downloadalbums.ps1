# powershell script to iterate through links in albums.txt and run a command with it
# command is: uv run spotdl <url> --generate-lrc --client-id 27840c6f64d848c2a8aa7d4a3b47874f --client-secret 8326a594ffa549c4bcb6de24199836d2 --lyrics --output "Music/{artist}/{album}/{title}.{output-ext}" --preload

# --client-id 27840c6f64d848c2a8aa7d4a3b47874f `
# --client-secret 8326a594ffa549c4bcb6de24199836d2 `


# Path to your file containing album URLs
$albumFile = "albums.txt"

# Read each line (album URL) from the file
Get-Content $albumFile | ForEach-Object {
    $url = $_.Trim()
    if ($url -ne "") {
        Write-Host "Downloading: $url"
        uv run spotdl $url `
            --generate-lrc `
            --lyrics `
            --output "Music/{artist}/{album}/{title}.{output-ext}" `
            --preload
    }
    Write-Host "Finished downloading: $url"
    Write-Host "----------------------------------------"
}

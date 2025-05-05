param (
    [string]$RepoListPath = "repositories.txt"
)

# Check if file exists
if (-not (Test-Path $RepoListPath)) {
    Write-Error "File not found: $RepoListPath"
    exit 1
}

$threshold = 100MB

# Read each repo path
Get-Content $RepoListPath | ForEach-Object {
    $repoPath = $_.Trim()
    
    if (-not (Test-Path $repoPath)) {
        Write-Warning "Path does not exist: $repoPath"
        return
    }

    $gitDir = Join-Path $repoPath ".git"
    if (-not (Test-Path $gitDir)) {
        Write-Warning "Not a git repo (no .git folder): $repoPath"
        return
    }

    Write-Output "`n[+] Processing: $repoPath"

    $gitignorePath = Join-Path $repoPath ".gitignore"

    # Ensure .gitignore exists
    if (-not (Test-Path $gitignorePath)) {
        New-Item -ItemType File -Path $gitignorePath | Out-Null
    }

    # Read current ignore entries
    $existingIgnores = Get-Content $gitignorePath -ErrorAction SilentlyContinue

    # Detect and add large files
    $changesMade = $false
    Get-ChildItem -Path $repoPath -Recurse -File | Where-Object { $_.Length -gt $threshold } | ForEach-Object {
        $relativePath = $_.FullName.Replace($repoPath + "\", "").Replace("\", "/")

        if ($existingIgnores -notcontains $relativePath) {
            Add-Content -Path $gitignorePath -Value $relativePath
            Write-Output "  - Added to .gitignore: $relativePath"
            $changesMade = $true
        }
    }

    # Commit .gitignore if changed
    if ($changesMade) {
        Push-Location $repoPath
        git add .gitignore
        git commit -m "Update .gitignore with large files" | Out-Null
        git push | Out-Null
        Pop-Location
        Write-Output "Pushed .gitignore updates."
    }

    # Stage and push all other changes
    Push-Location $repoPath
	git status
	git add .
	git status
    if ((git status --porcelain) -ne "") {
        git commit -m "Update project changes" | Out-Null
        git push | Out-Null
        Write-Output "Pushed additional changes."
    } else {
        Write-Output "No other changes to push."
    }
    Pop-Location
}

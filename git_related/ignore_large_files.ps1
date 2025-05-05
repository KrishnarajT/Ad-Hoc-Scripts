param (
    [string]$RepoRoot = $(Read-Host "Enter the path to your Git repository root")
)

# Normalize the path
$RepoRoot = (Resolve-Path $RepoRoot).Path.TrimEnd('\')

# Validate directory
if (-not (Test-Path "$RepoRoot\.git")) {
    Write-Error "No .git directory found at $RepoRoot. Please check the path."
    exit 1
}

$gitignorePath = Join-Path $RepoRoot ".gitignore"
$threshold = 100MB

# Ensure .gitignore exists
if (-not (Test-Path $gitignorePath)) {
    New-Item -ItemType File -Path $gitignorePath | Out-Null
}

# Read existing ignore entries
$existingIgnores = Get-Content $gitignorePath -ErrorAction SilentlyContinue

# Get all files > 100MB under the repo
Get-ChildItem -Path $RepoRoot -Recurse -File | Where-Object { $_.Length -gt $threshold } | ForEach-Object {
    $relativePath = $_.FullName.Replace($RepoRoot + "\", "").Replace("\", "/")

    if ($existingIgnores -notcontains $relativePath) {
        Add-Content -Path $gitignorePath -Value $relativePath
        Write-Output "Added to .gitignore: $relativePath"
    } else {
        Write-Output "Already in .gitignore: $relativePath"
    }
}

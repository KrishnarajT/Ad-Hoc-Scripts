param (
    [string]$RepoRoot = $(Read-Host "Enter the path to your Git repository root"),
    [string]$ExtensionsInput = $(Read-Host "Enter file extensions to include (comma separated, e.g. 'txt,log,png')")
)

# Validate repo root
if (-not (Test-Path $RepoRoot)) {
    Write-Error "The path '$RepoRoot' does not exist. Please check the path."
    exit 1
}

# Normalize repo root full path
$RepoRoot = [System.IO.Path]::GetFullPath($RepoRoot).TrimEnd('\','/')

# Process extensions
$extensions = $ExtensionsInput.Split(",") | ForEach-Object {
    $_.Trim().TrimStart('.').ToLower()
}

function Get-RelativePath {
    param (
        [string]$FullPath,
        [string]$RootPath
    )
    $fullPathNorm = [System.IO.Path]::GetFullPath($FullPath).TrimEnd('\','/')
    $rootPathNorm = [System.IO.Path]::GetFullPath($RootPath).TrimEnd('\','/')

    if ($fullPathNorm -eq $rootPathNorm) {
        return '.'
    }

    $uriFull = New-Object System.Uri ($fullPathNorm)
    $uriRoot = New-Object System.Uri ($rootPathNorm + [System.IO.Path]::DirectorySeparatorChar)

    $relativeUri = $uriRoot.MakeRelativeUri($uriFull)
    $relativePath = [System.Uri]::UnescapeDataString($relativeUri.ToString())

    # Use forward slashes for Git compatibility
    $relativePath = $relativePath -replace '\\', '/'
    return $relativePath
}

Get-ChildItem -Path $RepoRoot -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
    $ext = $_.Extension.TrimStart('.').ToLower()
    $extensions -contains $ext
} | ForEach-Object {
    $relativePath = Get-RelativePath $_.FullName $RepoRoot
    Write-Output $relativePath
}

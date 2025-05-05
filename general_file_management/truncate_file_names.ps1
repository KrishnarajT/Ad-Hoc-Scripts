param (
    [string]$RootDir = $(Read-Host "Enter path to root directory"),
    [int]$MaxLength = 50
)

# Resolve and validate path
$RootDir = (Resolve-Path $RootDir).Path
if (-not (Test-Path $RootDir)) {
    Write-Error "Directory does not exist: $RootDir"
    exit 1
}

Write-Output "Processing directory: $RootDir"
Write-Output "Max filename length: $MaxLength"

# Truncate function
function Truncate-Filename {
    param (
        [string]$filename,
        [int]$maxLength
    )

    $base = [System.IO.Path]::GetFileNameWithoutExtension($filename)
    $ext = [System.IO.Path]::GetExtension($filename)

    $truncated = $base
    if ($base.Length -gt ($maxLength - $ext.Length)) {
        $truncated = $base.Substring(0, $maxLength - $ext.Length)
    }

    return $truncated + $ext
}

# Rename logic
Get-ChildItem -Path $RootDir -Recurse -File | ForEach-Object {
    $originalName = $_.Name
    $parentDir = $_.DirectoryName
    $newName = Truncate-Filename $originalName $MaxLength

    if ($originalName.Length -le $MaxLength) {
        return  # Skip files already within limit
    }

    $newPath = Join-Path $parentDir $newName

    # Ensure uniqueness (add a suffix if name collision occurs)
    $counter = 1
    while (Test-Path $newPath) {
        $base = [System.IO.Path]::GetFileNameWithoutExtension($newName)
        $ext = [System.IO.Path]::GetExtension($newName)
        $suffix = "_$counter"
        $newName = ($base.Substring(0, [Math]::Min($base.Length, $MaxLength - $ext.Length - $suffix.Length))) + $suffix + $ext
        $newPath = Join-Path $parentDir $newName
        $counter++
    }

    Rename-Item -Path $_.FullName -NewName $newName
    Write-Output "Renamed: $originalName → $newName"
}

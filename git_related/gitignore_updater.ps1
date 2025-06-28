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

# Ensure .gitignore exists
if (-not (Test-Path $gitignorePath)) {
    New-Item -ItemType File -Path $gitignorePath | Out-Null
}

# Read existing ignore entries
$existingIgnores = Get-Content $gitignorePath -ErrorAction SilentlyContinue

# Prompt user for choice
Write-Host "Choose an option:"
Write-Host "1. Add files larger than 100MB to .gitignore"
Write-Host "2. Add folders to .gitignore except those containing files with specific extensions"
[int]$choice = 0
while ($choice -ne 1 -and $choice -ne 2) {
    $choice = Read-Host "Enter 1 or 2"
    if ($choice -ne 1 -and $choice -ne 2) {
        Write-Host "Invalid choice. Please enter 1 or 2."
    }
}

switch ($choice) {
    1 {
        $threshold = 100MB
        # Get all files > 100MB under the repo
        Get-ChildItem -Path $RepoRoot -Recurse -File | Where-Object { $_.Length -gt $threshold } | ForEach-Object {
			# Normalize UNC path and get relative path
			$relativePath = $_.FullName.Substring($RepoRoot.Length).TrimStart('\','/') -replace '\\','/'
			# For folders, add trailing slash
			if ($_.PSIsContainer) {
				$relativePath += '/'
			}

            if ($existingIgnores -notcontains $relativePath) {
                Add-Content -Path $gitignorePath -Value $relativePath
                Write-Output "Added to .gitignore: $relativePath"
            } else {
                Write-Output "Already in .gitignore: $relativePath"
            }
        }
    }
    2 {
        # Ask for extensions to exclude (comma separated)
        $extensionsInput = ""
        while ([string]::IsNullOrWhiteSpace($extensionsInput)) {
            $extensionsInput = Read-Host "Enter file extensions to exclude (comma separated, e.g. 'txt,log,png')"
            if ([string]::IsNullOrWhiteSpace($extensionsInput)) {
                Write-Host "Extensions cannot be empty. Please try again."
            }
        }

        # Process extensions: split, trim, lowercase, remove leading dots
        $excludedExtensions = $extensionsInput.Split(",") | ForEach-Object {
            $_.Trim().TrimStart('.').ToLower()
        }

        # Function to check if folder contains excluded extensions files (recursively)
        function ContainsExcludedFiles($folderPath, $excludedExts) {
            # Get all files directly in this folder
            $files = Get-ChildItem -Path $folderPath -File -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                $ext = $file.Extension.TrimStart('.').ToLower()
                if ($excludedExts -contains $ext) {
                    return $true
                }
            }
            # Recursively check subfolders
            $subfolders = Get-ChildItem -Path $folderPath -Directory -ErrorAction SilentlyContinue
            foreach ($subfolder in $subfolders) {
                if (ContainsExcludedFiles $subfolder.FullName $excludedExts) {
                    return $true
                }
            }
            return $false
        }

        # Recursive function to add folders to .gitignore if they don't contain excluded files
        function AddFoldersToGitignore($currentFolder) {
            $subfolders = Get-ChildItem -Path $currentFolder -Directory -ErrorAction SilentlyContinue

            foreach ($subfolder in $subfolders) {
                if (-not (ContainsExcludedFiles $subfolder.FullName $excludedExtensions)) {
                    # Add this folder to .gitignore if not already present
                    $relativePath = $subfolder.FullName.Replace($RepoRoot + "\", "").Replace("\", "/") + "/"
                    if ($existingIgnores -notcontains $relativePath) {
                        Add-Content -Path $gitignorePath -Value $relativePath
                        Write-Output "Added folder to .gitignore: $relativePath"
                    } else {
                        Write-Output "Folder already in .gitignore: $relativePath"
                    }
                }
                else {
                    # Folder contains excluded files, so recurse deeper
                    AddFoldersToGitignore $subfolder.FullName
                }
            }
        }

        # Also handle files directly under repo root (if any)
        $rootFiles = Get-ChildItem -Path $RepoRoot -File -ErrorAction SilentlyContinue
        foreach ($file in $rootFiles) {
            $ext = $file.Extension.TrimStart('.').ToLower()
            if ($excludedExtensions -notcontains $ext) {
                $relativePath = $file.FullName.Replace($RepoRoot + "\", "").Replace("\", "/")
                if ($existingIgnores -notcontains $relativePath) {
                    Add-Content -Path $gitignorePath -Value $relativePath
                    Write-Output "Added file to .gitignore: $relativePath"
                } else {
                    Write-Output "File already in .gitignore: $relativePath"
                }
            }
        }

        # Start recursive folder processing from repo root
        AddFoldersToGitignore $RepoRoot

        Write-Host "Completed adding folders except those containing files with extensions: $($excludedExtensions -join ', ')"
    }
}

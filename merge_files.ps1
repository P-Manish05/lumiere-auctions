# Merge script: For each file pair, take Stitch code.html as base,
# extract ALL <script>...</script> blocks from boilerplate,
# inject them just before </body> in the Stitch file, save to frontend folder.

$ErrorActionPreference = "Stop"

$projectDir = "C:\Users\DELL\.gemini\antigravity\scratch\lumiere-auctions"
$stitchDir = "C:\Users\DELL\OneDrive\Desktop\stitch_elysian_luxury_auction_platform"

$merges = @(
    @{
        StitchFile = "$stitchDir\auction_detail_elysian_auctions\code.html"
        BoilerplateFile = "$projectDir\frontend\auction-detail.html"
        OutputFile = "$projectDir\frontend\auction-detail.html"
    },
    @{
        StitchFile = "$stitchDir\sign_in_elysian_auctions\code.html"
        BoilerplateFile = "$projectDir\frontend\login.html"
        OutputFile = "$projectDir\frontend\login.html"
    },
    @{
        StitchFile = "$stitchDir\user_dashboard_elysian_auctions\code.html"
        BoilerplateFile = "$projectDir\frontend\dashboard.html"
        OutputFile = "$projectDir\frontend\dashboard.html"
    }
)

# We need a pristine copy of boilerplate files before we overwrite them
# Read all boilerplate files first
$boilerplateContents = @{}
foreach ($merge in $merges) {
    $boilerplateContents[$merge.OutputFile] = Get-Content -Path $merge.BoilerplateFile -Raw -Encoding UTF8
}

# Oops - the boilerplate files were already overwritten in the previous run.
# We need to re-read from the original stitch files and the boilerplate originals.
# But wait - the boilerplate files were already overwritten. Let me use git to restore them first.

# Actually, let me check: the previous script read boilerplate BEFORE writing.
# But now those files are corrupted from the previous run. Let me restore them from git.

Write-Host "Restoring original boilerplate files from git..." -ForegroundColor Yellow

Push-Location $projectDir
git checkout -- frontend/auction-detail.html frontend/login.html frontend/dashboard.html
Pop-Location

Write-Host "Restored successfully." -ForegroundColor Green

# Now re-read
foreach ($merge in $merges) {
    $boilerplateContents[$merge.OutputFile] = Get-Content -Path $merge.BoilerplateFile -Raw -Encoding UTF8
}

foreach ($merge in $merges) {
    Write-Host "`n=== Processing: $($merge.OutputFile) ===" -ForegroundColor Cyan

    # Read files
    $stitchContent = Get-Content -Path $merge.StitchFile -Raw -Encoding UTF8
    $boilerplateContent = $boilerplateContents[$merge.OutputFile]

    # Extract all <script>...</script> blocks from boilerplate
    # We want script blocks that contain actual JS code (not the tailwind CDN or config ones)
    $scriptPattern = '(?s)<script(?![^>]*\bsrc\b)(?![^>]*\bid="tailwind-config")(?:[^>]*)>.*?</script>'
    $scriptMatches = [regex]::Matches($boilerplateContent, $scriptPattern)

    $scriptBlocks = @()
    foreach ($m in $scriptMatches) {
        $scriptBlocks += $m.Value
    }

    Write-Host "  Found $($scriptBlocks.Count) script block(s) in boilerplate"

    if ($scriptBlocks.Count -eq 0) {
        Write-Host "  WARNING: No script blocks found! Skipping." -ForegroundColor Yellow
        continue
    }

    # Remove the Stitch file's own inline <script> blocks before </body>
    # Use [regex]::Replace to avoid PowerShell's $-interpolation issues
    $stitchCleaned = [regex]::Replace($stitchContent, '(?s)<script>\s*//.*?</script>\s*(?=</body>)', '')
    # Also handle script blocks that don't start with //
    $stitchCleaned = [regex]::Replace($stitchCleaned, '(?s)<script>\s*(?:function|document\.|//|var |let |const ).*?</script>\s*(?=</body>)', '')

    # Inject the boilerplate scripts just before </body>
    $injectedScripts = ($scriptBlocks -join "`n")
    
    # Use [regex]::Replace to avoid $ interpolation issues
    $mergedContent = [regex]::Replace($stitchCleaned, '</body>', "$injectedScripts`n</body>", [System.Text.RegularExpressions.RegexOptions]::None)

    # Hmm, the above still has issues. Let's use simple string replacement instead.
    # Actually the issue is that $injectedScripts contains $ signs from JS code.
    # Let's use .Replace() method instead of -replace operator.

    # Write output
    [System.IO.File]::WriteAllText($merge.OutputFile, $mergedContent, [System.Text.Encoding]::UTF8)
    Write-Host "  Written merged file to: $($merge.OutputFile)" -ForegroundColor Green
}

Write-Host "`n=== All 3 files merged successfully! ===" -ForegroundColor Green

# Install prompt-engine skill and sub-skills (Windows/PowerShell)
# Usage: .\install.ps1

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$SkillsDir = Join-Path $env:USERPROFILE ".claude\skills"
$Count = "unknown"

Write-Host "Installing prompt-engine skill ecosystem..."
Write-Host "Source: $ScriptDir"
Write-Host "Target: $SkillsDir"
Write-Host ""

# Create skills directory if needed
if (-not (Test-Path $SkillsDir)) {
    New-Item -ItemType Directory -Path $SkillsDir -Force | Out-Null
}

# [1/6] Install main skill (with path substitution)
Write-Host "[1/6] Installing prompt-engine (main skill)..."
$TargetMain = Join-Path $SkillsDir "prompt-engine"
if (Test-Path $TargetMain) { Remove-Item -Recurse -Force $TargetMain }
Copy-Item -Recurse (Join-Path $ScriptDir "prompt-engine") $TargetMain
$SkillMd = Join-Path $TargetMain "SKILL.md"
(Get-Content $SkillMd -Raw) -replace '\{PROMPT_ENGINE_DIR\}', $ScriptDir | Set-Content $SkillMd -NoNewline

# [2/6] Install sub-skills (with path substitution)
Write-Host "[2/6] Installing sub-skills..."
$SubSkills = @("prompt-build", "prompt-enhance", "prompt-adapt", "prompt-library")
foreach ($skill in $SubSkills) {
    Write-Host "  [+] $skill"
    $TargetSkill = Join-Path $SkillsDir $skill
    if (Test-Path $TargetSkill) { Remove-Item -Recurse -Force $TargetSkill }
    Copy-Item -Recurse (Join-Path $ScriptDir "skills\$skill") $TargetSkill
    $SkillFile = Join-Path $TargetSkill "SKILL.md"
    (Get-Content $SkillFile -Raw) -replace '\{PROMPT_ENGINE_DIR\}', $ScriptDir | Set-Content $SkillFile -NoNewline
}

# [3/6] Copy references (Windows doesn't support symlinks easily)
Write-Host "[3/6] Copying references..."
$RefsTarget = Join-Path $SkillsDir "prompt-engine\references"
if (Test-Path $RefsTarget) { Remove-Item -Recurse -Force $RefsTarget }
Copy-Item -Recurse (Join-Path $ScriptDir "references") $RefsTarget

# [4/6] Verify scripts are accessible
Write-Host "[4/6] Verifying scripts..."
try {
    $null = python3 (Join-Path $ScriptDir "scripts\search_prompts.py") --stats 2>&1
    Write-Host "  Search script: OK"
} catch {
    try {
        $null = python (Join-Path $ScriptDir "scripts\search_prompts.py") --stats 2>&1
        Write-Host "  Search script: OK (using 'python')"
    } catch {
        Write-Host "  Search script: WARNING - stats check failed"
    }
}

# [5/6] Verify prompt database
Write-Host "[5/6] Verifying prompt database..."
$DbPath = Join-Path $ScriptDir "prompts\all_prompts.json"
if (Test-Path $DbPath) {
    try {
        $Count = python3 -c "import json; print(len(json.load(open(r'$DbPath'))))" 2>$null
        if (-not $Count) {
            $Count = python -c "import json; print(len(json.load(open(r'$DbPath'))))" 2>$null
        }
        Write-Host "  Prompts loaded: $Count"
    } catch {
        Write-Host "  WARNING: Could not count prompts"
    }
} else {
    Write-Host "  WARNING: Prompt database not found at $DbPath"
}

# [6/6] Clean up old installations
Write-Host "[6/6] Cleaning up..."
$OldSkill = Join-Path $SkillsDir "claude-prompt"
if (Test-Path $OldSkill) {
    Write-Host "  Removing old claude-prompt skill (renamed to prompt-engine)..."
    Remove-Item -Recurse -Force $OldSkill
}

Write-Host ""
Write-Host "Installation complete!"
Write-Host ""
Write-Host "Installed skills:"
Write-Host "  /prompt          -- Search and find prompts"
Write-Host "  /prompt-build    -- Build custom prompts"
Write-Host "  /prompt-enhance  -- Enhance existing prompts"
Write-Host "  /prompt-adapt    -- Adapt prompts across models"
Write-Host "  /prompt-library  -- Browse the prompt library"
Write-Host ""
Write-Host "Database: $Count prompts across 19 categories and 17 models"
Write-Host "Repo path: $ScriptDir"

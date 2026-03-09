#!/usr/bin/env pwsh
# claude-prompts uninstaller for Windows

$ErrorActionPreference = "Stop"

function Main {
    $SkillDir = Join-Path $env:USERPROFILE ".claude" "skills"

    Write-Host "=== Uninstalling claude-prompts ===" -ForegroundColor Cyan
    Write-Host ""

    # Remove main skill
    $mainDir = Join-Path $SkillDir "prompt-engine"
    if (Test-Path $mainDir) {
        Remove-Item -Recurse -Force $mainDir
        Write-Host "  Removed: $mainDir" -ForegroundColor Green
    }

    # Remove sub-skills
    $subSkills = @("prompt-adapt", "prompt-build", "prompt-enhance", "prompt-library")
    foreach ($skill in $subSkills) {
        $skillPath = Join-Path $SkillDir $skill
        if (Test-Path $skillPath) {
            Remove-Item -Recurse -Force $skillPath
            Write-Host "  Removed: $skillPath" -ForegroundColor Green
        }
    }

    Write-Host ""
    Write-Host "=== claude-prompts uninstalled ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Restart Claude Code to complete removal." -ForegroundColor Yellow
}

Main

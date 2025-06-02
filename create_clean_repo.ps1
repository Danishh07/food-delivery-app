# This script creates a clean version of the repository with only essential files for deployment

# Create a new branch for the clean version
git checkout -b clean-deploy

# Remove non-essential files (they'll still be in your main branch)
Remove-Item -Path test_services.py, test_order_status.py, test_api.py, simple_test.py, setup.sh, setup.ps1, setup_local.ps1, hello.py, direct_debug.py, DEPLOYMENT.md, debug_order_status.py, debug_test.py, debug_output*.txt, check_modules.py, complete_test.py, git_setup.ps1, quick_test.py -Force -ErrorAction SilentlyContinue

# Keep README_DEPLOYMENT.md but rename it to README.md for clarity
if (Test-Path -Path README_DEPLOYMENT.md) {
    if (Test-Path -Path README.md) {
        Remove-Item -Path README.md -Force
    }
    Rename-Item -Path README_DEPLOYMENT.md -NewName README.md
}

# Add the essential files
git add .

# Commit the clean version
git commit -m "Clean repository with only essential files for deployment"

# Push to GitHub (optional)
# git push -u origin clean-deploy

Write-Host "Clean version created in 'clean-deploy' branch."
Write-Host "To push to GitHub, run: git push -u origin clean-deploy"

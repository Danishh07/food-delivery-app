# Script to initialize Git repository and push to GitHub
# To run:
# 1. Replace YOUR_GITHUB_USERNAME with your actual GitHub username
# 2. Create a new empty repository on GitHub named "food-delivery-app"
# 3. Run: .\git_setup.ps1

# Initialize Git repository
git init

# Add all files
git add .

# Set remote repository URL
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/food-delivery-app.git

# Make initial commit
git commit -m "Initial commit of Food Delivery App"

# Push to GitHub
echo "To push to GitHub, run:"
echo "git push -u origin master"
echo ""
echo "Remember to replace YOUR_GITHUB_USERNAME in this script with your actual GitHub username before pushing."

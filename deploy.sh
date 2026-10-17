#!/bin/bash

echo "🚀 Starting deployment process..."

# Build frontend assets if package.json exists
if [ -f package.json ]; then
    echo "📦 Building frontend assets..."
    npm run build
fi

# Stage all files
echo "➕ Staging changes..."
git add .

# Check if there are actually any changes to commit
if git diff-index --quiet HEAD --; then
    echo "✅ No new changes to push! Everything is already on the server."
    exit 0
fi

# Commit the changes
echo "📝 Committing changes..."
git commit -m "Auto deployment update: $(date '+%Y-%m-%d %H:%M:%S')"

# Push to GitHub (which triggers your deploy.yml)
echo "☁️  Pushing to server..."
git push

echo "🎉 Done! Your changes have been sent to the server directly."

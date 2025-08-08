#!/bin/bash

echo "🚀 Deploying BuiltByRays™ CFO OS to Cloudflare Pages..."

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

# Build the application
echo "🔨 Building application..."
npm run build

# Deploy to Cloudflare Pages
echo "☁️ Deploying to Cloudflare Pages..."
npx wrangler pages deploy dist --project-name=builtbyrays-cfo-os

echo "✅ Deployment complete!"
echo "🌐 Your CFO OS is now live on Cloudflare Pages"
echo "📱 Access your application at the URL provided above" 
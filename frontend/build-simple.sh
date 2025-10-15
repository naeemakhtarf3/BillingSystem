#!/bin/bash
set -e

echo "Installing dependencies..."
npm install

echo "Building with simple config..."
npx vite build --config vite.config.simple.js

echo "Build completed successfully!"

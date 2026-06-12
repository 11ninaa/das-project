#!/bin/sh
# Docker entrypoint script to inject environment variables into built React app

set -e

# Get API URL from environment (default to /api for Nginx proxy)
API_URL=${VITE_API_BASE_URL:-/api}

# Replace the API URL in the built JavaScript files
# Vite injects environment variables at build time as string literals
# We need to replace these at runtime
if [ -n "$API_URL" ]; then
    echo "Injecting API URL: $API_URL into built files..."
    
    # Replace various URL patterns in JS files (Vite injects as string literals)
    find /usr/share/nginx/html -type f -name "*.js" -exec sed -i "s|http://localhost:8080|${API_URL}|g" {} \; 2>/dev/null || true
    find /usr/share/nginx/html -type f -name "*.js" -exec sed -i "s|\"http://localhost:8080\"|\"${API_URL}\"|g" {} \; 2>/dev/null || true
    find /usr/share/nginx/html -type f -name "*.js" -exec sed -i "s|'http://localhost:8080'|'${API_URL}'|g" {} \; 2>/dev/null || true
    
    echo "API URL injection complete."
fi

# Execute the main command
exec "$@"


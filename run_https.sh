#!/bin/bash

# Run Django with HTTPS support for mobile testing
# This script enables camera access on mobile devices by using HTTPS

cd /Users/macduong/Documents/1/VB2/CNTT14/TT/demo

echo "🚀 Starting Django server with HTTPS support..."
echo "Your IP: 192.168.1.100"
echo "Access from mobile: https://192.168.1.100:8000"
echo ""
echo "⚠️  You'll see a security warning on mobile - this is normal"
echo "Click 'Advanced' → 'Continue' to proceed"
echo ""

# Try runserver_plus first (needs pyopenssl)
python manage.py runserver_plus --cert-file cert.pem 0.0.0.0:8000

# If that fails, fall back to regular runserver with warning
echo "⚠️  If HTTPS didn't work, using HTTP instead..."
echo "Access: http://192.168.1.100:8000"
echo "Note: Camera won't work on HTTP, but all other features will"
python manage.py runserver 0.0.0.0:8000

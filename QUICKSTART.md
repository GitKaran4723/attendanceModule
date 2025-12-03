# Quick Start Guide - BCA BUB PWA

## Installation & Running (3 Easy Steps)

### Option 1: Automatic Setup (Recommended for Windows)
```bash
# Double-click start.bat or run in terminal:
start.bat
```

### Option 2: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate icons (optional)
pip install Pillow
python generate_icons.py

# 3. Run the app
python app.py
```

### Option 3: Just Run It
```bash
pip install Flask Flask-SQLAlchemy
python app.py
```

## Access the App

1. **On your computer:**
   - Open browser: http://localhost:5000

2. **On your mobile device:**
   - Find your computer's IP address:
     - Windows: Run `ipconfig` in terminal
     - Look for "IPv4 Address" (e.g., 192.168.1.100)
   - Open mobile browser: http://YOUR_IP:5000
   - Example: http://192.168.1.100:5000

## Install as PWA on Mobile

### Android (Chrome):
1. Open the app in Chrome
2. Tap the "..." menu
3. Tap "Install app" or "Add to Home Screen"
4. Done! The app is now on your home screen

### iPhone (Safari):
1. Open the app in Safari
2. Tap the Share button (square with arrow)
3. Scroll and tap "Add to Home Screen"
4. Tap "Add"

## First Steps in the App

1. **Add Users:**
   - Click the "+" button or go to Users page
   - Add name and email
   - Save

2. **Check In:**
   - From home screen, tap "Check In" action
   - Select user
   - Add optional notes
   - Confirm

3. **View Records:**
   - Go to "Records" tab
   - See all check-ins/check-outs
   - Tap logout icon to check out

## Features You'll Love

- ✅ Works offline (after first visit)
- ✅ Installs like a real app
- ✅ Fast and responsive
- ✅ Looks like native Android
- ✅ Saves all data locally
- ✅ No internet required (after setup)

## Troubleshooting

**Can't access from mobile?**
- Make sure both devices are on the same WiFi
- Check your firewall settings
- Try disabling Windows Firewall temporarily

**Icons not showing?**
- Run: `pip install Pillow`
- Run: `python generate_icons.py`

**Database errors?**
- Delete the `instance` folder
- Restart the app

## Next Steps

- Customize colors in `static/css/style.css`
- Add your own icons in `static/icons/`
- Deploy to production server for remote access
- Add authentication for security

Enjoy your new PWA! 🚀

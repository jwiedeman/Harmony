# 🚀 HARMONY QA SYSTEM - QUICK START GUIDE

## One-Click Launch (Recommended for Non-Technical Users)

### 🍎 macOS
1. Open Terminal
2. Navigate to the Harmony folder
3. Run: `./launch-mac.sh`

### 🐧 Linux
1. Open Terminal  
2. Navigate to the Harmony folder
3. Run: `./launch-linux.sh`

### 🪟 Windows
1. Right-click `launch-windows.bat`
2. Select "Run as Administrator"

**That's it!** The application will automatically:
- ✅ Install all dependencies
- ✅ Set up the environment  
- ✅ Launch backend and frontend
- ✅ Open your browser to http://localhost:3000

---

## 🔍 Before You Start (Optional System Check)

Verify your system is ready:
```bash
python3 system-check.py
```

This checks for:
- Python 3.8+ with pip
- Node.js 16+ with npm  
- Yarn package manager
- Git (recommended)
- Available ports

---

## 🆘 Troubleshooting

### Scripts Won't Run
**macOS/Linux:**
```bash
chmod +x launch-mac.sh
chmod +x launch-linux.sh
```

**Windows:**
- Right-click → "Run as Administrator"
- Or open Command Prompt as Admin and run: `launch-windows.bat`

### Ports Already in Use
```bash
# macOS/Linux - Kill processes on ports 3000 and 8001:
sudo lsof -ti:3000 | xargs kill -9
sudo lsof -ti:8001 | xargs kill -9

# Windows - Find and kill processes:
netstat -ano | findstr :3000
taskkill /PID [PID_NUMBER] /F
```

### Missing Dependencies
The launch scripts will automatically install:
- **macOS**: Uses Homebrew
- **Linux**: Uses apt/yum/dnf
- **Windows**: Uses Chocolatey

If automatic installation fails, manually install:
1. **Python 3.8+** from https://python.org
2. **Node.js 16+** from https://nodejs.org  
3. **Git** from https://git-scm.com

---

## ✅ Success Indicators

When everything is working correctly, you'll see:

```
🌐 Web Interface: http://localhost:3000
🔧 API Endpoint:  http://localhost:8001
📖 Documentation: Open USER_GUIDE.md for usage instructions
```

Your browser should automatically open to the Harmony QA System interface.

---

## 📖 Next Steps

1. **Create Test Cases** - Define your QA rules
2. **Upload HAR Files** - Drag & drop for analysis
3. **View Results** - Comprehensive dashboard
4. **Export Reports** - Download Excel reports

**Need help?** Open `USER_GUIDE.md` for detailed instructions.

---

**🎉 Welcome to Harmony QA System!**
*Professional QA testing made simple.*
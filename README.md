# 🚀 Harmony QA System

**The Ultimate Web-Based QA Testing Tool for HTTP Archive Analysis**

Transform your quality assurance workflow with Harmony's intuitive web interface. No more command-line complexity - just powerful, visual QA testing that anyone can use.

---

## 🎯 What is Harmony QA System?

Harmony QA System is a comprehensive web-based tool that analyzes HTTP Archive (HAR) files to identify API parameter issues, validate data integrity, and generate detailed QA reports. Perfect for QA teams, developers, and anyone who needs to ensure their web applications are working correctly.

### ✨ Key Features

- 🎨 **Clean 1970s NASA Terminal Design** - Minimalist, functional interface
- 📝 **Visual Test Case Builder** - Create QA rules without editing files
- 📁 **Drag & Drop HAR Upload** - Easy file analysis interface
- 📊 **Comprehensive Dashboards** - Detailed results with filtering
- 📋 **Excel Report Export** - Professional reports for stakeholders
- 🔍 **Advanced Filtering** - Search and sort results by URL/parameter
- 🌐 **Cross-Platform** - Runs on Windows, macOS, and Linux

---

## 🚀 Quick Start (Choose Your Platform)

### 🍎 macOS Users
```bash
chmod +x launch-mac.sh
./launch-mac.sh
```

### 🐧 Linux Users
```bash
chmod +x launch-linux.sh
./launch-linux.sh
```

### 🪟 Windows Users
```batch
Right-click "launch-windows.bat" → "Run as Administrator"
```

**That's it!** The system will automatically:
- Install all dependencies
- Set up the environment
- Launch both backend and frontend
- Open your browser to the application

---
## Standalone Web Version

Place `test_cases.xlsx` and your HAR files in the `standalone` folder. Open `standalone/index.html` in a modern browser to run all analysis locally without a backend.


## 📋 System Requirements Check

Before running, you can verify your system has everything needed:

```bash
python3 system-check.py
```

This will check for:
- ✅ Python 3.8+ with pip and venv
- ✅ Node.js 16+ with npm
- ✅ Yarn package manager
- ✅ Git (recommended)
- ✅ Available ports (3000, 8001)
- ✅ Project file structure

---

## 📖 User Guide

### 🔧 Creating Test Cases

1. **Navigate to TEST CASES tab**
2. **Click "NEW TEST CASE"**
3. **Fill in the test details:**
   - **Name**: Descriptive identifier (e.g., "App Build Check")
   - **Description**: What the test validates
   - **Target URLs**: Specific domains (or leave empty for all)
   - **Parameter Name**: The parameter to check (e.g., "app_build")
   - **Condition**: `EXISTS` or `EQUALS`
   - **Expected Value**: Required for `EQUALS` condition
   - **Optional**: Check if parameter is not required
   - **Messages**: Custom success/failure messages with placeholders

### 📁 Analyzing HAR Files

1. **Navigate to HAR ANALYZER tab**
2. **Drag and drop your HAR file** (or click to select)
3. **Click "START ANALYSIS"**
4. **Results automatically appear** in the Results Dashboard

### 📊 Viewing Results

The Results Dashboard provides three views:

- **📈 SUMMARY**: Overview metrics and failure counts
- **📋 DETAILED RESULTS**: Filterable table of all test results
- **🔍 RAW DATA**: Complete request/response inspection

### 📥 Exporting Reports

Click **"EXPORT REPORT"** to download comprehensive Excel files containing:
- Individual test results
- Summary metrics
- URL failure analysis
- Parameter failure breakdown

---

## 🗂 How to Get HAR Files

### Chrome Browser
1. Open Developer Tools (`F12`)
2. Go to **Network** tab
3. Perform actions on your website
4. Right-click → **Save all as HAR with content**

### Firefox Browser
1. Open Developer Tools (`F12`)
2. Go to **Network** tab
3. Perform actions on your website
4. Click gear icon → **Save All As HAR**

### Safari Browser
1. Enable Develop menu in preferences
2. Open Web Inspector
3. Go to **Network** tab
4. Export as HAR file

---

## ⚙️ Manual Installation (Advanced Users)

If you prefer manual setup or the automatic scripts don't work:

### Prerequisites
- **Python 3.8+** with pip and venv
- **Node.js 16+** with npm
- **Yarn** package manager

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

### Frontend Setup
```bash
cd frontend
yarn install
yarn start
```

### Access Application
- **Web Interface**: http://localhost:3000
- **API Endpoint**: http://localhost:8001

---

## 🛠 Troubleshooting

### Common Issues

**🔴 Port Already in Use**
```bash
# Kill processes on ports 3000 and 8001
# macOS/Linux:
sudo lsof -ti:3000 | xargs kill -9
sudo lsof -ti:8001 | xargs kill -9

# Windows:
netstat -ano | findstr :3000
taskkill /PID [PID] /F
```

**🔴 Permission Denied on Scripts**
```bash
# Make scripts executable on macOS/Linux:
chmod +x launch-mac.sh
chmod +x launch-linux.sh
```

**🔴 Python/Node.js Not Found**
- Ensure you're using the correct Python command (`python3` vs `python`)
- Restart terminal after installing new packages
- Check PATH environment variables

**🔴 Dependencies Installation Fails**
- Run scripts as Administrator on Windows
- Use `sudo` for system package installation on macOS/Linux
- Check internet connectivity

### Getting Help

1. **Run System Check**: `python3 system-check.py`
2. **Check Service Status**: Look for error messages in the terminal
3. **Verify Ports**: Ensure ports 3000 and 8001 are available
4. **Browser Issues**: Try different browser or clear cache

---

## 🔧 Technical Architecture

### Backend (FastAPI)
- **API Endpoints**: RESTful API for all operations
- **HAR Processing**: Advanced parsing engine
- **Report Generation**: Excel export functionality
- **Data Storage**: In-memory with MongoDB support

### Frontend (React)
- **Modern UI**: Clean, responsive design
- **Component-Based**: Modular React architecture
- **Real-time Updates**: Live data synchronization
- **File Handling**: Drag-drop upload interface

### Security & Performance
- **CORS Enabled**: Secure cross-origin requests
- **Error Handling**: Comprehensive error management
- **Performance**: Optimized for large HAR files
- **Scalability**: Ready for production deployment

---

## 📝 Example Test Cases

### Basic Parameter Existence
```
Name: User ID Check
Description: Verify user_id parameter exists
Parameter: user_id
Condition: EXISTS
Target URLs: api.mysite.com
```

### Specific Value Validation
```
Name: API Version Check
Description: Ensure API version is v2.0
Parameter: version
Condition: EQUALS
Expected Value: v2.0
Target URLs: api.mysite.com
```

### Optional Parameter
```
Name: Debug Mode Check
Description: Check for optional debug flag
Parameter: debug
Condition: EXISTS
Optional: YES
Target URLs: debug.mysite.com
```

---

## 🎨 Design Philosophy

Harmony QA System embraces a **1970s NASA computer terminal aesthetic**:

- ✅ **Clean White Backgrounds** - Easy on the eyes
- ✅ **Pure Black Text** - Maximum readability  
- ✅ **Monospace Fonts** - Professional terminal feel
- ✅ **Minimal Design** - Focus on functionality
- ✅ **Clear Navigation** - Intuitive user experience

---

## 📊 System Status

After launching, verify your system at these endpoints:

- **🌐 Main Application**: http://localhost:3000
- **🔧 API Health Check**: http://localhost:8001/api/health
- **📋 Test Page**: http://localhost:3000/test.html

---

## 🚀 What's Next?

Harmony QA System is ready for production use! Some advanced features you might want to explore:

- **Database Integration**: Connect MongoDB for persistent storage
- **Team Collaboration**: Share test cases across team members
- **CI/CD Integration**: Automate HAR analysis in pipelines
- **Custom Reporting**: Create branded reports for stakeholders
- **Advanced Analytics**: Track QA trends over time

---

## 📞 Support

For technical support:

1. **Check Documentation**: Read the complete USER_GUIDE.md
2. **System Requirements**: Run `python3 system-check.py`
3. **Platform Scripts**: Use appropriate launch script for your OS
4. **Manual Setup**: Follow advanced installation instructions

---

**🎉 Happy Testing with Harmony QA System!**

*Transform your QA workflow from command-line complexity to visual simplicity.*
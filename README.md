# 7 Days to Die Server Configuration Editor™

<div align="center">

![Version](https://img.shields.io/badge/version-1.2.6-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-NDT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

**A comprehensive, professional GUI application for editing 7 Days to Die server configurations with ease and precision.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Building](#-building) • [Screenshots](#-screenshots) • [Support](#-support)

</div>

---

## 📖 Overview

The **7 Days to Die Server Configuration Editor** is a powerful, user-friendly desktop application designed to simplify the process of managing and editing your 7 Days to Die dedicated server's `serverconfig.xml` file. Built with Python and Tkinter, this editor transforms the complex task of manual XML editing into an intuitive, organized experience with real-time validation, intelligent search, and comprehensive tooltips.

### Why Use This Editor?

Managing a 7 Days to Die server requires careful configuration of over 90+ different properties across multiple categories. Manually editing XML files is:
- **Error-prone**: One typo can break your server
- **Time-consuming**: Finding the right property among dozens is tedious
- **Confusing**: Remembering what each property does is challenging
- **Risky**: No backup means lost configurations

This editor solves all these problems with a clean, organized interface that makes server configuration **fast, safe, and intuitive**.

---

## ✨ Features

### 🎯 Organized Property Management
- **10 Categorized Tabs**: Properties intelligently grouped into logical categories
  - 🔧 **General**: Server identity, ports, admin settings, network configuration
  - 🌍 **World**: World generation, map settings, save management
  - ⚔️ **Difficulty**: Game difficulty, damage multipliers, XP settings
  - 📜 **Rules**: Game rules, day/night cycles, biome progression
  - ⚡ **Performance**: Server performance, view distance, spawn limits
  - 🧟 **Zombies**: Zombie behavior, blood moons, feral settings
  - 💰 **Loot**: Loot abundance, respawn rates, airdrops
  - 👥 **Multiplayer**: Party settings, PvP modes
  - 🏠 **Claims**: Land claim settings, protection zones
  - 🎮 **Other**: Twitch integration, quest settings

### 🔍 Advanced Search & Navigation
- **Global Cross-Tab Search**: Search across all 91 properties simultaneously
- **Smart Filtering**: Matches both property names and descriptions
- **Result Navigation**: Previous/Next buttons with result counter (X of Y)
- **Visual Highlighting**: Pale yellow background highlights current search result
- **Auto-Scrolling**: Automatically scrolls to and centers highlighted results
- **Tab Switching**: Automatically switches to the correct tab for each result

### 💡 Intelligent Help System
- **Contextual Tooltips**: Hover over the ? icon for detailed property descriptions
- **Official Documentation**: Tooltips extracted directly from serverconfig.xml comments
- **Value Ranges**: See acceptable values, ranges, and detailed explanations
- **Real-Time Help**: Get information exactly when you need it

### 🎨 Professional User Interface
- **Modern Design**: Clean, professional blue header with branded logos
- **2-Column Layout**: Efficient use of screen space with side-by-side properties
- **Responsive UI**: Smooth scrolling, intuitive controls, keyboard shortcuts
- **Visual Feedback**: Clear indication of unsaved changes
- **Status Bar**: Real-time feedback on configuration file status

### 🛡️ Safety & Reliability
- **Automatic Backups**: Creates timestamped backups before every save
- **XML Validation**: Validates XML structure before saving
- **Encoding Repair**: Automatically fixes common XML encoding issues
- **Read-Only Mode**: Loads configurations safely without modifying originals
- **Error Handling**: Graceful error handling with user-friendly messages

### ⚙️ Configuration Management
- **Persistent Settings**: Remembers your server config file location
- **Browse & Select**: Easy file browser for locating configuration files
- **Auto-Load**: Automatically loads your saved configuration on startup
- **Multiple Configs**: Switch between different server configurations easily

### ⌨️ Productivity Features
- **Keyboard Shortcuts**: 
  - `Ctrl+S`: Quick save
  - `Ctrl+R`: Reload configuration
- **Quick Search**: Instantly filter properties as you type
- **Copy Debug Info**: One-click debug information copying for troubleshooting
- **Change Log**: Built-in version history and feature documentation

### 📦 Standalone Executable
- **No Python Required**: Runs as a standalone Windows executable
- **All-In-One**: All resources bundled in a single 22MB file
- **Portable**: Run from anywhere, no installation needed
- **Professional Icons**: Custom taskbar and window icons

---

## 🚀 Installation

### Option 1: Download Executable (Recommended)
1. Download the latest `7D2D-ServerConfigEditor.exe` from the [Releases](../../releases) page
2. Place it anywhere on your computer
3. Double-click to run - no installation required!

### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/cfranz73/7D2D-ServerConfigEditor.git
cd 7D2D-ServerConfigEditor

# Install dependencies
pip install pillow

# Run the application
python 7d2d_server_config_editor.py
```

### Requirements
- **For Executable**: Windows 10 or later
- **For Source**: Python 3.8+, Pillow library

---

## 💻 Usage

### First Launch
1. **Launch the Application**: Run `7D2D-ServerConfigEditor.exe` or `python 7d2d_server_config_editor.py`
2. **Configure File Location**: 
   - Go to **File** → **Settings**
   - Click **Browse** and navigate to your server's `serverconfig.xml`
   - Default location: `C:\Program Files (x86)\Steam\steamapps\common\7 Days to Die Dedicated Server\serverconfig.xml`
   - Click **Save**

### Editing Configuration
1. **Browse Properties**: Click through the tabs to explore different property categories
2. **Edit Values**: Click on any property value field and type your desired value
3. **Get Help**: Hover over the ? icon next to property names for detailed information
4. **Search**: Use the search bar to quickly find specific properties
5. **Navigate Results**: Use Previous/Next buttons to jump between search results
6. **Save Changes**: Click **Save Configuration** or press `Ctrl+S`

### Search Tips
- Search by property name: `ServerName`, `BloodMoon`, `Loot`
- Search by description keywords: `password`, `zombie speed`, `difficulty`
- Use the counter to see how many matches were found
- Navigate with Previous (◀ Prev) and Next (▶ Next) buttons

### Safety Tips
- The application creates automatic backups with timestamps before saving
- Your original file remains safe until you click Save
- Use **File** → **Reload Configuration** (`Ctrl+R`) to discard changes
- Backups are stored next to your original file with `.backup_YYYYMMDD_HHMMSS` extension

---

## 🔨 Building

### Building Your Own Executable

#### Using Build Scripts
```bash
# Windows
build_exe.bat

# Linux/Mac
chmod +x build_exe.sh
./build_exe.sh
```

#### Manual Build
```bash
python -m PyInstaller --onefile --windowed \
    --name "7D2D-ServerConfigEditor" \
    --icon="icon.ico" \
    --add-data "icon.ico;." \
    --add-data "Logos and Images;Logos and Images" \
    7d2d_server_config_editor.py
```

The executable will be created in the `dist/` folder.

For detailed build instructions, see [BUILD.md](BUILD.md).

---

## 📸 Screenshots

### Main Interface
Clean, organized interface with categorized tabs and professional design.

### Search & Navigation
Powerful cross-tab search with visual highlighting and result navigation.

### Tooltip System
Contextual help with official documentation right at your fingertips.

---

## 🐛 Troubleshooting

### Taskbar Icon Not Showing
Run the included `clear_icon_cache.bat` to refresh Windows icon cache.

### Configuration File Not Found
1. Go to **File** → **Settings**
2. Use the **Browse** button to locate your `serverconfig.xml`
3. Default location: `C:\Program Files (x86)\Steam\steamapps\common\7 Days to Die Dedicated Server\`

### Changes Not Saving
- Ensure you have write permissions to the server config directory
- Try running the application as Administrator
- Check that the server is not currently using the file

### Application Won't Start
- Ensure you have the latest version
- Check Windows Security hasn't blocked the executable
- Try running from source with Python

---

## 📋 Property Categories

The editor organizes **91 server properties** into 10 intuitive categories:

| Category | Properties | Description |
|----------|------------|-------------|
| 🔧 **General** | 28 | Server identity, network settings, admin controls, web dashboard |
| 🌍 **World** | 8 | World generation, map size, game modes, save management |
| ⚔️ **Difficulty** | 7 | Game difficulty, damage settings, XP multipliers, safe zones |
| 📜 **Rules** | 9 | Game rules, day/night cycles, death penalties, spawn settings |
| ⚡ **Performance** | 4 | Performance tuning, view distance, spawn limits, mesh settings |
| 🧟 **Zombies** | 12 | Zombie AI, movement speeds, blood moon configuration, feral settings |
| 💰 **Loot** | 4 | Loot abundance, respawn rates, airdrop frequency |
| 👥 **Multiplayer** | 2 | Party settings, player killing modes |
| 🏠 **Claims** | 12 | Land claim system, protection zones, durability modifiers |
| 🎮 **Other** | 3 | Twitch integration, quest progression limits |

---

## 🤝 Support

### Bug Reports
Found a bug? Use the built-in bug report feature:
1. Click the **Report Bug** button in the application
2. Fill out the automatic bug report form
3. Submit via email with auto-attached system information

### Feature Requests
Have an idea? Open an issue on GitHub with the "enhancement" label.

### Documentation
- [BUILD.md](BUILD.md) - Comprehensive build instructions
- [Change Log](../../releases) - Version history and changes
- Built-in Help → Change Log for detailed version history

---

## 📜 Version History

### v1.2.6 (Current)
- PyInstaller executable build support with resource bundling
- Fixed Windows taskbar icon display
- Added automated build scripts and documentation
- Window title updated with trademark symbol

### v1.2.5
- Settings dialog for persistent configuration
- Updated property descriptions with official documentation
- Professional tooltip icon system

### v1.1.0
- Global cross-tab search with navigation
- Result highlighting and auto-scrolling
- Search result counter

### v1.0.0
- Initial release with 10 organized tabs
- 91 properties with descriptions
- XML comment extraction for tooltips

For complete version history, see the built-in Change Log (Help → Change Log).

---

## 📄 License

This project is licensed under the NDT License.

---

## 👨‍💻 Development

**Author**: Niggot Development Team  
**Version**: 1.2.6  
**Python**: 3.8+  
**Framework**: Tkinter  
**Image Processing**: Pillow (PIL)

---

## 🌟 Acknowledgments

- Built for the 7 Days to Die community
- Powered by Python and Tkinter
- Logo by Mayhem Mods

---

<div align="center">

**Made with ❤️ for server administrators**

[Report Bug](../../issues) • [Request Feature](../../issues) • [View Releases](../../releases)

</div>

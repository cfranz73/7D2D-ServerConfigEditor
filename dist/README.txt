7 Days to Die Server Config Editor
=================================

Overview
--------
A Tkinter-based desktop app to view and edit 7 Days to Die dedicated server configuration files (serverconfig.xml). It organizes 90+ properties into tabs, surfaces official descriptions via tooltips, and provides search, save, reload, and safety helpers like backups and XML repair.

Key Features
------------
- Organized tabs (General, World, Difficulty, Rules, Performance, etc.) with two-column layout.
- Tooltip help icons showing official property descriptions pulled from XML comments or built-in mappings.
- Global search across property names and descriptions with Prev/Next navigation and highlighting.
- Settings dialog to persist your preferred serverconfig.xml path across runs.
- Safe editing: creates a backup before saving and can repair common XML encoding issues.
- Header bar with cached logo downloads (Imgur) and versioned footer.
- Keyboard shortcuts: Ctrl+S (save), Ctrl+R (reload).
- Bug/debug copy button to grab environment details to the clipboard.

How It Works
------------
- Loads serverconfig.xml into memory (read-only until you click Save).
- Extracts XML comments for tooltips; falls back to bundled PROPERTY_DESCRIPTIONS.
- Tracks changes and warns on unsaved edits; marks dirty on keypress in fields.
- Saves updates back to XML, creating serverconfig.xml.backup first.

Running the App (source)
------------------------
- Requirements: Python 3.8+ (currently tested on 3.14), Tkinter (bundled with Windows Python), Pillow.
- From the project folder:
  C:/Users/Gramps/AppData/Local/Python/pythoncore-3.14-64/python.exe 7d2d_server_config_editor.py

Settings Persistence
--------------------
- Stored at: %USERPROFILE%/.7d2d_config_editor_settings.json
- Field: Server Config Location (path to serverconfig.xml). Loaded automatically on start.

Search Usage
------------
- Type in the search bar to filter all tabs.
- Prev/Next buttons cycle results; count shown as X of Y.
- Clear resets search and restores the placeholder text.

Tooltips
--------
- Hover the question-mark icon image next to any property to view its description.

Save and Reload
---------------
- Save writes changes and creates a .backup file alongside the config.
- Reload re-reads from disk and repopulates the UI.

Building an EXE (PyInstaller)
-----------------------------
- PyInstaller 6.17.0 is installed for the current interpreter.
- From the project folder:
  "C:/Users/Gramps/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m PyInstaller "7d2d_server_config_editor.py" --onefile --windowed --noconfirm
- Drop --windowed if you want a console window for debugging.

Notes
-----
- Logos are cached to the user profile to avoid repeated downloads.
- If an XML parse error is detected, the app attempts an encoding repair before failing.
- Keep the tooltip-icon.png in Logos and Images/ for the help icons.

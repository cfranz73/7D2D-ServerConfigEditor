#!/usr/bin/env python3
"""
7 Days to Die Server Config Editor

Creates a modern Tkinter GUI to edit serverconfig.xml properties.
Place this script in the same folder as serverconfig.xml and run.
"""
import os
import sys
import platform
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont
from datetime import datetime


# Short descriptions for tooltips
DESCRIPTIONS = {
    "ServerName": "Name of the server",
    "ServerDescription": "Short server description",
    "ServerWebsiteURL": "Website URL for the server",
    "ServerPassword": "Password for private servers",
    "ServerLoginConfirmationText": "Login confirmation message shown to players",
    "Region": "Server region (e.g., US, EU)",
    "Language": "Server language code",
    "ServerPort": "Port the server listens on",
    "ServerVisibility": "Public or private server visibility",
    "ServerDisabledNetworkProtocols": "Disabled network protocols list",
    "ServerMaxWorldTransferSpeedKiBs": "Max world transfer speed (KiB/s)",
    "ServerMaxPlayerCount": "Maximum number of players",
    "ServerReservedSlots": "Number of reserved slots",
    "ServerReservedSlotsPermission": "Permission for reserved slots",
    "ServerAdminSlots": "Admin-only slots",
    "ServerAdminSlotsPermission": "Permission for admin slots",
    "WebDashboardEnabled": "Enable web dashboard",
    "WebDashboardPort": "Web dashboard port",
    "WebDashboardUrl": "Web dashboard URL",
    "EnableMapRendering": "Enable map rendering for dashboard",
    "TelnetEnabled": "Enable telnet interface",
    "TelnetPort": "Telnet port",
    "TelnetPassword": "Telnet password",
    "TelnetFailedLoginLimit": "Failed telnet login limit",
    "TelnetFailedLoginsBlocktime": "Block time after failed logins (s)",
    "TerminalWindowEnabled": "Enable terminal window",
    "AdminFileName": "Admin file name",
    "ServerAllowCrossplay": "Allow crossplay clients",
    "EACEnabled": "Easy Anti-Cheat enabled",
    "IgnoreEOSSanctions": "Ignore EOS sanctions",
    "HideCommandExecutionLog": "Hide command execution logs",
    "MaxUncoveredMapChunksPerPlayer": "Max uncovered map chunks per player",
    "PersistentPlayerProfiles": "Use persistent player profiles",
    "MaxChunkAge": "Max age for world chunks",
    "SaveDataLimit": "Save data limit",
    "GameWorld": "World name",
    "WorldGenSeed": "World generation seed",
    "WorldGenSize": "World size",
    "GameName": "Game name shown",
    "GameMode": "Game mode",
    "GameDifficulty": "Game difficulty level",
    "BlockDamagePlayer": "Block damage caused by players",
    "BlockDamageAI": "Block damage caused by AI",
    "BlockDamageAIBM": "Block Damage AI BMM",
    "XPMultiplier": "XP multiplier",
    "PlayerSafeZoneLevel": "Player safe zone level",
    "PlayerSafeZoneHours": "Hours for player safe zone",
    "BuildCreate": "Allow build/create actions",
    "DayNightLength": "Length of full day-night cycle",
    "DayLightLength": "Length of daylight portion",
    "BiomeProgression": "Biome progression setting",
    "StormFreq": "Storm frequency",
    "DeathPenalty": "Death penalty setting",
    "DropOnDeath": "Drop items on death",
    "DropOnQuit": "Drop items on quit",
    "BedrollDeadZoneSize": "Bedroll dead zone size",
    "BedrollExpiryTime": "Bedroll expiry time",
    "AllowSpawnNearFriend": "Allow spawning near friends",
    "CameraRestrictionMode": "Camera restriction mode",
    "JarRefund": "Jar refund setting",
    "MaxSpawnedZombies": "Maximum spawned zombies",
    "MaxSpawnedAnimals": "Maximum spawned animals",
    "ServerMaxAllowedViewDistance": "Maximum view distance",
    "MaxQueuedMeshLayers": "Max queued mesh layers",
    "EnemySpawnMode": "Enemy spawn mode",
    "EnemyDifficulty": "Enemy difficulty",
    "ZombieFeralSense": "Zombie feral sense",
    "ZombieMove": "Zombie movement speed",
    "ZombieMoveNight": "Zombie night movement speed",
    "ZombieFeralMove": "Feral zombie movement speed",
    "ZombieBMMove": "BM zombie movement setting",
    "AISmellMode": "AI smell mode",
    "BloodMoonFrequency": "Blood moon frequency",
    "BloodMoonRange": "Blood moon range",
    "BloodMoonWarning": "Blood moon warning time",
    "BloodMoonEnemyCount": "Enemies during blood moon",
    "LootAbundance": "Loot abundance multiplier",
    "LootRespawnDays": "Days until loot respawn",
    "AirDropFrequency": "Air drop frequency",
    "AirDropMarker": "Air drop marker setting",
    "PartySharedKillRange": "Party shared kill range",
    "PlayerKillingMode": "Player killing mode",
    "LandClaimCount": "Number of land claims",
    "LandClaimSize": "Size of each land claim",
    "LandClaimDeadZone": "Land claim dead zone",
    "LandClaimExpiryTime": "Land claim expiry time",
    "LandClaimDecayMode": "Land claim decay mode",
    "LandClaimOnlineDurabilityModifier": "Online durability modifier",
    "LandClaimOfflineDurabilityModifier": "Offline durability modifier",
    "LandClaimOfflineDelay": "Offline delay",
    "DynamicMeshEnabled": "Enable dynamic mesh",
    "DynamicMeshLandClaimOnly": "Dynamic mesh for land claims only",
    "DynamicMeshLandClaimBuffer": "Land claim buffer for dynamic mesh",
    "DynamicMeshMaxItemCache": "Max item cache for dynamic mesh",
    "TwitchServerPermission": "Twitch server permission",
    "TwitchBloodMoonAllowed": "Allow Twitch blood moon",
    "QuestProgressionDailyLimit": "Daily quest progression limit",
}

# Detailed descriptions can be populated from web sources; default to short descriptions
DETAILED_DESCRIPTIONS = {k: (v + "\n\n(Short description — load detailed help from web via Help ▸ Update Help)") for k, v in DESCRIPTIONS.items()}

# Pages to fetch when updating help from web (common community/wiki pages)
WEB_HELP_PAGES = [
    "https://7daystodie.fandom.com/wiki/Server_Configuration",
    "https://7daystodie.fandom.com/wiki/Server_Commands",
    "https://community.7daystodie.com/",
    "https://7daystodie.com/",
    "https://steamcommunity.com/app/251570/discussions/",
]


def extract_comments_descriptions(path):
    """Extract comments preceding property elements and map them to property names.

    Looks for patterns: <!-- comment -->\n<property name="SettingName" ...>
    Returns dict: {SettingName: comment_text}
    """
    import re
    results = {}
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    except Exception:
        return results

    # Match comment followed by a property element with a name attribute
    pattern = re.compile(r'<!--(.*?)-->\s*<property[^>]*\bname\s*=\s*["\']([^"\']+)["\']', re.DOTALL | re.IGNORECASE)
    for m in pattern.finditer(text):
        comment = m.group(1).strip()
        # normalize whitespace in comment
        comment = re.sub(r'\s+', ' ', comment)
        name = m.group(2).strip()
        if name:
            results[name] = comment

    return results


TAB_DEFINITIONS = {
    "🔧 General Server Settings": [
        "ServerName", "ServerDescription", "ServerWebsiteURL", "ServerPassword",
        "ServerLoginConfirmationText", "Region", "Language", "ServerPort",
        "ServerVisibility", "ServerDisabledNetworkProtocols", "ServerMaxWorldTransferSpeedKiBs",
        "ServerMaxPlayerCount", "ServerReservedSlots", "ServerReservedSlotsPermission",
        "ServerAdminSlots", "ServerAdminSlotsPermission", "WebDashboardEnabled",
        "WebDashboardPort", "WebDashboardUrl", "EnableMapRendering", "TelnetEnabled",
        "TelnetPort", "TelnetPassword", "TelnetFailedLoginLimit", "TelnetFailedLoginsBlocktime",
        "TerminalWindowEnabled", "AdminFileName", "ServerAllowCrossplay", "EACEnabled",
        "IgnoreEOSSanctions", "HideCommandExecutionLog", "MaxUncoveredMapChunksPerPlayer",
    ],
    "🌍 Gameplay - World": [
        "PersistentPlayerProfiles", "MaxChunkAge", "SaveDataLimit", "GameWorld",
        "WorldGenSeed", "WorldGenSize", "GameName", "GameMode",
    ],
    "⚔️ Gameplay - Difficulty": [
        "GameDifficulty", "BlockDamagePlayer", "BlockDamageAI", "BlockDamageAIBM",
        "XPMultiplier", "PlayerSafeZoneLevel", "PlayerSafeZoneHours",
    ],
    "📜 Gameplay - Rules": [
        "BuildCreate", "DayNightLength", "DayLightLength", "BiomeProgression",
        "StormFreq", "DeathPenalty", "DropOnDeath", "DropOnQuit",
        "BedrollDeadZoneSize", "BedrollExpiryTime", "AllowSpawnNearFriend",
        "CameraRestrictionMode", "JarRefund",
    ],
    "⚡ Performance": [
        "MaxSpawnedZombies", "MaxSpawnedAnimals", "ServerMaxAllowedViewDistance",
        "MaxQueuedMeshLayers",
    ],
    "🧟 Zombies": [
        "EnemySpawnMode", "EnemyDifficulty", "ZombieFeralSense", "ZombieMove",
        "ZombieMoveNight", "ZombieFeralMove", "ZombieBMMove", "AISmellMode",
        "BloodMoonFrequency", "BloodMoonRange", "BloodMoonWarning", "BloodMoonEnemyCount",
    ],
    "💰 Loot": [
        "LootAbundance", "LootRespawnDays", "AirDropFrequency", "AirDropMarker",
    ],
    "👥 Multiplayer": ["PartySharedKillRange", "PlayerKillingMode"],
    "🏠 Land Claims": [
        "LandClaimCount", "LandClaimSize", "LandClaimDeadZone", "LandClaimExpiryTime",
        "LandClaimDecayMode", "LandClaimOnlineDurabilityModifier", "LandClaimOfflineDurabilityModifier",
        "LandClaimOfflineDelay", "DynamicMeshEnabled", "DynamicMeshLandClaimOnly",
        "DynamicMeshLandClaimBuffer", "DynamicMeshMaxItemCache",
    ],
    "🎮 Other": ["TwitchServerPermission", "TwitchBloodMoonAllowed", "QuestProgressionDailyLimit"],
}


class ToolTip:
    """Simple tooltip for widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.enter)
        widget.bind("<Leave>", self.leave)

    def enter(self, _):
        if not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Segoe UI", 9))
        label.pack(ipadx=6, ipady=3)

    def leave(self, _):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, borderwidth=0, background="#f0f0f0")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class ServerConfigEditor:
    VERSION = "v1.0"

    def __init__(self, root):
        self.root = root
        self.root.title("7 Days to Die Server Config Editor")
        self.root.geometry("1300x950")
        self.root.minsize(900, 600)
        self.root.configure(bg="#f0f0f0")

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        self.font_header = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        self.font_regular = tkfont.Font(family="Segoe UI", size=10)

        self.filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serverconfig.xml")
        self.tree = None
        self.root_element = None
        self.props_map = {}  # name -> element
        self.widget_rows = {}  # name -> frame/widgets

        self.build_ui()
        self.load_xml()

    def build_ui(self):
        # Header bar
        header = tk.Frame(self.root, bg="#007acc", height=60)
        header.pack(fill="x", side="top")
        title = tk.Label(header, text="7 Days to Die Server Config Editor",
                         bg="#007acc", fg="white", font=("Segoe UI", 18, "bold"))
        title.pack(side="left", padx=16, pady=12)

        # Bug report button (below header, top-left)
        bug_frame = tk.Frame(self.root, bg="#f0f0f0")
        bug_frame.pack(fill="x", side="top", padx=10, pady=(8, 0))
        bug_btn = tk.Button(bug_frame, text="🐛", width=3, relief="flat",
                            command=self.copy_bug_report, bg="#e0e0e0")
        bug_btn.pack(side="left")
        ToolTip(bug_btn, "Copy debug info to clipboard")

        # Menu
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save)
        file_menu.add_command(label="Reload", accelerator="Ctrl+R", command=self.load_xml)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Update Help", command=self.update_help_from_web)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menubar)

        # Search bar
        search_frame = tk.Frame(self.root, bg="#f0f0f0")
        search_frame.pack(fill="x", padx=12, pady=10)
        search_icon = tk.Label(search_frame, text="🔍", bg="#f0f0f0")
        search_icon.pack(side="left", padx=(4, 6))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=self.font_regular,
                                relief="solid", bg="white")
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        search_entry.bind("<KeyRelease>", lambda e: self.on_search())
        clear_btn = tk.Button(search_frame, text="Clear", command=self.clear_search, bg="#e0e0e0")
        clear_btn.pack(side="right")

        # Notebook tabs
        self.notebook = ttk.Notebook(self.root)
        self.tabs = {}
        for tab_name in TAB_DEFINITIONS.keys():
            frame = ScrollableFrame(self.notebook)
            self.notebook.add(frame, text=tab_name)
            self.tabs[tab_name] = frame
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        # Bottom buttons and status
        bottom_frame = tk.Frame(self.root, bg="#f0f0f0")
        bottom_frame.pack(fill="x", side="bottom")
        btn_frame = tk.Frame(bottom_frame, bg="#f0f0f0")
        btn_frame.pack(side="right", padx=12, pady=12)
        save_btn = tk.Button(btn_frame, text="Save", command=self.save,
                             bg="#007acc", fg="white", padx=12, pady=6, relief="flat")
        reload_btn = tk.Button(btn_frame, text="Reload", command=self.load_xml,
                               bg="#007acc", fg="white", padx=12, pady=6, relief="flat")
        save_btn.pack(side="right", padx=(6, 0))
        reload_btn.pack(side="right")

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(self.root, textvariable=self.status_var, anchor="w",
                          bg="#e0e0e0", fg="#333333")
        status.pack(fill="x", side="bottom")

        # Footer
        footer = tk.Label(self.root, text=f"{self.VERSION} - 7 Days to Die Server Config Editor",
                          bg="#dcdcdc", font=("Segoe UI", 9))
        footer.pack(fill="x", side="bottom")

        # Bind keys
        self.root.bind_all('<Control-s>', lambda e: self.save())
        self.root.bind_all('<Control-S>', lambda e: self.save())
        self.root.bind_all('<Control-r>', lambda e: self.load_xml())
        self.root.bind_all('<Control-R>', lambda e: self.load_xml())

    def show_about(self):
        messagebox.showinfo("About", "7 Days to Die Server Config Editor\nVersion: " + self.VERSION)

    def clear_search(self):
        self.search_var.set("")
        self.on_search()

    def load_xml(self, *_):
        # If the expected file doesn't exist, try some common locations and allow the user to pick one
        candidates = [self.filepath, os.path.join(os.getcwd(), "serverconfig.xml")]
        pf86 = os.environ.get('PROGRAMFILES(X86)')
        pf = os.environ.get('PROGRAMFILES')
        if pf86:
            candidates.append(os.path.join(pf86, 'Steam', 'steamapps', 'common', '7 Days to Die Dedicated Server', 'serverconfig.xml'))
        if pf:
            candidates.append(os.path.join(pf, 'Steam', 'steamapps', 'common', '7 Days to Die Dedicated Server', 'serverconfig.xml'))
        # include a literal common path (helps for some installs)
        candidates.append(r"C:\Program Files (x86)\Steam\steamapps\common\7 Days to Die Dedicated Server\serverconfig.xml")

        found = None
        for p in candidates:
            try:
                if p and os.path.exists(p):
                    found = p
                    break
            except Exception:
                continue

        if found:
            self.filepath = found
        else:
            ask = messagebox.askyesno("serverconfig.xml not found",
                                      f"serverconfig.xml not found at: {self.filepath}\nWould you like to locate it manually?")
            if not ask:
                self.status_var.set("Error: serverconfig.xml not found")
                return
            chosen = filedialog.askopenfilename(title="Locate serverconfig.xml",
                                                initialdir=os.path.expanduser("~"),
                                                filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
            if not chosen:
                self.status_var.set("Error: no file selected")
                return
            self.filepath = chosen

        try:
            self.tree = ET.parse(self.filepath)
            self.root_element = self.tree.getroot()
        except ET.ParseError as e:
            messagebox.showerror("XML Error", f"Error parsing XML: {e}")
            self.status_var.set("Error parsing XML")
            return

        # Try extracting detailed descriptions from XML comments in the file
        try:
            comments_map = extract_comments_descriptions(self.filepath)
            imported = 0
            for k, v in comments_map.items():
                DETAILED_DESCRIPTIONS[k] = v
                imported += 1
            if imported:
                self.status_var.set(f"Loaded {len(self.props_map)} properties; imported {imported} descriptions from XML comments")
        except Exception:
            # non-fatal: continue without detailed descriptions
            pass

        # build property map
        self.props_map.clear()
        for prop in self.root_element.findall('.//property'):
            name = prop.get('name')
            if not name:
                # sometimes name is attribute, sometimes element text used differently
                continue
            self.props_map[name] = prop

        # Create UI rows for properties (if not yet created)
        self.widget_rows.clear()
        for tab_name, names in TAB_DEFINITIONS.items():
            frame_container = self.tabs[tab_name].scrollable_frame
            # clear existing children
            for child in frame_container.winfo_children():
                child.destroy()

            for pname in names:
                self.create_property_row(frame_container, pname)

        self.status_var.set(f"Loaded {len(self.props_map)} properties from serverconfig.xml")

    def create_property_row(self, container, name):
        # Row frame
        row = tk.Frame(container, bg="#f0f0f0")
        row.pack(fill="x", pady=6, padx=6)
        lbl = tk.Label(row, text=name, anchor="w", width=34, bg="#f0f0f0", fg="#666666",
                       font=self.font_regular)
        lbl.pack(side="left", padx=(6, 12))

        val = ""
        elem = self.props_map.get(name)
        if elem is not None:
            if 'value' in elem.attrib:
                val = elem.get('value', '')
            elif elem.text and elem.text.strip():
                val = elem.text.strip()
            else:
                # check for <value> child
                vchild = elem.find('value')
                if vchild is not None and vchild.text:
                    val = vchild.text.strip()

        entry_var = tk.StringVar(value=val)
        entry = tk.Entry(row, textvariable=entry_var, relief="solid", bg="white",
                         font=self.font_regular)
        entry.pack(side="right", fill="x", expand=True, padx=(6, 12))
        desc = DESCRIPTIONS.get(name, "")
        if desc:
            ToolTip(entry, desc)

        # Help button to show detailed description
        help_btn = tk.Button(row, text='?', width=2, relief='groove', bg="#e8e8e8",
                             command=lambda n=name: self.show_help(n))
        help_btn.pack(side="right", padx=(0, 6))

        self.widget_rows[name] = {
            'frame': row,
            'label': lbl,
            'entry': entry,
            'var': entry_var,
            'description': desc,
        }

    def show_help(self, name):
        text = DETAILED_DESCRIPTIONS.get(name) or DESCRIPTIONS.get(name) or "No description available."
        win = tk.Toplevel(self.root)
        win.title(f"Help: {name}")
        win.geometry("560x320")
        lbl = tk.Label(win, text=name, font=("Segoe UI", 12, "bold"))
        lbl.pack(anchor='w', padx=8, pady=(8, 4))
        txt = tk.Text(win, wrap='word', bg='white')
        txt.insert('1.0', text)
        txt.config(state='disabled')
        txt.pack(fill='both', expand=True, padx=8, pady=8)

    def update_help_from_web(self):
        # Offer JSON import or live web fetch
        choice = messagebox.askquestion("Update Help",
                                        "Choose method to update help:\nYes = Fetch from web (may take time).\nNo = Load from a local JSON file.",
                                        icon='question')
        if choice == 'no':
            chosen = filedialog.askopenfilename(title="Select help JSON",
                                                filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
            if not chosen:
                return
            try:
                import json
                with open(chosen, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                updated = 0
                for k, v in data.items():
                    DETAILED_DESCRIPTIONS[k] = v
                    updated += 1
                messagebox.showinfo("Update Help", f"Updated {updated} descriptions from JSON.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load help JSON: {e}")
            return

        # Otherwise fetch from web
        try:
            import requests
            from bs4 import BeautifulSoup
        except Exception:
            res = messagebox.askyesno("Dependencies missing",
                                      "The features to fetch help from the web require 'requests' and 'beautifulsoup4'.\nInstall them now? (Internet required)")
            if res:
                try:
                    import subprocess, sys
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"]) 
                    import requests
                    from bs4 import BeautifulSoup
                except Exception as e:
                    messagebox.showerror("Install failed", f"Failed to install dependencies: {e}")
                    return
            else:
                return

        names = list(DETAILED_DESCRIPTIONS.keys())
        combined_texts = []
        for url in WEB_HELP_PAGES:
            try:
                r = requests.get(url, timeout=12)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    texts = []
                    for tag in soup.find_all(['p', 'li', 'td', 'div']):
                        if tag.get_text(strip=True):
                            texts.append(tag.get_text(' ', strip=True))
                    combined_texts.append('\n'.join(texts))
            except Exception:
                continue

        updated = 0
        for name in names:
            lname = name.lower()
            best = None
            for page_text in combined_texts:
                idx = page_text.lower().find(lname)
                if idx != -1:
                    start = max(0, idx - 200)
                    end = min(len(page_text), idx + 400)
                    snippet = page_text[start:end]
                    snippet = ' '.join(snippet.split())
                    best = snippet
                    break
            if best:
                DETAILED_DESCRIPTIONS[name] = best
                updated += 1

        messagebox.showinfo("Update Help", f"Fetched and updated {updated} descriptions from web pages.")

    def on_search(self):
        q = self.search_var.get().strip().lower()
        for name, rowd in self.widget_rows.items():
            txt = name.lower()
            desc = (rowd.get('description') or "").lower()
            frame = rowd['frame']
            if not q or q in txt or q in desc:
                frame.pack(fill="x", pady=6, padx=6)
            else:
                frame.pack_forget()

    def save(self, *_):
        if not self.tree or not self.root_element:
            messagebox.showerror("No file loaded", "No serverconfig.xml is loaded to save to.")
            return
        # Update elements from widget_rows
        for name, rowd in self.widget_rows.items():
            newval = rowd['var'].get()
            elem = self.props_map.get(name)
            if elem is None:
                # create a new property element under root
                elem = ET.SubElement(self.root_element, 'property')
                elem.set('name', name)
                elem.set('value', newval)
                self.props_map[name] = elem
            else:
                if 'value' in elem.attrib:
                    elem.set('value', newval)
                else:
                    # set text
                    elem.text = newval

        # Write back to file safely
        bak = self.filepath + ".bak"
        try:
            if os.path.exists(self.filepath):
                try:
                    os.replace(self.filepath, bak)
                except Exception:
                    # fallback: copy
                    import shutil
                    shutil.copy2(self.filepath, bak)
            self.tree.write(self.filepath, encoding='utf-8', xml_declaration=True)
            self.status_var.set(f"Saved {len(self.widget_rows)} properties at {datetime.now().strftime('%H:%M:%S')}")
            messagebox.showinfo("Saved", "serverconfig.xml saved successfully.")
        except Exception as e:
            messagebox.showerror("Save error", f"Failed saving: {e}")
            self.status_var.set("Error saving file")

    def copy_bug_report(self):
        info = {
            'platform': platform.platform(),
            'python': sys.version.replace('\n', ' '),
            'script': os.path.abspath(__file__),
            'config_path': self.filepath,
            'loaded_props': len(self.props_map),
            'timestamp': datetime.now().isoformat(),
        }
        txt = "\n".join(f"{k}: {v}" for k, v in info.items())
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(txt)
            messagebox.showinfo("Copied", "Debug info copied to clipboard.")
        except Exception as e:
            messagebox.showerror("Clipboard error", f"Could not copy to clipboard: {e}")


def main():
    root = tk.Tk()
    app = ServerConfigEditor(root)
    root.mainloop()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
7 Days to Die Server Configuration Editor
A comprehensive Tkinter GUI for editing serverconfig.xml with meticulous attention to design details.

Version: 1.1.1
Author: Niggot Development Team
License: NDT
"""

import os
import re
import sys
import json
import platform
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import subprocess
import webbrowser
from urllib.parse import quote


# ============================================================================
# CORE CONFIGURATION
# ============================================================================

DEFAULT_CONFIG_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\7 Days to Die Dedicated Server\serverconfig.xml"

# EXACT property mappings per specification
TAB_DEFINITIONS = {
    "🔧 General": [
        "ServerName", "ServerDescription", "ServerWebsiteURL", "ServerPassword",
        "ServerLoginConfirmationText", "Region", "Language", "ServerPort",
        "ServerVisibility", "ServerDisabledNetworkProtocols", "ServerMaxWorldTransferSpeedKiBs",
        "ServerMaxPlayerCount", "ServerReservedSlots", "ServerReservedSlotsPermission",
        "ServerAdminSlots", "ServerAdminSlotsPermission", "WebDashboardEnabled",
        "WebDashboardPort", "WebDashboardUrl", "EnableMapRendering", "TelnetEnabled",
        "TelnetPort", "TelnetPassword", "TelnetFailedLoginLimit", "TelnetFailedLoginsBlocktime",
        "TerminalWindowEnabled", "AdminFileName", "ServerAllowCrossplay", "EACEnabled",
        "IgnoreEOSSanctions", "HideCommandExecutionLog", "MaxUncoveredMapChunksPerPlayer"
    ],
    "🌍 World": [
        "PersistentPlayerProfiles", "MaxChunkAge", "SaveDataLimit", "GameWorld",
        "WorldGenSeed", "WorldGenSize", "GameName", "GameMode"
    ],
    "⚔️ Difficulty": [
        "GameDifficulty", "BlockDamagePlayer", "BlockDamageAI", "BlockDamageAIBM",
        "XPMultiplier", "PlayerSafeZoneLevel", "PlayerSafeZoneHours"
    ],
    "📜 Rules": [
        "BuildCreate", "DayNightLength", "DayLightLength", "BiomeProgression",
        "StormFreq", "DeathPenalty", "DropOnDeath", "DropOnQuit",
        "BedrollDeadZoneSize", "BedrollExpiryTime", "AllowSpawnNearFriend",
        "CameraRestrictionMode", "JarRefund"
    ],
    "⚡ Performance": [
        "MaxSpawnedZombies", "MaxSpawnedAnimals", "ServerMaxAllowedViewDistance",
        "MaxQueuedMeshLayers"
    ],
    "🧟 Zombies": [
        "EnemySpawnMode", "EnemyDifficulty", "ZombieFeralSense", "ZombieMove",
        "ZombieMoveNight", "ZombieFeralMove", "ZombieBMMove", "AISmellMode",
        "BloodMoonFrequency", "BloodMoonRange", "BloodMoonWarning", "BloodMoonEnemyCount"
    ],
    "💰 Loot": [
        "LootAbundance", "LootRespawnDays", "AirDropFrequency", "AirDropMarker"
    ],
    "👥 Multiplayer": [
        "PartySharedKillRange", "PlayerKillingMode"
    ],
    "🏠 Claims": [
        "LandClaimCount", "LandClaimSize", "LandClaimDeadZone", "LandClaimExpiryTime",
        "LandClaimDecayMode", "LandClaimOnlineDurabilityModifier", "LandClaimOfflineDurabilityModifier",
        "LandClaimOfflineDelay", "DynamicMeshEnabled", "DynamicMeshLandClaimOnly",
        "DynamicMeshLandClaimBuffer", "DynamicMeshMaxItemCache"
    ],
    "🎮 Other": [
        "TwitchServerPermission", "TwitchBloodMoonAllowed", "QuestProgressionDailyLimit"
    ]
}

# Comprehensive property descriptions
PROPERTY_DESCRIPTIONS = {
    "ServerName": "Name of the server displayed in server browser",
    "ServerDescription": "Description shown for the server",
    "ServerWebsiteURL": "Website URL associated with the server",
    "ServerPassword": "Password required to join the server",
    "ServerLoginConfirmationText": "Message shown when player logs in",
    "Region": "Server region identifier",
    "Language": "Server language code",
    "ServerPort": "Port number for server connections",
    "ServerVisibility": "Public or private server visibility",
    "ServerDisabledNetworkProtocols": "Network protocols to disable",
    "ServerMaxWorldTransferSpeedKiBs": "Maximum world transfer speed in KiB/s",
    "ServerMaxPlayerCount": "Maximum concurrent players allowed",
    "ServerReservedSlots": "Number of reserved player slots",
    "ServerReservedSlotsPermission": "Permission level for reserved slots",
    "ServerAdminSlots": "Number of admin-only slots",
    "ServerAdminSlotsPermission": "Permission level for admin slots",
    "WebDashboardEnabled": "Enable or disable web dashboard",
    "WebDashboardPort": "Port for web dashboard access",
    "WebDashboardUrl": "Base URL for web dashboard",
    "EnableMapRendering": "Enable or disable map rendering",
    "TelnetEnabled": "Enable or disable telnet interface",
    "TelnetPort": "Port for telnet connections",
    "TelnetPassword": "Password for telnet access",
    "TelnetFailedLoginLimit": "Max failed login attempts",
    "TelnetFailedLoginsBlocktime": "Block time after failed logins (minutes)",
    "TerminalWindowEnabled": "Show terminal window for server",
    "AdminFileName": "Admin configuration filename",
    "ServerAllowCrossplay": "Allow crossplay between platforms",
    "EACEnabled": "Enable Easy Anti-Cheat",
    "IgnoreEOSSanctions": "Ignore EOS account sanctions",
    "HideCommandExecutionLog": "Hide command execution in logs",
    "MaxUncoveredMapChunksPerPlayer": "Maximum uncovered map chunks per player",
    "PersistentPlayerProfiles": "Save player profiles persistently",
    "MaxChunkAge": "Maximum chunk age before deletion (days)",
    "SaveDataLimit": "Maximum save data size in MB",
    "GameWorld": "World name/identifier",
    "WorldGenSeed": "World generation seed number",
    "WorldGenSize": "World size (4096, 8192, 16384)",
    "GameName": "Game instance name",
    "GameMode": "Game mode (Survival, Creative, etc)",
    "GameDifficulty": "Game difficulty setting (0-5)",
    "BlockDamagePlayer": "Block damage multiplier for players",
    "BlockDamageAI": "Block damage multiplier for zombies",
    "BlockDamageAIBM": "Block damage during blood moon",
    "XPMultiplier": "Experience gain multiplier",
    "PlayerSafeZoneLevel": "Safe zone size/level",
    "PlayerSafeZoneHours": "Hours of protection after spawn",
    "BuildCreate": "Allow building and creation",
    "DayNightLength": "Day/night cycle length in minutes",
    "DayLightLength": "Daylight duration in minutes",
    "BiomeProgression": "Progression through biomes",
    "StormFreq": "Frequency of storms",
    "DeathPenalty": "Penalty for player death",
    "DropOnDeath": "Drop items when player dies",
    "DropOnQuit": "Drop items when player quits",
    "BedrollDeadZoneSize": "Bedroll spawn dead zone radius",
    "BedrollExpiryTime": "Bedroll expiry time (days)",
    "AllowSpawnNearFriend": "Spawn near friends option",
    "CameraRestrictionMode": "Camera movement restrictions",
    "JarRefund": "Percentage refund for jar crafting",
    "MaxSpawnedZombies": "Maximum active zombie count",
    "MaxSpawnedAnimals": "Maximum active animal count",
    "ServerMaxAllowedViewDistance": "Maximum view distance in chunks",
    "MaxQueuedMeshLayers": "Maximum mesh layer queue size",
    "EnemySpawnMode": "Enemy spawn method",
    "EnemyDifficulty": "Enemy difficulty (0-5)",
    "ZombieFeralSense": "Zombie feral sense ability level",
    "ZombieMove": "Zombie movement speed multiplier",
    "ZombieMoveNight": "Night zombie movement speed",
    "ZombieFeralMove": "Feral zombie movement speed",
    "ZombieBMMove": "Blood moon zombie movement",
    "AISmellMode": "Zombie smell detection sensitivity",
    "BloodMoonFrequency": "Days between blood moons",
    "BloodMoonRange": "Blood moon spawn range",
    "BloodMoonWarning": "Blood moon warning time (minutes)",
    "BloodMoonEnemyCount": "Enemy count during blood moon",
    "LootAbundance": "Loot spawn multiplier",
    "LootRespawnDays": "Days until loot respawns",
    "AirDropFrequency": "Air drop frequency in days",
    "AirDropMarker": "Air drop marker visibility",
    "PartySharedKillRange": "Range for party kill sharing",
    "PlayerKillingMode": "Player vs player mode settings",
    "LandClaimCount": "Maximum land claims per player",
    "LandClaimSize": "Land claim block radius",
    "LandClaimDeadZone": "Land claim dead zone radius",
    "LandClaimExpiryTime": "Land claim expiry time (days)",
    "LandClaimDecayMode": "Claim decay mode (off, on, etc)",
    "LandClaimOnlineDurabilityModifier": "Online durability multiplier",
    "LandClaimOfflineDurabilityModifier": "Offline durability multiplier",
    "LandClaimOfflineDelay": "Hours before offline protection",
    "DynamicMeshEnabled": "Enable dynamic mesh system",
    "DynamicMeshLandClaimOnly": "Dynamic mesh for claims only",
    "DynamicMeshLandClaimBuffer": "Buffer zone for dynamic mesh",
    "DynamicMeshMaxItemCache": "Maximum item cache size",
    "TwitchServerPermission": "Twitch integration permission",
    "TwitchBloodMoonAllowed": "Allow blood moon via Twitch",
    "QuestProgressionDailyLimit": "Daily quest progression limit",
}


# ============================================================================
# UTILITY CLASSES
# ============================================================================

class ToolTip:
    """Tooltip widget that appears on hover with word wrapping."""
    
    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        
        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        widget.bind("<Motion>", self._on_motion, add="+")
    
    def _on_enter(self, event):
        self._schedule_show()
    
    def _on_motion(self, event):
        self.x, self.y = event.x_root + 15, event.y_root + 15
        if self.tip_window:
            self.tip_window.wm_geometry(f"+{self.x}+{self.y}")
    
    def _on_leave(self, event):
        self._cancel_show()
        self._hide()
    
    def _schedule_show(self):
        self._cancel_show()
        self.id = self.widget.after(500, self._show)
    
    def _cancel_show(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
    
    def _show(self):
        if self.tip_window or not self.text:
            return
        
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{self.x}+{self.y}")
        
        label = tk.Label(
            tw,
            text=self.text,
            background="#ffffe0",
            foreground="#000000",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Segoe UI", 9),
            wraplength=350,
            justify=tk.LEFT,
            padx=8,
            pady=6
        )
        label.pack()
        
        try:
            tw.attributes('-topmost', True)
        except tk.TclError:
            pass
    
    def _hide(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class ScrollableFrame(ttk.Frame):
    """Canvas-based scrollable frame with mousewheel support."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create canvas
        self.canvas = tk.Canvas(self, bg="#f0f0f0", highlightthickness=0, height=400)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Create scrollable frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Place frame in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)
    
    def _on_mousewheel(self, event):
        """Handle Windows mousewheel."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _on_mousewheel_linux(self, event):
        """Handle Linux mousewheel."""
        if event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(3, "units")


# ============================================================================
# XML UTILITIES
# ============================================================================

def extract_comments_from_xml(filepath: str) -> Dict[str, str]:
    """Extract comments that appear after property elements on the same line.
    
    Looks for:
    <property name="PropertyName" value="..." />		<!-- Comment text -->
    
    Returns mapping of property names to comment text.
    """
    comments = {}
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return comments
    
    # Pattern: property tag followed by comment on same line
    # <property name="PropName" ... /> <!-- comment -->
    pattern = re.compile(
        r'<\s*property\s+[^>]*?name\s*=\s*["\']([^"\']+)["\'][^>]*?/>\s*<!--\s*(.*?)\s*-->',
        re.IGNORECASE
    )
    
    for match in pattern.finditer(content):
        prop_name = match.group(1)
        comment_text = match.group(2).strip()
        
        if prop_name and comment_text:
            # Normalize whitespace in comment
            comment_text = re.sub(r'\s+', ' ', comment_text)
            comments[prop_name] = comment_text
    
    return comments


def repair_xml_encoding(filepath: str) -> bool:
    """Repair common XML encoding issues without modifying original until save.
    
    Handles:
    - UTF-8 BOM removal
    - UTF-16 detection and conversion
    - Stray bytes before XML declaration
    """
    try:
        with open(filepath, 'rb') as f:
            original_data = f.read()
        
        data = bytearray(original_data)
        modified = False
        
        # Check and remove UTF-8 BOM
        if data.startswith(b'\xef\xbb\xbf'):
            data = data[3:]
            modified = True
        
        # Check for UTF-16 LE BOM and convert
        elif data.startswith(b'\xff\xfe'):
            try:
                text = bytes(data).decode('utf-16-le')
                data = bytearray(text.encode('utf-8'))
                modified = True
            except Exception:
                pass
        
        # Check for UTF-16 BE BOM and convert
        elif data.startswith(b'\xfe\xff'):
            try:
                text = bytes(data).decode('utf-16-be')
                data = bytearray(text.encode('utf-8'))
                modified = True
            except Exception:
                pass
        
        # Remove stray bytes before XML declaration
        xml_start = bytes(data).find(b'<?xml')
        if xml_start > 0:
            data = data[xml_start:]
            modified = True
        
        # Verify it's valid XML
        try:
            ET.fromstring(bytes(data))
        except ET.ParseError as e:
            return False
        
        return modified
    
    except Exception:
        return False


# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================

class ServerConfigEditor:
    """Main application for 7 Days to Die server configuration editing."""
    
    VERSION = "1.2.0"
    
    def __init__(self, root):
        self.root = root
        self.root.title("7 Days to Die Server Config Editor")
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)
        self.root.configure(bg="#f0f0f0")
        
        # Center window on screen
        self._center_window()
        
        # Data
        self.config_file = DEFAULT_CONFIG_PATH
        self.xml_tree = None
        self.xml_root = None
        self.properties_map = {}  # name -> Element
        self.property_vars = {}   # name -> tk.StringVar
        self.comments = {}         # name -> comment text
        self.property_rows = {}    # name -> (Frame, tab_name) tuple
        self.is_dirty = False
        
        # Search tracking
        self.search_results = []   # List of (tab_name, prop_name) tuples
        self.current_result_index = 0
        self.result_counter_var = tk.StringVar(value="")
        
        # Setup styles
        self._configure_styles()
        
        # Build UI
        self._build_ui()
        
        # Load configuration
        self._load_configuration()
        
        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # Bind shortcuts
        self.root.bind("<Control-s>", lambda e: self.save_configuration())
        self.root.bind("<Control-r>", lambda e: self._load_configuration())
    
    def _configure_styles(self):
        """Configure ttk theme and colors."""
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        
        # Configure colors for clam theme
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TNotebook.Tab", font=("Segoe UI", 10))
    
    def _center_window(self):
        """Center the window on the screen after it's fully rendered."""
        def do_center():
            self.root.update_idletasks()
            
            # Get window dimensions
            window_width = 1200
            window_height = 750
            
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Calculate center position
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            # Ensure position is not negative
            x = max(0, x)
            y = max(0, y)
            
            # Set window position
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Schedule centering after window is fully initialized
        self.root.after(100, do_center)
    
    def _build_ui(self):
        """Construct the complete user interface."""
        # Header bar (blue)
        self._create_header()
        
        # Bug report button
        self._create_bug_button()
        
        # Menu bar
        self._create_menubar()
        
        # Search bar
        self._create_search_bar()
        
        # Notebook with tabs
        self._create_notebook()
        
        # Save/Reload buttons
        self._create_action_buttons()
        
        # Status bar
        self._create_status_bar()
        
        # Footer
        self._create_footer()
    
    def _create_header(self):
        """Create the blue header banner."""
        header = tk.Frame(self.root, bg="#007acc", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header,
            text="7 Days to Die Server Config Editor",
            font=("Segoe UI", 20, "bold"),
            bg="#007acc",
            fg="white"
        )
        title_label.pack(side="left", padx=20, pady=15)
    
    def _create_bug_button(self):
        """Create bug report button in top-right."""
        container = tk.Frame(self.root, bg="#f0f0f0")
        container.pack(fill="x", padx=15, pady=8)
        
        btn = tk.Button(
            container,
            text="🐛",
            font=("Arial", 13),
            width=5,
            height=1,
            bg="#e0e0e0",
            activebackground="#d0d0d0",
            relief="raised",
            command=self._copy_debug_info
        )
        btn.pack(side="left")
        
        ToolTip(btn, "Copy debug information to clipboard")
    
    def _create_menubar(self):
        """Create application menu bar."""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(
            label="Save Configuration",
            accelerator="Ctrl+S",
            command=self.save_configuration
        )
        file_menu.add_command(
            label="Reload Configuration",
            accelerator="Ctrl+R",
            command=self._load_configuration
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Open File...",
            command=self._browse_for_file
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Exit",
            command=self._on_window_close
        )
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="About",
            command=self._show_about_dialog
        )
        help_menu.add_command(
            label="Change Log",
            command=self._show_changelog
        )
        help_menu.add_command(
            label="Report a Bug",
            command=self._show_bug_report_dialog
        )
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def _create_search_bar(self):
        """Create search and filter bar with global search across all tabs."""
        search_frame = tk.Frame(self.root, bg="#f0f0f0")
        search_frame.pack(fill="x", padx=15, pady=12)
        
        # Icon
        icon_label = tk.Label(search_frame, text="🔍", bg="#f0f0f0", font=("Arial", 12))
        icon_label.pack(side="left", padx=(0, 10))
        
        # Search input
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
            relief="solid",
            borderwidth=1,
            bg="white",
            fg="#000000"
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        search_entry.bind("<KeyRelease>", lambda e: self._global_search())
        search_entry.bind("<Return>", lambda e: self._go_to_next_result())
        
        # Result counter
        counter_label = tk.Label(
            search_frame,
            textvariable=self.result_counter_var,
            bg="#f0f0f0",
            fg="#666666",
            font=("Segoe UI", 10),
            width=10
        )
        counter_label.pack(side="right", padx=(10, 0))
        
        # Next button
        next_btn = tk.Button(
            search_frame,
            text="Next ▶",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            activebackground="#d0d0d0",
            relief="raised",
            width=7,
            command=self._go_to_next_result
        )
        next_btn.pack(side="right", padx=(5, 0))
        
        # Previous button
        prev_btn = tk.Button(
            search_frame,
            text="◀ Prev",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            activebackground="#d0d0d0",
            relief="raised",
            width=7,
            command=self._go_to_prev_result
        )
        prev_btn.pack(side="right", padx=(5, 0))
        
        # Clear button
        clear_btn = tk.Button(
            search_frame,
            text="Clear",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            activebackground="#d0d0d0",
            relief="raised",
            width=7,
            command=self._clear_search
        )
        clear_btn.pack(side="right", padx=(5, 0))
    
    def _create_notebook(self):
        """Create tabbed notebook with all property tabs."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        
        self.tab_frames = {}
        
        for tab_name in TAB_DEFINITIONS.keys():
            frame = ScrollableFrame(self.notebook)
            self.tab_frames[tab_name] = frame
            self.notebook.add(frame, text=tab_name)
    
    def _create_action_buttons(self):
        """Create Save and Reload buttons."""
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(fill="x", padx=15, pady=12)
        
        buttons_container = tk.Frame(button_frame, bg="#f0f0f0")
        buttons_container.pack(side="right")
        
        # Reload button
        reload_btn = tk.Button(
            buttons_container,
            text="Reload",
            font=("Segoe UI", 10),
            bg="#007acc",
            fg="white",
            activebackground="#005f9e",
            activeforeground="white",
            relief="raised",
            padx=15,
            pady=6,
            command=self._load_configuration
        )
        reload_btn.pack(side="right", padx=(10, 0))
        
        # Save button
        save_btn = tk.Button(
            buttons_container,
            text="Save",
            font=("Segoe UI", 10),
            bg="#007acc",
            fg="white",
            activebackground="#005f9e",
            activeforeground="white",
            relief="raised",
            padx=15,
            pady=6,
            command=self.save_configuration
        )
        save_btn.pack(side="right")
    
    def _create_status_bar(self):
        """Create status bar at bottom."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            bg="#e0e0e0",
            fg="#333333",
            font=("Segoe UI", 9),
            padx=15,
            pady=6
        )
        status_bar.pack(fill="x", side="bottom")
    
    def _create_footer(self):
        """Create footer bar."""
        footer = tk.Label(
            self.root,
            text=f"Version {self.VERSION} © 7 Days to Die Server Config Editor by Mayhem Mods",
            bg="#dcdcdc",
            fg="#666666",
            font=("Segoe UI", 8),
            padx=15,
            pady=4
        )
        footer.pack(fill="x", side="bottom")
    
    def _load_configuration(self):
        """Load XML configuration file."""
        if not os.path.exists(self.config_file):
            response = messagebox.askyesno(
                "File Not Found",
                f"Configuration file not found:\n\n{self.config_file}\n\nBrowse for file?"
            )
            if response:
                self._browse_for_file()
            else:
                self.status_var.set("Error: Configuration file not found")
            return
        
        try:
            # Parse XML
            self.xml_tree = ET.parse(self.config_file)
            self.xml_root = self.xml_tree.getroot()
            
        except ET.ParseError as parse_error:
            # Attempt repair
            if repair_xml_encoding(self.config_file):
                try:
                    self.xml_tree = ET.parse(self.config_file)
                    self.xml_root = self.xml_tree.getroot()
                    self.status_var.set("Loaded (XML was repaired)")
                except Exception as e:
                    messagebox.showerror("XML Error", f"Failed to parse XML after repair:\n{e}")
                    self.status_var.set("Error: XML parsing failed")
                    return
            else:
                messagebox.showerror(
                    "XML Parse Error",
                    f"Failed to parse XML file:\n{parse_error}"
                )
                self.status_var.set("Error: XML parsing failed")
                return
        
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load file:\n{e}")
            self.status_var.set("Error: File load failed")
            return
        
        # Extract comments from XML
        try:
            self.comments = extract_comments_from_xml(self.config_file)
        except Exception:
            self.comments = {}
        
        # Build property map
        self.properties_map.clear()
        for element in self.xml_root.findall(".//property"):
            name = element.get("name")
            if name:
                self.properties_map[name] = element
        
        # Populate UI
        self._populate_all_tabs()
        
        # Update status
        filename = os.path.basename(self.config_file)
        prop_count = len(self.properties_map)
        self.status_var.set(f"Loaded {filename} • {prop_count} properties")
        self.is_dirty = False
    
    def _populate_all_tabs(self):
        """Populate all tabs with property rows."""
        self.property_vars.clear()
        self.property_rows.clear()
        
        for tab_name, property_names in TAB_DEFINITIONS.items():
            # Get the scrollable frame inside this tab
            scrollable_frame = self.tab_frames[tab_name].scrollable_frame
            
            # Clear existing widgets
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            # Add property rows
            for prop_name in property_names:
                if prop_name in self.properties_map:
                    self._add_property_row(scrollable_frame, prop_name, tab_name)
    
    def _add_property_row(self, parent, prop_name: str, tab_name: str = ""):
        """Add a single property row with label and entry."""
        elem = self.properties_map.get(prop_name)
        value = elem.get("value", "") if elem is not None else ""
        
        # Create row frame
        row_frame = tk.Frame(parent, bg="#f0f0f0")
        row_frame.pack(fill="x", padx=10, pady=8)
        
        # Store tab reference on frame
        row_frame._tab_name = tab_name
        row_frame._prop_name = prop_name
        
        # Create label frame to hold property name and ? icon
        label_frame = tk.Frame(row_frame, bg="#f0f0f0")
        label_frame.pack(side="left", padx=(0, 15))
        
        # Property name label (left side, gray text)
        name_label = tk.Label(
            label_frame,
            text=prop_name,
            bg="#f0f0f0",
            fg="#666666",
            font=("Segoe UI", 10),
            anchor="w",
            justify="left"
        )
        name_label.pack(side="left")
        row_frame._label = name_label
        
        # Get tooltip text from XML comments
        tooltip_text = self.comments.get(prop_name) or PROPERTY_DESCRIPTIONS.get(prop_name, "")
        
        # Add ? icon only if there's a description
        if tooltip_text:
            help_icon = tk.Label(
                label_frame,
                text="?",
                bg="#f0f0f0",
                fg="#0066cc",
                font=("Segoe UI", 9, "bold"),
                padx=4,
                cursor="question_arrow"
            )
            help_icon.pack(side="left", padx=(2, 0))
            
            # Attach tooltip to the ? icon
            ToolTip(help_icon, tooltip_text)
        
        # Entry field (right side, white background)
        var = tk.StringVar(value=value)
        entry = tk.Entry(
            row_frame,
            textvariable=var,
            bg="white",
            fg="#000000",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 10)
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        row_frame._entry = entry
        
        # Bind change event
        entry.bind("<KeyRelease>", lambda e: self._mark_dirty())
        
        # Store references
        self.property_vars[prop_name] = var
        self.property_rows[prop_name] = (row_frame, tab_name)
    
    def _global_search(self):
        """Search across all tabs and track all matches - exact substring matching."""
        query = self.search_var.get().strip().lower()
        self.search_results = []
        self.current_result_index = 0
        
        if not query:
            # Clear search - show all, reset highlighting
            self._reset_highlights()
            self._show_all_properties()
            self.result_counter_var.set("")
            return
        
        # Search ONLY through properties defined in TAB_DEFINITIONS
        for tab_name, prop_list in TAB_DEFINITIONS.items():
            for prop_name in prop_list:
                # Check name match - substring in property name (exact match)
                name_match = query in prop_name.lower()
                
                # Check description match - whole word matching only
                tooltip = self.comments.get(prop_name) or PROPERTY_DESCRIPTIONS.get(prop_name, "")
                # Split description into words and check for exact word match
                desc_words = re.findall(r'\b\w+\b', tooltip.lower())
                desc_match = query in desc_words
                
                # Only add if this property actually matches the search
                if name_match or desc_match:
                    self.search_results.append((tab_name, prop_name))
        
        # Update counter and navigate
        if self.search_results:
            self.result_counter_var.set(f"1 of {len(self.search_results)}")
            self._highlight_result(0)
        else:
            self.result_counter_var.set("No results")
            self._reset_highlights()
            self._show_all_properties()
    
    def _reset_highlights(self):
        """Remove highlighting from all property rows."""
        for prop_name, (row_frame, tab_name) in self.property_rows.items():
            row_frame.configure(bg="#f0f0f0")
            if hasattr(row_frame, '_label'):
                row_frame._label.configure(bg="#f0f0f0", fg="#666666")
            if hasattr(row_frame, '_entry'):
                row_frame._entry.configure(bg="white")
    
    def _show_all_properties(self):
        """Show all properties in their respective tabs."""
        for prop_name, (row_frame, tab_name) in self.property_rows.items():
            row_frame.pack(fill="x", padx=10, pady=8)
    
    def _highlight_result(self, index: int):
        """Navigate to and highlight a specific search result."""
        try:
            if not self.search_results or index < 0 or index >= len(self.search_results):
                return
            
            self.current_result_index = index
            tab_name, prop_name = self.search_results[index]
            
            # Verify prop_name exists in properties_map
            if prop_name not in self.properties_map:
                messagebox.showerror("Error", f"Property {prop_name} not found")
                return
            
            # Verify tab_name exists in TAB_DEFINITIONS
            if tab_name not in TAB_DEFINITIONS:
                messagebox.showerror("Error", f"Tab {tab_name} not found")
                return
            
            # Update counter
            self.result_counter_var.set(f"{index + 1} of {len(self.search_results)}")
            
            # First, hide all properties
            for pname, (rframe, tname) in self.property_rows.items():
                rframe.pack_forget()
            
            # Show only properties in the current tab
            for pname, (rframe, tname) in self.property_rows.items():
                if tname == tab_name:
                    rframe.pack(fill="x", padx=10, pady=8)
            
            # Switch to the tab containing this result
            tab_index = list(TAB_DEFINITIONS.keys()).index(tab_name)
            self.notebook.select(tab_index)
            
            # Reset all highlights
            self._reset_highlights()
            
            # Highlight the matching row
            if prop_name in self.property_rows:
                row_frame, _ = self.property_rows[prop_name]
                row_frame.configure(bg="#ffffcc")  # Pale yellow background
                if hasattr(row_frame, '_label'):
                    row_frame._label.configure(bg="#ffffcc", fg="#cc6600")  # Orange text
                if hasattr(row_frame, '_entry'):
                    row_frame._entry.configure(bg="#ffffcc")
                
                # Scroll the frame to make the result visible
                self.root.after(100, lambda: self._scroll_to_widget(row_frame))
        except Exception as e:
            messagebox.showerror("Highlight Error", f"Error highlighting result: {e}")
    
    def _scroll_to_widget(self, widget):
        """Scroll canvas to make widget visible."""
        try:
            # Get the current tab's canvas
            current_tab_index = self.notebook.index(self.notebook.select())
            tab_name = list(TAB_DEFINITIONS.keys())[current_tab_index]
            scrollable_frame = self.tab_frames[tab_name]
            
            # Get widget position relative to canvas
            canvas = scrollable_frame.canvas
            y = widget.winfo_y()
            height = widget.winfo_height()
            canvas_height = canvas.winfo_height()
            
            # Scroll to center the widget
            canvas.yview_moveto((y / (canvas.bbox("all")[3] if canvas.bbox("all") else 1)) - 0.3)
        except Exception:
            pass
    
    def _go_to_next_result(self):
        """Navigate to the next search result."""
        if not self.search_results:
            return
        
        next_index = (self.current_result_index + 1) % len(self.search_results)
        self._highlight_result(next_index)
    
    def _go_to_prev_result(self):
        """Navigate to the previous search result."""
        if not self.search_results:
            return
        
        prev_index = (self.current_result_index - 1) % len(self.search_results)
        self._highlight_result(prev_index)
    
    def _clear_search(self):
        """Clear search and show all properties."""
        self.search_var.set("")
        self.search_results = []
        self.current_result_index = 0
        self._reset_highlights()
        self._show_all_properties()
        self.result_counter_var.set("")
    
    def _browse_for_file(self):
        """Open file browser to select configuration file."""
        filepath = filedialog.askopenfilename(
            title="Select serverconfig.xml",
            filetypes=[("XML Files", "*.xml"), ("All Files", "*.*")],
            initialdir=os.path.dirname(self.config_file) if os.path.dirname(self.config_file) else os.path.expanduser("~")
        )
        
        if filepath:
            self.config_file = filepath
            self._load_configuration()
    
    def save_configuration(self):
        """Save configuration changes to XML file."""
        if not self.xml_root or not self.xml_tree:
            messagebox.showerror("Error", "No configuration loaded.")
            self.status_var.set("Error: No configuration loaded")
            return
        
        try:
            # Update all properties in XML
            for prop_name, var in self.property_vars.items():
                new_value = var.get()
                elem = self.properties_map.get(prop_name)
                
                if elem is not None:
                    elem.set("value", new_value)
                else:
                    # Create new element if it doesn't exist
                    new_elem = ET.SubElement(self.xml_root, "property")
                    new_elem.set("name", prop_name)
                    new_elem.set("value", new_value)
                    self.properties_map[prop_name] = new_elem
            
            # Create backup before save
            backup_path = self.config_file + ".backup"
            try:
                if os.path.exists(self.config_file):
                    shutil.copy2(self.config_file, backup_path)
            except Exception as e:
                messagebox.showwarning("Backup Warning", f"Could not create backup:\n{e}")
            
            # Write XML
            self.xml_tree.write(
                self.config_file,
                encoding="utf-8",
                xml_declaration=True
            )
            
            self.is_dirty = False
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.status_var.set(f"Saved successfully at {timestamp}")
            messagebox.showinfo("Success", "Configuration saved successfully!")
        
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save:\n{e}")
            self.status_var.set("Error: Save failed")
    
    def _mark_dirty(self):
        """Mark configuration as modified."""
        self.is_dirty = True
    
    def _copy_debug_info(self):
        """Copy debug information to clipboard."""
        debug_info = (
            f"Platform: {platform.platform()}\n"
            f"Python: {platform.python_version()}\n"
            f"Script: {os.path.abspath(__file__)}\n"
            f"Config File: {self.config_file}\n"
            f"Properties: {len(self.properties_map)}\n"
            f"Timestamp: {datetime.now().isoformat()}"
        )
        
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(debug_info)
            messagebox.showinfo("Copied", "Debug information copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard:\n{e}")
    
    def _show_about_dialog(self):
        """Show about dialog."""
        about_text = (
            f"7 Days to Die Server Config Editor\n"
            f"Version {self.VERSION}\n\n"
            f"A comprehensive GUI for editing serverconfig.xml\n\n"
            f"Features:\n"
            f"• 10 organized property tabs\n"
            f"• Real-time search filtering\n"
            f"• XML comment extraction for tooltips\n"
            f"• Automatic XML repair for encoding issues\n"
            f"• Backup creation on save\n"
            f"• Keyboard shortcuts (Ctrl+S, Ctrl+R)\n"
            f"• Read-only parsing until explicit save\n\n"
            f"Configuration File:\n"
            f"{self.config_file}"
        )
        messagebox.showinfo("About", about_text)
    
    def _show_changelog(self):
        """Show change log dialog with scrollable text."""
        # Create custom changelog window
        changelog_window = tk.Toplevel(self.root)
        changelog_window.title("Change Log")
        changelog_window.geometry("700x400")
        changelog_window.minsize(600, 300)
        
        # Create frame for text and scrollbar
        frame = tk.Frame(changelog_window, bg="white")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create scrollbar
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        # Create text widget with scrollbar
        text_widget = tk.Text(
            frame,
            wrap="word",
            font=("Segoe UI", 9),
            yscrollcommand=scrollbar.set,
            bg="white",
            fg="#000000"
        )
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Insert changelog content
        changelog = (
            "v1.2.0 (Current)\n"
            "- MINOR: Bug report now has intelligent fallback email delivery\n"
            "- Primary: Try sending via localhost:25 SMTP relay (corporate/ISP networks)\n"
            "- Fallback: If SMTP unavailable, creates files and opens email client\n"
            "- Creates 7D2D_BugReport folder on Desktop with all files\n"
            "- Files saved: serverconfig.xml, serverconfig_changes.xml, BUG_REPORT_INFO.txt\n"
            "- Opens file explorer to folder automatically\n"
            "- Opens email client with pre-filled subject, body, and instructions\n"
            "- Clear instructions for manual file attachment if email client fails\n"
            "- Graceful degradation: Always finds a way to help user send report\n"
            "- Cross-platform: Works on Windows, macOS, and Linux\n\n"
            "v1.1.9\n"
            "- PATCH: Bug report now automatically sends with MIME attachments\n"
            "- Removed user email client requirement - uses SMTP directly\n"
            "- Automatically attaches serverconfig.xml with proper MIME encoding\n"
            "- Automatically attaches serverconfig_changes.xml showing all changes\n"
            "- Enhanced changes XML with detailed modification tracking\n"
            "- Shows original vs current values for all properties\n"
            "- Marks properties as MODIFIED or unchanged in XML\n"
            "- Includes change summary (count of modified properties)\n"
            "- Uses localhost:25 SMTP relay for email sending\n"
            "- Pre-filled subject and body text in email\n"
            "- Background thread prevents UI freezing during send\n"
            "- Helpful error messages if SMTP relay not available\n\n"
            "v1.1.5\n"
            "- PATCH: Clear button now matches Previous/Next button size and spacing\n"
            "- Font size adjusted from 11 to 10 for consistency\n"
            "- Added width parameter for uniform button dimensions\n\n"
            "v1.1.4\n"
            "- PATCH: Removed header line from Change Log display\n"
            "- Change Log now starts directly with version information\n"
            "- Cleaner, more concise changelog presentation\n\n"
            
            "v1.1.3\n"
            "- PATCH: Change Log window now scrollable with improved layout\n"
            "- Change Log dialog now uses custom scrollable text window\n"
            "- Window is wider (700px) and shorter (400px) for better viewing\n"
            "- Added scrollbar for long changelog navigation\n\n"
            
            "v1.1.2\n"
            "- PATCH: Fixed window centering on different monitor resolutions\n"
            "- Window now appears dead center regardless of screen size\n\n"
            
            "v1.1.1\n"
            "- PATCH: Window now launches centered on screen\n"
            "- Added automatic screen center positioning\n\n"
            
            "v1.1.0\n"
            "- MINOR: Global cross-tab search with Previous/Next navigation\n"
            "- Added search result counter (X of Y)\n"
            "- Implemented result highlighting with pale yellow background\n"
            "- Search now works across all 10 tabs simultaneously\n"
            "- Added Previous (◀ Prev) and Next (▶ Next) navigation buttons\n"
            "- Search uses whole-word matching for descriptions\n"
            "- Exact substring matching for property names\n"
            "- Auto-switches to correct tab when result is selected\n"
            "- Auto-scrolls to center highlighted result\n"
            "- Reduced window height to 750px to fit on screen\n"
            "- Reduced Save/Reload buttons by 25%\n"
            "- Added ? icon next to property names for tooltips\n"
            "- Tooltips now display exact XML comments from serverconfig.xml\n"
            "- Fixed tooltip text to show actual XML comments (not paraphrased)\n\n"
            
            "v1.0.0\n"
            "- MAJOR: Initial release\n"
            "- 10 organized property tabs (General, World, Difficulty, Rules, etc.)\n"
            "- Real-time search and filter functionality\n"
            "- 98 properties with descriptions mapped to tabs\n"
            "- XML comment extraction for tooltip descriptions\n"
            "- Automatic XML file repair (UTF-8 BOM, UTF-16 handling)\n"
            "- Safe file handling with backup creation on save\n"
            "- Blue header (#007acc) with application title\n"
            "- Menu bar with File (Save, Reload, Open, Exit) and Help (About)\n"
            "- Bug report button (🐛) with debug info copy to clipboard\n"
            "- Search bar with 🔍 icon and Clear button\n"
            "- Scrollable frames with mousewheel support\n"
            "- Hover tooltips with 500ms delay\n"
            "- Keyboard shortcuts: Ctrl+S (Save), Ctrl+R (Reload)\n"
            "- Status bar showing file info and property count\n"
            "- Footer with version information\n"
            "- Clam theme with Segoe UI fonts\n"
            "- Dirty state tracking with unsaved changes warning\n"
            "- 1200x750px window, resizable with minimum size constraints"
        )
        
        text_widget.insert("1.0", changelog)
        text_widget.config(state="disabled")  # Make read-only
        
        # Center changelog window
        changelog_window.transient(self.root)
        changelog_window.grab_set()
    
    def _show_bug_report_dialog(self):
        """Show bug report dialog with email submission."""
        bug_window = tk.Toplevel(self.root)
        bug_window.title("Report a Bug")
        bug_window.geometry("600x500")
        bug_window.minsize(500, 400)
        bug_window.transient(self.root)
        bug_window.grab_set()
        
        # Title label
        title_label = tk.Label(
            bug_window,
            text="Report a Bug",
            font=("Segoe UI", 14, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        title_label.pack(padx=15, pady=(15, 10))
        
        # Subject line
        subject_frame = tk.Frame(bug_window, bg="#f0f0f0")
        subject_frame.pack(fill="x", padx=15, pady=5)
        
        tk.Label(
            subject_frame,
            text="Subject:",
            bg="#f0f0f0",
            fg="#333333",
            font=("Segoe UI", 10)
        ).pack(side="left")
        
        subject_var = tk.StringVar()
        subject_entry = tk.Entry(
            subject_frame,
            textvariable=subject_var,
            font=("Segoe UI", 10),
            relief="solid",
            borderwidth=1
        )
        subject_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Body text
        body_frame = tk.Frame(bug_window, bg="#f0f0f0")
        body_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        tk.Label(
            body_frame,
            text="Description & Notes:",
            bg="#f0f0f0",
            fg="#333333",
            font=("Segoe UI", 10)
        ).pack(anchor="w")
        
        body_text = tk.Text(
            body_frame,
            font=("Segoe UI", 9),
            relief="solid",
            borderwidth=1,
            bg="white",
            fg="#000000",
            height=12
        )
        body_text.pack(fill="both", expand=True, pady=(5, 0))
        
        # Error info frame
        error_frame = tk.LabelFrame(
            bug_window,
            text="Current Errors/Status",
            bg="#f0f0f0",
            fg="#333333",
            font=("Segoe UI", 9)
        )
        error_frame.pack(fill="x", padx=15, pady=(5, 10))
        
        error_label = tk.Label(
            error_frame,
            text=self.status_var.get() or "No errors",
            bg="#f0f0f0",
            fg="#666666",
            font=("Segoe UI", 9),
            wraplength=550,
            justify="left"
        )
        error_label.pack(padx=10, pady=10, anchor="w")
        
        # Send button
        def send_bug_report():
            subject = subject_var.get().strip()
            body = body_text.get("1.0", "end-1c").strip()
            
            if not subject:
                messagebox.showwarning("Missing Subject", "Please enter a subject line.")
                return
            
            if not body:
                messagebox.showwarning("Missing Description", "Please enter a description.")
                return
            
            messagebox.showinfo(
                "Sending Bug Report",
                "Preparing bug report with attachments...\n\nThis may take a moment."
            )
            
            # Send in background thread to avoid freezing UI
            def send_thread():
                try:
                    self._send_bug_report_with_attachments(subject, body, error_label.cget("text"))
                    self.root.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Success",
                            "Bug report sent successfully!\n\n"
                            "Thank you for helping improve the application."
                        )
                    )
                    self.root.after(0, bug_window.destroy)
                except Exception as e:
                    self.root.after(
                        0,
                        lambda: messagebox.showerror(
                            "Send Error",
                            f"Failed to send bug report:\n\n{str(e)}"
                        )
                    )
            
            thread = threading.Thread(target=send_thread, daemon=True)
            thread.start()
        
        button_frame = tk.Frame(bug_window, bg="#f0f0f0")
        button_frame.pack(fill="x", padx=15, pady=10)
        
        send_btn = tk.Button(
            button_frame,
            text="Send Bug Report",
            font=("Segoe UI", 10),
            bg="#007acc",
            fg="white",
            activebackground="#005f9e",
            activeforeground="white",
            relief="raised",
            padx=20,
            pady=6,
            command=send_bug_report
        )
        send_btn.pack(side="right")
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            activebackground="#d0d0d0",
            relief="raised",
            padx=20,
            pady=6,
            command=bug_window.destroy
        )
        cancel_btn.pack(side="right", padx=(0, 10))
    
    def _create_changes_xml(self) -> str:
        """Create XML file with current editor settings and changes.
        
        Returns the XML content as a string with detailed change tracking.
        """
        root = ET.Element("serverconfig_changes")
        root.set("timestamp", datetime.now().isoformat())
        root.set("editor_version", self.VERSION)
        root.set("original_file", os.path.basename(self.config_file))
        
        # Summary section
        summary = ET.SubElement(root, "summary")
        changed_count = 0
        
        # Add current values from property_vars
        for prop_name, var in self.property_vars.items():
            prop_elem = ET.SubElement(root, "property")
            prop_elem.set("name", prop_name)
            
            current_value = var.get()
            
            # Get original value for comparison
            original_elem = self.properties_map.get(prop_name)
            original_value = ""
            if original_elem is not None:
                original_value = original_elem.get("value", "")
            
            # Add original value
            prop_elem.set("original", original_value)
            
            # Add current value
            prop_elem.set("current", current_value)
            
            # Mark if changed and add status
            is_changed = current_value != original_value
            if is_changed:
                prop_elem.set("status", "MODIFIED")
                changed_count += 1
            else:
                prop_elem.set("status", "unchanged")
        
        # Add summary info
        summary_text = ET.SubElement(summary, "changes_count")
        summary_text.text = str(changed_count)
        
        summary_date = ET.SubElement(summary, "timestamp")
        summary_date.text = datetime.now().isoformat()
        
        summary_version = ET.SubElement(summary, "editor_version")
        summary_version.text = self.VERSION
        
        # Format as pretty XML
        xml_str = ET.tostring(root, encoding="unicode")
        
        # Add XML declaration
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str
    
    def _send_bug_report_with_attachments(self, subject: str, body: str, error_info: str):
        """Send bug report email with attachments via SMTP.
        Falls back to manual file creation + email client if SMTP unavailable.
        
        Args:
            subject: Email subject line
            body: User-provided description
            error_info: Current error/status information
        """
        # Build email body
        email_body = f"""Bug Report from 7 Days to Die Server Config Editor

Version: {self.VERSION}
Timestamp: {datetime.now().isoformat()}
Platform: {platform.platform()}
Python: {platform.python_version()}

--- USER DESCRIPTION ---
{body}

--- CURRENT STATUS ---
{error_info}

--- EDITOR STATE ---
Configuration File: {self.config_file}
Total Properties: {len(self.property_vars)}
Unsaved Changes: {"Yes" if self.is_dirty else "No"}
"""
        
        # Create email message
        msg = MIMEMultipart()
        msg["From"] = "7d2d-server-config-editor@localhost"
        msg["To"] = "cfranz73@gmail.com"
        msg["Subject"] = f"[Bug Report] {subject}"
        msg.attach(MIMEText(email_body, "plain"))
        
        # Attach original serverconfig.xml
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename=serverconfig.xml"
                    )
                    msg.attach(part)
            except Exception as e:
                raise Exception(f"Failed to attach serverconfig.xml: {str(e)}")
        
        # Create and attach serverconfig_changes.xml
        changes_xml = self._create_changes_xml()
        try:
            changes_part = MIMEBase("application", "octet-stream")
            changes_part.set_payload(changes_xml.encode("utf-8"))
            encoders.encode_base64(changes_part)
            changes_part.add_header(
                "Content-Disposition",
                "attachment; filename=serverconfig_changes.xml"
            )
            msg.attach(changes_part)
        except Exception as e:
            raise Exception(f"Failed to attach serverconfig_changes.xml: {str(e)}")
        
        # Try to send via SMTP relay
        smtp_sent = False
        smtp_error = None
        
        try:
            # Try localhost SMTP first (works if running behind corporate/ISP relay)
            server = smtplib.SMTP("localhost", 25, timeout=10)
            try:
                server.sendmail(
                    "7d2d-server-config-editor@localhost",
                    "cfranz73@gmail.com",
                    msg.as_string()
                )
                smtp_sent = True
            finally:
                server.quit()
        except Exception as e:
            smtp_error = str(e)
        
        # If SMTP failed, use fallback: save files and open email client
        if not smtp_sent:
            try:
                self._fallback_email_with_files(subject, body, error_info, email_body, changes_xml)
            except Exception as fallback_error:
                raise Exception(
                    f"Could not send via SMTP and fallback failed:\n\n"
                    f"SMTP Error: {smtp_error}\n\n"
                    f"Fallback Error: {str(fallback_error)}"
                )
    
    def _fallback_email_with_files(self, subject: str, body: str, error_info: str, email_body: str, changes_xml: str):
        """Fallback: Save files to home directory and open default email client.
        
        Args:
            subject: Email subject line
            body: User description
            error_info: Current error/status
            email_body: Full email body text
            changes_xml: XML content of changes
        """
        home_dir = os.path.expanduser("~")
        desktop_dir = os.path.join(home_dir, "Desktop")
        report_dir = os.path.join(desktop_dir, "7D2D_BugReport")
        
        # Create bug report directory
        try:
            os.makedirs(report_dir, exist_ok=True)
        except Exception as e:
            # Fallback to home directory
            report_dir = home_dir
        
        # Save original serverconfig.xml
        original_path = os.path.join(report_dir, "serverconfig.xml")
        if os.path.exists(self.config_file):
            try:
                shutil.copy2(self.config_file, original_path)
            except Exception as e:
                raise Exception(f"Failed to save serverconfig.xml: {str(e)}")
        
        # Save serverconfig_changes.xml
        changes_path = os.path.join(report_dir, "serverconfig_changes.xml")
        try:
            with open(changes_path, 'w', encoding='utf-8') as f:
                f.write(changes_xml)
        except Exception as e:
            raise Exception(f"Failed to save serverconfig_changes.xml: {str(e)}")
        
        # Save email body as text file
        email_path = os.path.join(report_dir, "BUG_REPORT_INFO.txt")
        try:
            with open(email_path, 'w', encoding='utf-8') as f:
                f.write(f"Subject: [Bug Report] {subject}\n\n")
                f.write(email_body)
                f.write("\n\nUser Notes:\n")
                f.write(body)
        except Exception as e:
            raise Exception(f"Failed to save email info: {str(e)}")
        
        # Open file explorer to the directory
        try:
            if sys.platform == "win32":
                os.startfile(report_dir)
            elif sys.platform == "darwin":
                subprocess.run(["open", report_dir], check=True)
            else:
                subprocess.run(["xdg-open", report_dir], check=True)
        except Exception:
            pass  # Silent fail on file explorer open
        
        # Now open email client
        mailto_subject = f"[Bug Report] {subject}"
        email_message = f"""Please attach the following files from the folder that just opened:
- serverconfig.xml
- serverconfig_changes.xml

Then paste this information in your email body:

{email_body}

User Notes:
{body}"""
        
        encoded_subject = quote(mailto_subject)
        encoded_body = quote(email_message)
        
        mailto_url = f"mailto:cfranz73@gmail.com?subject={encoded_subject}&body={encoded_body}"
        
        try:
            if sys.platform == "win32":
                os.startfile(mailto_url)
            elif sys.platform == "darwin":
                subprocess.run(["open", mailto_url], check=True)
            else:
                webbrowser.open(mailto_url)
        except Exception as e:
            # If email client fails, provide manual instructions
            raise Exception(
                f"Files saved to: {report_dir}\n\n"
                f"To complete the bug report:\n"
                f"1. Open your email client\n"
                f"2. Create new email to: cfranz73@gmail.com\n"
                f"3. Subject: [Bug Report] {subject}\n"
                f"4. Attach the two XML files from the folder\n"
                f"5. Include the information from BUG_REPORT_INFO.txt\n\n"
                f"Email client error: {str(e)}"
            )
    
    def _open_bug_report_email(self, subject: str, body: str, error_info: str):
        """Open default email client with bug report.
        
        Args:
            subject: Email subject line
            body: User-provided description
            error_info: Current error/status information
        """
        # Build email body
        email_body = f"""Bug Report from 7 Days to Die Server Config Editor

Version: {self.VERSION}
Timestamp: {datetime.now().isoformat()}
Platform: {platform.platform()}
Python: {platform.python_version()}

--- USER DESCRIPTION ---
{body}

--- CURRENT STATUS ---
{error_info}

--- EDITOR STATE ---
Configuration File: {self.config_file}
Total Properties: {len(self.property_vars)}
Unsaved Changes: {"Yes" if self.is_dirty else "No"}

Attachments needed:
- serverconfig.xml: Original configuration file
- serverconfig_changes.xml: Current editor settings with changes marked

Files are located in:
{os.path.expanduser("~")}
"""
        
        # Create files in home directory
        home_dir = os.path.expanduser("~")
        
        # Save original serverconfig.xml
        original_path = os.path.join(home_dir, "serverconfig.xml")
        if os.path.exists(self.config_file):
            try:
                shutil.copy2(self.config_file, original_path)
            except Exception as e:
                raise Exception(f"Failed to copy serverconfig.xml: {str(e)}")
        
        # Save serverconfig_changes.xml
        changes_path = os.path.join(home_dir, "serverconfig_changes.xml")
        changes_xml = self._create_changes_xml()
        try:
            with open(changes_path, 'w', encoding='utf-8') as f:
                f.write(changes_xml)
        except Exception as e:
            raise Exception(f"Failed to create serverconfig_changes.xml: {str(e)}")
        
        # Build mailto URL
        mailto_subject = f"[Bug Report] {subject}"
        
        # URL encode the subject and body
        encoded_subject = quote(mailto_subject)
        encoded_body = quote(email_body)
        
        mailto_url = f"mailto:cfranz73@gmail.com?subject={encoded_subject}&body={encoded_body}"
        
        # Open default email client
        try:
            if sys.platform == "win32":
                # Windows: Use os.startfile
                os.startfile(mailto_url)
            elif sys.platform == "darwin":
                # macOS: Use open command
                subprocess.run(["open", mailto_url], check=True)
            else:
                # Linux and others: Use webbrowser
                webbrowser.open(mailto_url)
        except Exception as e:
            # If opening email client fails, show manual instructions
            files_info = f"Attachment files created at:\n{original_path}\n{changes_path}"
            raise Exception(
                f"Could not open your default email client.\n\n"
                f"Please manually create an email to: cfranz73@gmail.com\n"
                f"Subject: {mailto_subject}\n\n"
                f"{files_info}\n\n"
                f"Then attach the two XML files and send.\n\n"
                f"Original error: {str(e)}"
            )
    
    def _on_window_close(self):
        """Handle window close event."""
        if self.is_dirty:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Save before closing?"
            )
            if response is None:
                return
            elif response:
                self.save_configuration()
        
        self.root.destroy()


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def main():
    """Main application entry point."""
    root = tk.Tk()
    app = ServerConfigEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()

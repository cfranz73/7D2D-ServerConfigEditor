#!/usr/bin/env python3
# type: ignore
"""
7 Days to Die Server Configuration Editor™
A comprehensive Tkinter GUI for editing serverconfig.xml with meticulous attention to design details.

Version: 1.1.1
Author: Dance Monkey Dance Studios™
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
from PIL import Image, ImageTk


# ============================================================================
# RESOURCE PATH HELPER (PyInstaller Support)
# ============================================================================

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS  # PyInstaller temp dir
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ============================================================================
# CORE CONFIGURATION
# ============================================================================

DEFAULT_CONFIG_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\7 Days to Die Dedicated Server\serverconfig.xml"
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".7d2d_config_editor_settings.json")

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
    "ServerName": "Whatever you want the name of the server to be.",
    "ServerDescription": "Whatever you want the server description to be, will be shown in the server browser.",
    "ServerWebsiteURL": "Website URL for the server, will be shown in the server browser as a clickable link",
    "ServerPassword": "Password to gain entry to the server",
    "ServerLoginConfirmationText": "If set the user will see the message during joining the server and has to confirm it before continuing. For more complex changes to this window you can change the \"serverjoinrulesdialog\" window in XUi",
    "Region": "The region this server is in. Values: NorthAmericaEast, NorthAmericaWest, CentralAmerica, SouthAmerica, Europe, Russia, Asia, MiddleEast, Africa, Oceania",
    "Language": "Primary language for players on this server. Values: Use any language name that you would users expect to search for. Should be the English name of the language, e.g. not \"Deutsch\" but \"German\"",
    "ServerPort": "Port you want the server to listen on. Keep it in the ranges 26900 to 26905 or 27015 to 27020 if you want PCs on the same LAN to find it as a LAN server.",
    "ServerVisibility": "Visibility of this server: 2 = public, 1 = only shown to friends, 0 = not listed. As you are never friend of a dedicated server setting this to \"1\" will only work when the first player connects manually by IP.",
    "ServerDisabledNetworkProtocols": "Networking protocols that should not be used. Separated by comma. Possible values: LiteNetLib, SteamNetworking. Dedicated servers should disable SteamNetworking if there is no NAT router in between your users and the server or when port-forwarding is set up correctly",
    "ServerMaxWorldTransferSpeedKiBs": "Maximum (!) speed in kiB/s the world is transferred at to a client on first connect if it does not have the world yet. Maximum is about 1300 kiB/s, even if you set a higher value.",
    "ServerMaxPlayerCount": "Maximum Concurrent Players",
    "ServerReservedSlots": "Out of the MaxPlayerCount this many slots can only be used by players with a specific permission level",
    "ServerReservedSlotsPermission": "Required permission level to use reserved slots above",
    "ServerAdminSlots": "This many admins can still join even if the server has reached MaxPlayerCount",
    "ServerAdminSlotsPermission": "Required permission level to use the admin slots above",
    "WebDashboardEnabled": "Enable/disable the web dashboard",
    "WebDashboardPort": "Port of the web dashboard",
    "WebDashboardUrl": "External URL to the web dashboard if not just using the public IP of the server, e.g. if the web dashboard is behind a reverse proxy. Needs to be the full URL, like \"https://domainOfReverseProxy.tld:1234/\". Can be left empty if directly using the public IP and dashboard port",
    "EnableMapRendering": "Enable/disable rendering of the map to tile images while exploring it. This is used e.g. by the web dashboard to display a view of the map.",
    "TelnetEnabled": "Enable/Disable the telnet",
    "TelnetPort": "Port of the telnet server",
    "TelnetPassword": "Password to gain entry to telnet interface. If no password is set the server will only listen on the local loopback interface",
    "TelnetFailedLoginLimit": "After this many wrong passwords from a single remote client the client will be blocked from connecting to the Telnet interface",
    "TelnetFailedLoginsBlocktime": "How long will the block persist (in seconds)",
    "TerminalWindowEnabled": "Show a terminal window for log output / command input (Windows only)",
    "AdminFileName": "Server admin file name. Path relative to UserDataFolder/Saves",
    "ServerAllowCrossplay": "Enables/Disables crossplay, crossplay servers will only be found in searches and joinable if sanctions are not ignored, and have a default or fewer player slot count",
    "EACEnabled": "Enables/Disables EasyAntiCheat",
    "IgnoreEOSSanctions": "Ignore EOS sanctions when allowing players to join",
    "HideCommandExecutionLog": "Hide logging of command execution. 0 = show everything, 1 = hide only from Telnet/ControlPanel, 2 = also hide from remote game clients, 3 = hide everything",
    "MaxUncoveredMapChunksPerPlayer": "Override how many chunks can be uncovered on the in-game map by each player. Resulting max map file size limit per player is (x * 512 Bytes), uncovered area is (x * 256 m²). Default 131072 means max 32 km² can be uncovered at any time",
    "PersistentPlayerProfiles": "If disabled a player can join with any selected profile. If true they will join with the last profile they joined with",
    "MaxChunkAge": "The number of in-game days which must pass since visiting a chunk before it will reset to its original state if not revisited or protected (e.g. by a land claim or bedroll being in close proximity).",
    "SaveDataLimit": "The maximum disk space allowance for each saved game in megabytes (MB). Saved chunks may be forcibly reset to their original states to free up space when this limit is reached. Negative values disable the limit.",
    "GameWorld": "\"RWG\" (see WorldGenSeed and WorldGenSize options below) or any already existing world name in the Worlds folder (currently shipping with e.g. \"Navezgane\", \"Pregen06k01\", \"Pregen06k02\", \"Pregen08k01\", \"Pregen08k02\", ...)",
    "WorldGenSeed": "If RWG this is the seed for the generation of the new world. If a world with the resulting name already exists it will simply load it",
    "WorldGenSize": "6144, 8192, 10240 If GameWorld = RWG, this controls the width and height of the created world. Officially supported sizes are between 6144 and 10240 and must be a multiple of 2048, e.g. 6144, 8192, 10240.",
    "GameName": "Whatever you want the game name to be (allowed [A-Za-z0-9_-. ]). This affects the save game name as well as the seed used when placing decoration (trees etc.) in the world. It does not control the generic layout of the world if creating an RWG world",
    "GameMode": "GameModeSurvival",
    "GameDifficulty": "0 - 5, 0=easiest, 5=hardest",
    "BlockDamagePlayer": "How much damage do players to blocks (percentage in whole numbers)",
    "BlockDamageAI": "How much damage do AIs to blocks (percentage in whole numbers)",
    "BlockDamageAIBM": "How much damage do AIs during blood moons to blocks (percentage in whole numbers)",
    "XPMultiplier": "XP gain multiplier (percentage in whole numbers)",
    "PlayerSafeZoneLevel": "If a player is less or equal this level he will create a safe zone (no enemies) when spawned",
    "PlayerSafeZoneHours": "Hours in world time this safe zone exists",
    "BuildCreate": "cheat mode on/off",
    "DayNightLength": "real time minutes per in game day: 60 minutes",
    "DayLightLength": "in game hours the sun shines per day: 18 hours day light per in game day",
    "BiomeProgression": "Enables biome hazards and loot stage caps to promote biome progression. Loot stage caps are increased by completing biome challenges.",
    "StormFreq": "Adjusts the frequency of storms. 0% turns them off. Vanilla values: 0, 50, 100, 150, 200, 300, 400, 500",
    "DeathPenalty": "Penalty after dying. 0 = Nothing. 1 = Default: Classic XP Penalty. 2 = Injured: You keep most of your de-buffs. Food and Water is set to 50% on respawn. 3 = Permanent Death: Your character is completely reset. You will respawn with a fresh start within the saved game.",
    "DropOnDeath": "0 = nothing, 1 = everything, 2 = toolbelt only, 3 = backpack only, 4 = delete all",
    "DropOnQuit": "0 = nothing, 1 = everything, 2 = toolbelt only, 3 = backpack only",
    "BedrollDeadZoneSize": "Size (box \"radius\", so a box with 2 times the given value for each side's length) of bedroll dead zone, no zombies will spawn inside this area, and any cleared sleeper volumes that touch a bedroll deadzone will not spawn after they've been cleared.",
    "BedrollExpiryTime": "Number of real world days a bedroll stays active after owner was last online",
    "AllowSpawnNearFriend": "Can new players joining the server for the first time select to join near any friend playing at the same time? 0 = Disabled, 1 = Always, 2 = Only near friends in forest biome",
    "CameraRestrictionMode": "0 = Players can freely swap between first and third person camera modes, 1 = Restricted to first person, 2 = Restricted to third person",
    "JarRefund": "0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100% The empty jar refund percentage after consuming an item.",
    "MaxSpawnedZombies": "This setting covers the entire map. There can only be this many zombies on the entire map at one time. Changing this setting has a huge impact on performance.",
    "MaxSpawnedAnimals": "If your server has a large number of players you can increase this limit to add more wildlife. Animals don't consume as much CPU as zombies. NOTE: That this doesn't cause more animals to spawn arbitrarily: The biome spawning system only spawns a certain number of animals in a given area, but if you have lots of players that are all spread out then you may be hitting the limit and can increase it.",
    "ServerMaxAllowedViewDistance": "Max view distance a client may request (6 - 12). High impact on memory usage and performance.",
    "MaxQueuedMeshLayers": "Maximum amount of Chunk mesh layers that can be enqueued during mesh generation. Reducing this will improve memory usage but may increase Chunk generation time",
    "EnemySpawnMode": "Enable/Disable enemy spawning",
    "EnemyDifficulty": "0 = Normal, 1 = Feral",
    "ZombieFeralSense": "0-3 (Off, Day, Night, All)",
    "ZombieMove": "0-4 (walk, jog, run, sprint, nightmare)",
    "ZombieMoveNight": "0-4 (walk, jog, run, sprint, nightmare)",
    "ZombieFeralMove": "0-4 (walk, jog, run, sprint, nightmare)",
    "ZombieBMMove": "0-4 (walk, jog, run, sprint, nightmare)",
    "AISmellMode": "0-5 (off, walk, jog, run, sprint, nightmare)",
    "BloodMoonFrequency": "What frequency (in days) should a blood moon take place. Set to \"0\" for no blood moons",
    "BloodMoonRange": "How many days can the actual blood moon day randomly deviate from the above setting. Setting this to 0 makes blood moons happen exactly each Nth day as specified in BloodMoonFrequency",
    "BloodMoonWarning": "The Hour number that the red day number begins on a blood moon day. Setting this to -1 makes the red never show.",
    "BloodMoonEnemyCount": "This is the number of zombies that can be alive (spawned at the same time) at any time PER PLAYER during a blood moon horde, however, MaxSpawnedZombies overrides this number in multiplayer games. Also note that your game stage sets the max number of zombies PER PARTY. Low game stage values can result in lower number of zombies than the BloodMoonEnemyCount setting. Changing this setting has a huge impact on performance.",
    "LootAbundance": "Percentage in whole numbers",
    "LootRespawnDays": "Days in whole numbers",
    "AirDropFrequency": "How often airdrop occur in game-hours, 0 == never",
    "AirDropMarker": "Sets if a marker is added to map/compass for air drops.",
    "PartySharedKillRange": "The distance you must be within to receive party shared kill XP and quest party kill objective credit.",
    "PlayerKillingMode": "Player Killing Settings (0 = No Killing, 1 = Kill Allies Only, 2 = Kill Strangers Only, 3 = Kill Everyone)",
    "LandClaimCount": "Maximum allowed land claims per player.",
    "LandClaimSize": "Size in blocks that is protected by a keystone",
    "LandClaimDeadZone": "Keystones must be this many blocks apart (unless you are friends with the other player)",
    "LandClaimExpiryTime": "The number of real world days a player can be offline before their claims expire and are no longer protected",
    "LandClaimDecayMode": "Controls how offline players land claims decay. 0=Slow (Linear) , 1=Fast (Exponential), 2=None (Full protection until claim is expired).",
    "LandClaimOnlineDurabilityModifier": "How much protected claim area block hardness is increased when a player is online. 0 means infinite (no damage will ever be taken). Default is 4x",
    "LandClaimOfflineDurabilityModifier": "How much protected claim area block hardness is increased when a player is offline. 0 means infinite (no damage will ever be taken). Default is 4x",
    "LandClaimOfflineDelay": "The number of minutes after a player logs out that the land claim area hardness transitions from online to offline. Default is 0",
    "DynamicMeshEnabled": "Is Dynamic Mesh system enabled",
    "DynamicMeshLandClaimOnly": "Is Dynamic Mesh system only active in player LCB areas",
    "DynamicMeshLandClaimBuffer": "Dynamic Mesh LCB chunk radius",
    "DynamicMeshMaxItemCache": "How many items can be processed concurrently, higher values use more RAM",
    "TwitchServerPermission": "Required permission level to use twitch integration on the server",
    "TwitchBloodMoonAllowed": "If the server allows twitch actions during a blood moon. This could cause server lag with extra zombies being spawned during blood moon.",
    "QuestProgressionDailyLimit": "Limits the number of quests that contribute to quest tier progression a player can complete each day. Quests after the limit can still be completed for rewards.",
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
    
    VERSION = "1.2.6"
    
    def __init__(self, root):
        self.root = root
        self.root.title("7 Days to Die Server Config Editor™")
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)
        self.root.configure(bg="#f0f0f0")
        
        # Set window icon with multiple methods for best compatibility
        try:
            icon_path = resource_path('icon.ico')
            
            # Method 1: iconbitmap (for window border)
            self.root.iconbitmap(default=icon_path)
            
            # Method 2: iconphoto (for taskbar on some systems)
            try:
                # Load icon and convert to PhotoImage
                icon_img = Image.open(icon_path)
                # Use the largest size from the ico (usually 256x256 or 128x128)
                icon_photo = ImageTk.PhotoImage(icon_img)
                # Store reference to prevent garbage collection
                self.root.icon_photo = icon_photo
                self.root.iconphoto(True, icon_photo)
            except Exception as e:
                print(f"Debug: iconphoto failed: {e}")
                
            # Method 3: Set window attributes for Windows
            if platform.system() == 'Windows':
                try:
                    # Force update the window
                    self.root.update_idletasks()
                except:
                    pass
        except Exception as e:
            print(f"Debug: Icon loading failed: {e}")
        
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
        
        # Load saved settings
        self._load_settings()
        
        # Load tooltip icon image
        self.tooltip_icon_photo = None
        self._load_tooltip_icon()
        
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
    
    def _load_tooltip_icon(self):
        """Load and scale the tooltip icon image."""
        try:
            tooltip_icon_path = resource_path(os.path.join("Logos and Images", "tooltip-icon.png"))
            
            if os.path.exists(tooltip_icon_path):
                # Load the image
                img = Image.open(tooltip_icon_path)
                # Scale to 16x16 pixels to fit nicely with property box
                img_resized = img.resize((16, 16), Image.Resampling.LANCZOS)
                # Convert to PhotoImage
                self.tooltip_icon_photo = ImageTk.PhotoImage(img_resized)
            else:
                print(f"Debug: Tooltip icon not found at {tooltip_icon_path}")
        except Exception as e:
            print(f"Debug: Failed to load tooltip icon: {e}")
    
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
        
        # Menu bar
        self._create_menubar()
        
        # Search bar
        self._create_search_bar()
        
        # Notebook with tabs
        self._create_notebook()
        
        # Save/Reload buttons and bug button
        self._create_action_buttons()
        
        # Status bar
        self._create_status_bar()
        
        # Footer
        self._create_footer()
    
    def _create_header(self):
        """Create the blue header banner with logo."""
        header = tk.Frame(self.root, bg="#007acc", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        # Load and display left logo
        left_logo_url = "https://i.imgur.com/TlzRI3x.jpeg"
        left_logo_path = os.path.join(os.path.expanduser("~"), ".7d2d_config_editor_left_logo.jpeg")
        
        # Download left logo if not cached
        try:
            if not os.path.exists(left_logo_path):
                import urllib.request
                import socket
                socket.setdefaulttimeout(10)
                
                # Create request with User-Agent to bypass imgur blocks
                req = urllib.request.Request(
                    left_logo_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                with urllib.request.urlopen(req) as response:
                    with open(left_logo_path, 'wb') as out_file:
                        out_file.write(response.read())
        except Exception as e:
            print(f"Debug: Left logo download failed: {e}")
        
        if os.path.exists(left_logo_path) and os.path.getsize(left_logo_path) > 0:
            try:
                # Load left logo image and resize
                img = Image.open(left_logo_path)
                header_height = 70
                max_width = 150  # Prevent logo from being too wide
                aspect_ratio = img.width / img.height
                new_height = header_height - 10
                new_width = int(new_height * aspect_ratio)
                # Constrain width to max_width
                if new_width > max_width:
                    new_width = max_width
                    new_height = int(new_width / aspect_ratio)
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.left_header_photo = ImageTk.PhotoImage(img_resized)
                
                # Create label for left logo
                left_logo_label = tk.Label(
                    header,
                    image=self.left_header_photo,
                    bg="#007acc",
                    borderwidth=0
                )
                left_logo_label.pack(side="left", padx=20, pady=5)
            except Exception as e:
                print(f"Debug: Left logo display failed: {e}")
        
        title_label = tk.Label(
            header,
            text="7 Days to Die Server Config Editor™",
            font=("Segoe UI", 23, "bold"),
            bg="#007acc",
            fg="white"
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        # Load and display right logo (Mayhem logo)
        logo_url = "https://i.imgur.com/iQaAn2V.png"
        logo_path = os.path.join(os.path.expanduser("~"), ".7d2d_config_editor_logo.png")
        
        # Download logo if not cached
        try:
            if not os.path.exists(logo_path):
                import urllib.request
                import socket
                socket.setdefaulttimeout(10)
                
                # Create request with User-Agent to bypass imgur blocks
                req = urllib.request.Request(
                    logo_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                with urllib.request.urlopen(req) as response:
                    with open(logo_path, 'wb') as out_file:
                        out_file.write(response.read())
        except Exception as e:
            # Logo download failed, continue without it
            print(f"Debug: Logo download failed: {e}")
        
        if os.path.exists(logo_path) and os.path.getsize(logo_path) > 0:
            try:
                # Load image and resize to fit header height (70px) while maintaining aspect ratio
                img = Image.open(logo_path)
                header_height = 70
                # Calculate width to maintain aspect ratio
                aspect_ratio = img.width / img.height
                new_height = header_height - 10  # Leave 5px padding top and bottom
                new_width = int(new_height * aspect_ratio)
                # Resize image with high-quality resampling
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                # Convert to PhotoImage for Tkinter
                self.header_photo = ImageTk.PhotoImage(img_resized)
                # Create label with image
                logo_label = tk.Label(
                    header,
                    image=self.header_photo,
                    bg="#007acc",
                    borderwidth=0
                )
                logo_label.pack(side="right", padx=20, pady=5)
            except Exception as e:
                # If logo fails to load, silently continue without logo
                print(f"Debug: Logo display failed: {e}")
    
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
            label="Settings...",
            command=self._show_settings_dialog
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
        icon_label = tk.Label(search_frame, text="🔍", bg="#f0f0f0", font=("Segoe UI", 10))
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
        
        # Add placeholder text
        placeholder_text = "Search for specific Properties or keywords in Descriptions"
        placeholder_color = "#808080"  # 50% grey
        
        def on_focus_in(event):
            if self.search_var.get() == placeholder_text:
                search_entry.delete(0, tk.END)
                search_entry.config(fg="#000000")
                search_entry.config(font=("Segoe UI", 10))
        
        def on_focus_out(event):
            if self.search_var.get() == "":
                search_entry.insert(0, placeholder_text)
                search_entry.config(fg=placeholder_color)
                search_entry.config(font=("Segoe UI", 10, "italic"))
        
        # Insert placeholder text initially
        search_entry.insert(0, placeholder_text)
        search_entry.config(fg=placeholder_color)
        search_entry.config(font=("Segoe UI", 10, "italic"))
        
        # Bind focus events
        search_entry.bind("<FocusIn>", on_focus_in)
        search_entry.bind("<FocusOut>", on_focus_out)
        
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
        """Create Save, Reload, and Debug buttons."""
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(fill="x", padx=15, pady=12)
        
        # Left side - Bug report button
        left_container = tk.Frame(button_frame, bg="#f0f0f0")
        left_container.pack(side="left")
        
        debug_btn = tk.Button(
            left_container,
            text="🐛",
            font=("Arial", 13),
            width=5,
            height=1,
            bg="#e0e0e0",
            activebackground="#d0d0d0",
            relief="raised",
            command=self._copy_debug_info
        )
        debug_btn.pack(side="left")
        ToolTip(debug_btn, "Copy debug information to clipboard")
        
        # Right side - Save and Reload buttons
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
            text=f"Version {self.VERSION} © 7 Days to Die Server Config Editor™ by Dance Monkey Dance™",
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
        """Populate all tabs with property rows in 2 columns."""
        self.property_vars.clear()
        self.property_rows.clear()
        
        for tab_name, property_names in TAB_DEFINITIONS.items():
            # Get the scrollable frame inside this tab
            scrollable_frame = self.tab_frames[tab_name].scrollable_frame
            
            # Clear existing widgets
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            # Create 2-column layout container
            columns_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
            columns_frame.pack(fill="both", expand=True, padx=8, pady=10)
            
            # Create left and right column frames
            left_column = tk.Frame(columns_frame, bg="#f0f0f0")
            left_column.pack(side="left", fill="both", expand=True, padx=(0, 5))
            
            right_column = tk.Frame(columns_frame, bg="#f0f0f0")
            right_column.pack(side="left", fill="both", expand=True, padx=(5, 0))
            
            # Add property rows to alternating columns
            for idx, prop_name in enumerate(property_names):
                if prop_name in self.properties_map:
                    # Choose column based on index (even = left, odd = right)
                    column = left_column if idx % 2 == 0 else right_column
                    self._add_property_row(column, prop_name, tab_name)
    
    def _add_property_row(self, parent, prop_name: str, tab_name: str = ""):
        """Add a single property row with label and entry (optimized for 2-column layout)."""
        elem = self.properties_map.get(prop_name)
        value = elem.get("value", "") if elem is not None else ""
        
        # Create row frame
        row_frame = tk.Frame(parent, bg="#f0f0f0")
        row_frame.pack(fill="x", padx=0, pady=6)
        
        # Store tab reference on frame
        row_frame._tab_name = tab_name
        row_frame._prop_name = prop_name
        
        # Create label frame to hold property name and ? icon
        label_frame = tk.Frame(row_frame, bg="#f0f0f0")
        label_frame.pack(side="left", padx=(0, 10))
        
        # Get tooltip text from XML comments
        tooltip_text = self.comments.get(prop_name) or PROPERTY_DESCRIPTIONS.get(prop_name, "")
        
        # Add ? icon only if there's a description (BEFORE property name)
        if tooltip_text:
            help_icon = tk.Label(
                label_frame,
                image=self.tooltip_icon_photo,
                bg="#f0f0f0",
                cursor="question_arrow"
            )
            help_icon.pack(side="left", padx=(0, 5))
            
            # Attach tooltip to the ? icon
            ToolTip(help_icon, tooltip_text)
        
        # Property name label (left side, gray text)
        name_label = tk.Label(
            label_frame,
            text=prop_name,
            bg="#f0f0f0",
            fg="#666666",
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
            width=28
        )
        name_label.pack(side="left")
        row_frame._label = name_label
        
        # Entry field (right side, white background)
        var = tk.StringVar(value=value)
        entry = tk.Entry(
            row_frame,
            textvariable=var,
            bg="white",
            fg="#000000",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
            width=22
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        row_frame._entry = entry
        
        # Bind change event
        entry.bind("<KeyRelease>", lambda e: self._mark_dirty())
        
        # Store references
        self.property_vars[prop_name] = var
        self.property_rows[prop_name] = (row_frame, tab_name)
    
    def _global_search(self):
        """Search across all tabs and track all matches - exact substring matching."""
        placeholder_text = "Search for specific Properties or keywords in Descriptions"
        query = self.search_var.get().strip().lower()
        
        # Ignore placeholder text
        if query == placeholder_text.lower():
            query = ""
        
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
            row_frame.pack(fill="x", padx=0, pady=6)
    
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
            "v1.2.6 (Current)\n"
            "- PATCH: PyInstaller executable build support\n"
            "- Added resource_path() helper function for PyInstaller compatibility\n"
            "- Fixed duplicate tk.Tk() instances causing PhotoImage errors\n"
            "- Updated icon.ico and tooltip-icon.png loading to use resource_path()\n"
            "- Fixed Windows taskbar icon display using SetCurrentProcessExplicitAppUserModelID\n"
            "- Added multiple icon setting methods (iconbitmap, iconphoto) for best compatibility\n"
            "- Taskbar icon fix now runs before tk.Tk() window creation\n"
            "- Created build_exe.bat and build_exe.sh automated build scripts\n"
            "- Created BUILD.md with comprehensive build documentation\n"
            "- Created clear_icon_cache.bat utility for Windows icon cache issues\n"
            "- Application now builds as standalone 22MB executable\n"
            "- All resources properly bundled in PyInstaller build\n"
            "- Window title updated with trademark symbol (™)\n\n"
            "v1.2.5\n"
            "- MINOR: Added Settings dialog in File menu\n"
            "- New 'Server Config Location' setting for persistent path storage\n"
            "- Settings saved to user home directory (~/.7d2d_config_editor_settings.json)\n"
            "- Auto-loads saved config path on next application startup\n"
            "- Browse button for easy file selection in settings dialog\n"
            "- PATCH: Updated all property descriptions with official values\n"
            "- All 91 properties now have accurate descriptions from serverconfig.xml\n"
            "- Descriptions include specific values, ranges, and detailed explanations\n"
            "- PATCH: Tooltip icon now displays before property name\n"
            "- Replaced text '?' with tooltip-icon.png image (16x16 pixels)\n"
            "- Professional appearance with scaled PNG icon\n"
            "- Better visual alignment with property input fields\n\n"
            "v1.2.4\n"
            "- (Skipped)\n\n"
            "v1.2.3\n"
            "- PATCH: Added Mayhem Mods logo to blue header bar\n"
            "- Logo displays on far right side of header\n"
            "- Logo height matches header height with preserved aspect ratio\n"
            "- No stretching - maintains original proportions\n"
            "- Graceful fallback if logo file not found\n\n"
            "v1.2.2\n"
            "- PATCH: Columns made 10% wider for better readability\n"
            "- Reduced frame padding from 10px to 8px (20% reduction)\n"
            "- Increased property name width from 25 to 28 characters\n"
            "- Increased entry field width from 20 to 22 characters\n"
            "- Better visibility of longer property names and values\n"
            "- More space for data entry with wider input fields\n\n"
            "v1.2.1\n"
            "- PATCH: Property rows now display in 2-column layout\n"
            "- Cleaner, more compact tab view with side-by-side properties\n"
            "- Even-indexed properties in left column, odd-indexed in right\n"
            "- Reduced font size from 10 to 9 for better fit\n"
            "- Fixed property name width at 25 characters for alignment\n"
            "- Entry field width fixed at 20 characters\n"
            "- Reduced padding and margins for compact layout\n"
            "- Better utilization of screen space\n"
            "- Easier to view more properties at once\n"
            "- Maintains all search and highlighting functionality\n\n"
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
    
    def _load_settings(self):
        """Load saved settings from file."""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if "config_path" in settings and settings["config_path"]:
                        self.config_file = settings["config_path"]
        except Exception as e:
            # Silently fail if settings file is corrupted
            print(f"Debug: Error loading settings: {e}")
    
    def _save_settings(self):
        """Save settings to file."""
        try:
            settings = {
                "config_path": self.config_file
            }
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            messagebox.showerror("Settings Error", f"Failed to save settings:\n{e}")
    
    def _show_settings_dialog(self):
        """Open settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x200")
        settings_window.resizable(False, False)
        
        # Center dialog on parent window
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 250
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 100
        settings_window.geometry(f"+{x}+{y}")
        
        # Make dialog modal
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Main frame with padding
        main_frame = tk.Frame(settings_window, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title label
        title_label = tk.Label(
            main_frame,
            text="Settings",
            bg="#f0f0f0",
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 15))
        
        # Server Config Location label
        config_label = tk.Label(
            main_frame,
            text="Server Config Location:",
            bg="#f0f0f0",
            font=("Segoe UI", 10)
        )
        config_label.pack(anchor="w", pady=(0, 5))
        
        # Frame for entry and button
        config_frame = tk.Frame(main_frame, bg="#f0f0f0")
        config_frame.pack(fill="x", pady=(0, 15))
        
        # Entry field for config path
        config_var = tk.StringVar(value=self.config_file)
        config_entry = tk.Entry(
            config_frame,
            textvariable=config_var,
            bg="white",
            fg="#000000",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
            width=50
        )
        config_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Browse button
        def browse_config():
            filepath = filedialog.askopenfilename(
                title="Select serverconfig.xml",
                filetypes=[("XML Files", "*.xml"), ("All Files", "*.*")],
                initialdir=os.path.dirname(config_var.get()) if os.path.dirname(config_var.get()) else os.path.expanduser("~")
            )
            if filepath:
                config_var.set(filepath)
        
        browse_button = tk.Button(
            config_frame,
            text="Browse...",
            command=browse_config,
            bg="#0078d4",
            fg="white",
            font=("Segoe UI", 9),
            padx=10,
            relief="solid",
            borderwidth=1,
            cursor="hand2"
        )
        browse_button.pack(side="left")
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(fill="x", pady=(10, 0), anchor="e")
        
        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=settings_window.destroy,
            bg="#e0e0e0",
            fg="#000000",
            font=("Segoe UI", 9),
            padx=15,
            relief="solid",
            borderwidth=1,
            cursor="hand2"
        )
        cancel_button.pack(side="right", padx=(5, 0))
        
        # Save button
        def save_settings():
            new_path = config_var.get()
            if not new_path:
                messagebox.showwarning("Empty Path", "Please enter a config file path.")
                return
            
            if not os.path.exists(new_path):
                response = messagebox.askyesno(
                    "File Not Found",
                    f"File does not exist:\n{new_path}\n\nSave anyway?"
                )
                if not response:
                    return
            
            self.config_file = new_path
            self._save_settings()
            messagebox.showinfo("Success", "Settings saved successfully.")
            settings_window.destroy()
        
        save_button = tk.Button(
            button_frame,
            text="Save",
            command=save_settings,
            bg="#0078d4",
            fg="white",
            font=("Segoe UI", 9),
            padx=15,
            relief="solid",
            borderwidth=1,
            cursor="hand2"
        )
        save_button.pack(side="right")
    
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
    # Fix Windows taskbar icon (must be called before tk.Tk())
    if platform.system() == 'Windows':
        try:
            import ctypes
            myappid = 'DanceMonkeyDance.7D2DServerConfigEditor.1.2.5'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except:
            pass
    
    root = tk.Tk()
    app = ServerConfigEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()

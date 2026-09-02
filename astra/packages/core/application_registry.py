import os
import re
import glob
import webbrowser
from typing import Optional, Dict, List

class ApplicationRegistry:
    """
    Maintains a comprehensive registry of known applications and their executables/paths.
    Resolves natural language aliases to executable commands using:
    1. Hardcoded exact paths discovered on this machine
    2. Windows Registry App Paths
    3. Start Menu shortcuts
    4. Dynamic glob scanning
    """
    def __init__(self):
        # ── Exact executable paths discovered on this machine ──────────────────
        self._exact: Dict[str, str] = {}
        self._discover_exact_paths()

        # ── Static alias → command / URI map ──────────────────────────────────
        self.app_map: Dict[str, str] = {
            # System utilities (always on PATH)
            "calculator": "calc",
            "calc": "calc",
            "calculator app": "calc",
            "notepad": "notepad",
            "text editor": "notepad",
            "paint": "mspaint",
            "mspaint": "mspaint",
            "cmd": "cmd",
            "command prompt": "cmd",
            "powershell": "powershell",
            "terminal": "wt",
            "windows terminal": "wt",
            "wt": "wt",
            "explorer": "explorer",
            "file explorer": "explorer",
            "files": "explorer",
            "my computer": "explorer",
            "task manager": "taskmgr",
            "taskmgr": "taskmgr",
            "control panel": "control",
            "snipping tool": "snippingtool",

            # Windows URI schemes
            "settings": "ms-settings:",
            "windows settings": "ms-settings:",
            "camera": "microsoft.windows.camera:",
            "clock": "ms-clock:",
            "photos": "ms-photos:",
            "mail": "outlookmail:",
            "calendar": "outlookcal:",

            # WhatsApp
            "whatsapp": "whatsapp://",
            "whats app": "whatsapp://",
            "whatsapp desktop": "whatsapp://",

            # VS Code
            "vs code": "code",
            "visual studio code": "code",
            "code": "code",
            "vscode": "code",

            # Browsers
            "browser": "chrome",
            "web browser": "chrome",

            # Office aliases → will resolve via _exact if found
            "word": "winword",
            "microsoft word": "winword",
            "ms word": "winword",
            "excel": "excel",
            "microsoft excel": "excel",
            "ms excel": "excel",
            "powerpoint": "powerpnt",
            "ppt": "powerpnt",
            "microsoft powerpoint": "powerpnt",
            "ms powerpoint": "powerpnt",
            "access": "msaccess",
            "outlook": "outlook",
            "onenote": "onenote",
            "publisher": "mspub",

            # Other
            "sublime text": "subl",
            "sublime": "subl",
            "pycharm": "pycharm",
            "intellij": "idea",
            "android studio": "studio64",
            "git bash": "git-bash",
            "java": "java",
            "opera": "opera",
            "opera gx": "opera",
        }

        # Overlay exact paths into app_map so they take priority
        for alias, path in self._exact.items():
            if path:
                self.app_map[alias] = path

        # Dynamic apps from registry / start menu
        self.dynamic_apps: Dict[str, str] = {}
        self.pre_warm()

    # ──────────────────────────────────────────────────────────────────────────
    # Exact-path discovery  (runs once at init)
    # ──────────────────────────────────────────────────────────────────────────
    def _discover_exact_paths(self):
        """Probe well-known install locations and populate self._exact."""
        user = os.path.expandvars("%USERPROFILE%")
        pf   = os.environ.get("PROGRAMFILES", r"C:\Program Files")
        pf86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
        appdata  = os.path.expandvars("%APPDATA%")
        localapp = os.path.expandvars("%LOCALAPPDATA%")

        candidates = {
            # Browsers
            "chrome":       [rf"{pf}\Google\Chrome\Application\chrome.exe",
                             rf"{pf86}\Google\Chrome\Application\chrome.exe"],
            "google chrome":[rf"{pf}\Google\Chrome\Application\chrome.exe",
                             rf"{pf86}\Google\Chrome\Application\chrome.exe"],
            "msedge":       [rf"{pf86}\Microsoft\Edge\Application\msedge.exe",
                             rf"{pf}\Microsoft\Edge\Application\msedge.exe"],
            "edge":         [rf"{pf86}\Microsoft\Edge\Application\msedge.exe"],
            "microsoft edge":[rf"{pf86}\Microsoft\Edge\Application\msedge.exe"],
            "firefox":      [rf"{pf}\Mozilla Firefox\firefox.exe",
                             rf"{pf86}\Mozilla Firefox\firefox.exe"],
            "opera":        [rf"{localapp}\Programs\Opera GX\opera.exe",
                             rf"{localapp}\Programs\Opera\opera.exe",
                             rf"{pf}\Opera GX\opera.exe"],

            # Office suite
            "winword":      [rf"{pf}\Microsoft Office\root\Office16\WINWORD.EXE",
                             rf"{pf}\Microsoft Office\Office16\WINWORD.EXE"],
            "excel":        [rf"{pf}\Microsoft Office\root\Office16\EXCEL.EXE",
                             rf"{pf}\Microsoft Office\Office16\EXCEL.EXE"],
            "powerpnt":     [rf"{pf}\Microsoft Office\root\Office16\POWERPNT.EXE",
                             rf"{pf}\Microsoft Office\Office16\POWERPNT.EXE"],
            "msaccess":     [rf"{pf}\Microsoft Office\root\Office16\MSACCESS.EXE"],
            "outlook":      [rf"{pf}\Microsoft Office\root\Office16\OUTLOOK.EXE"],
            "onenote":      [rf"{pf}\Microsoft Office\root\Office16\ONENOTE.EXE"],
            "mspub":        [rf"{pf}\Microsoft Office\root\Office16\MSPUB.EXE"],

            # VS Code
            "code":         [rf"{localapp}\Programs\Microsoft VS Code\Code.exe"],

            # Media / social
            "spotify":      [rf"{appdata}\Spotify\Spotify.exe",
                             rf"{localapp}\Microsoft\WindowsApps\SpotifyAB.SpotifyMusic*\Spotify.exe"],
            "discord":      [rf"{localapp}\Discord\*\Discord.exe",
                             rf"{localapp}\Discord\Update.exe"],
            "telegram":     [rf"{appdata}\Telegram Desktop\Telegram.exe",
                             rf"{localapp}\Telegram Desktop\Telegram.exe",
                             rf"{pf}\Telegram Desktop\Telegram.exe"],
            "zoom":         [rf"{appdata}\Zoom\bin\Zoom.exe",
                             rf"{pf}\Zoom\bin\Zoom.exe",
                             rf"{pf86}\Zoom\bin\Zoom.exe"],
            "vlc":          [rf"{pf}\VideoLAN\VLC\vlc.exe",
                             rf"{pf86}\VideoLAN\VLC\vlc.exe"],
            "slack":        [rf"{localapp}\slack\slack.exe",
                             rf"{appdata}\Microsoft\Windows\Start Menu\Programs\Slack Technologies\Slack.lnk"],
            "steam":        [rf"{pf86}\Steam\steam.exe",
                             rf"{pf}\Steam\steam.exe"],
            "postman":      [rf"{localapp}\Postman\Postman.exe"],
            "pycharm":      [rf"{pf}\JetBrains\PyCharm*\bin\pycharm64.exe"],
            "android studio": [rf"{pf}\Android\Android Studio\bin\studio64.exe"],
        }

        for alias, paths in candidates.items():
            for pattern in paths:
                matches = glob.glob(pattern)
                if matches:
                    self._exact[alias] = matches[0]
                    break

    # ──────────────────────────────────────────────────────────────────────────
    # Registry + Start Menu scan
    # ──────────────────────────────────────────────────────────────────────────
    def pre_warm(self):
        """
        Dynamically scans Windows Registry App Paths and Start Menu shortcuts.
        """
        # 1. Registry App Paths
        try:
            import winreg
            for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                try:
                    with winreg.OpenKey(root, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths") as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                exe_path    = winreg.QueryValue(key, subkey_name)
                                if exe_path:
                                    clean_k = subkey_name.lower().replace(".exe", "").strip()
                                    if clean_k not in self.dynamic_apps and clean_k not in self.app_map:
                                        self.dynamic_apps[clean_k] = exe_path
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception:
            pass

        # 2. Start Menu shortcuts
        try:
            start_dirs = [
                os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs"),
                os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            ]
            for s_dir in start_dirs:
                if os.path.exists(s_dir):
                    for root, _, files in os.walk(s_dir):
                        for f in files:
                            if f.lower().endswith(".lnk"):
                                app_name = f[:-4].lower().strip()
                                app_name_clean = re.sub(r"\s*\([^)]*\)", "", app_name).strip()
                                full_lnk_path  = os.path.join(root, f)
                                if app_name_clean not in self.dynamic_apps and app_name_clean not in self.app_map:
                                    self.dynamic_apps[app_name_clean] = full_lnk_path
        except Exception:
            pass

    # ──────────────────────────────────────────────────────────────────────────
    # Resolve
    # ──────────────────────────────────────────────────────────────────────────
    def resolve(self, app_name: str) -> str:
        """
        Resolves an application alias or name to its executable command / path.
        Priority: static_map (with injected exact paths) → dynamic registry/start-menu → partial match → raw string
        """
        clean_name = app_name.lower().strip()

        # 1. Static/exact map
        if clean_name in self.app_map:
            return self.app_map[clean_name]

        # 2. Dynamic registry / start menu
        if clean_name in self.dynamic_apps:
            return self.dynamic_apps[clean_name]

        # 3. Partial matching on static map
        for k, v in self.app_map.items():
            if clean_name in k or k in clean_name:
                return v

        # 4. Partial matching on dynamic apps
        for k, v in self.dynamic_apps.items():
            if clean_name in k or k in clean_name:
                return v

        # 5. Fallback to raw string
        return clean_name

    # ──────────────────────────────────────────────────────────────────────────
    # Launch
    # ──────────────────────────────────────────────────────────────────────────
    def launch(self, target: str) -> bool:
        """
        Launches an application, shortcut (.lnk), URI protocol, or URL using
        native Win32 ShellExecute with graceful fallbacks.
        """
        clean_target = str(target).strip()

        # Resolve if not already an absolute path or URL
        if not (os.path.isabs(clean_target) or
                clean_target.startswith(("http://", "https://", "whatsapp://", "ms-", "microsoft."))):
            resolved = self.resolve(clean_target)
        else:
            resolved = clean_target

        # WhatsApp: try desktop protocol, fall back to Web
        if resolved == "whatsapp://":
            try:
                os.startfile(resolved)
                return True
            except Exception:
                pass
            try:
                webbrowser.open("https://web.whatsapp.com/")
                return True
            except Exception:
                return False

        # Web URL
        if resolved.startswith(("http://", "https://")):
            try:
                webbrowser.open(resolved)
                return True
            except Exception:
                return False

        # 1. Native ShellExecute (handles .exe, .lnk, ms- URIs, UWP protocols)
        if hasattr(os, "startfile"):
            try:
                os.startfile(resolved)
                return True
            except Exception:
                pass

        # 2. CMD start (handles .lnk, spaces in paths, UWP aliases)
        try:
            import subprocess
            subprocess.Popen(f'start "" "{resolved}"', shell=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            pass

        # 3. PowerShell Start-Process
        try:
            import subprocess
            subprocess.Popen(["powershell", "-Command", f"Start-Process '{resolved}'"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            pass

        return False

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────────
    def parse_multiple(self, text: str) -> List[str]:
        """
        Parses 'notepad and calculator' → ['notepad', 'calculator'].
        """
        cleaned  = re.sub(r"\s+and\s+|\s*&\s+|\s+then\s+", ",", text, flags=re.IGNORECASE)
        parts    = [p.strip() for p in cleaned.split(",") if p.strip()]
        filtered = []
        for p in parts:
            p_clean = re.sub(r"^(?:the|an|a|my)\s+", "", p, flags=re.IGNORECASE).strip()
            if p_clean and p_clean not in ["all", "apps", "applications", "them"]:
                filtered.append(p_clean)
        return filtered if filtered else [text]

    def get_common_applications(self) -> List[str]:
        """Returns the suite launched by 'open all applications'."""
        return ["notepad", "calc", "paint", "explorer", "chrome", "edge", "code",
                "word", "excel", "powerpoint"]

    def get_known_aliases(self) -> List[str]:
        """Returns all known application aliases."""
        return list(set(list(self.app_map.keys()) + list(self.dynamic_apps.keys())))

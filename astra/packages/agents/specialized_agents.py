from typing import Dict, Any
from packages.agents.base_agent import AstraAgent
import subprocess
import time
import urllib.parse
import re
from packages.core.website_registry import WebsiteRegistry

class ResearchAgent(AstraAgent):
    def __init__(self):
        super().__init__("ResearchAgent", ["web_search", "summarize_articles", "compare_sources"])

    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get('action')
        query = task.get('query', '')
        
        if action == "web_search":
            import urllib.request
            try:
                url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
                req = urllib.request.Request(
                    url, 
                    data=None, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                
                with urllib.request.urlopen(req) as response:
                    html = response.read().decode('utf-8')
                    
                results = []
                parts = html.split('class="result__snippet')
                for p in parts[1:4]: # Top 3
                    snippet = p.split('>', 1)[1].split('</a>', 1)[0]
                    clean_text = re.sub('<[^<]+>', '', snippet).strip()
                    results.append(clean_text)
                    
                if not results:
                    return {"status": "error", "details": "No search results found."}
                    
                return {
                    "status": "success",
                    "action": action,
                    "result": f"Found information: {' | '.join(results)}"
                }
            except Exception as e:
                return {"status": "error", "details": str(e)}
        return {"status": "error", "details": "Unknown action"}


class BrowserAgent(AstraAgent):
    def __init__(self):
        super().__init__("BrowserAgent", ["browser_open", "open_website", "youtube_search", "website_search", "web_search", "browser_search_current_page", "browser_click"])
        self.website_registry = WebsiteRegistry()

    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get('action')
        print(f"[BrowserAgent] Executing {action}")
        
        try:
            if action in ["browser_open", "open_website"]:
                target = task.get('target', '')
                target_url = self.website_registry.resolve_url(target) if target else "https://www.google.com/"
                    
                subprocess.Popen(["powershell", "-Command", f"Start-Process '{target_url}'"])
                return {"status": "dispatched", "message": "Browser launch dispatched."}
                
            elif action == "youtube_search":
                query = task.get('query', '')
                search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
                subprocess.Popen(["powershell", "-Command", f"Start-Process '{search_url}'"])
                return {"status": "dispatched", "message": "YouTube search dispatched."}
                
            elif action == "website_search":
                query = task.get('query', '')
                target = task.get('target', '')
                # Generic fallback for website searches that don't have a special API adapter
                # We can route this to DuckDuckGo site search or just Google
                # Let's use duckduckgo site search
                url = self.website_registry.resolve_url(target)
                domain = urllib.parse.urlparse(url).netloc
                search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}+site%3A{domain}"
                subprocess.Popen(["powershell", "-Command", f"Start-Process '{search_url}'"])
                return {"status": "dispatched", "message": f"{target} search dispatched."}
                
            elif action == "web_search":
                query = task.get('query', '')
                search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
                subprocess.Popen(["powershell", "-Command", f"Start-Process '{search_url}'"])
                return {"status": "dispatched", "message": "Web search dispatched."}

            elif action == "browser_search_current_page":
                query = task.get('query', '')
                active_page = context.get('active_page', '').lower()
                
                if active_page == "youtube":
                    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
                else:
                    search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
                    
                subprocess.Popen(["powershell", "-Command", f"Start-Process '{search_url}'"])
                return {"status": "dispatched", "message": "Contextual search dispatched."}
                
            return {"status": "error", "details": "Action not fully supported in headless mode"}
        except Exception as e:
            return {"status": "error", "details": str(e)}


class CodingAgent(AstraAgent):
    def __init__(self):
        super().__init__("CodingAgent", ["inspect_repo", "write_code", "debug"])

    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success"}

class DocumentAgent(AstraAgent):
    def __init__(self):
        super().__init__("DocumentAgent", ["read_pdf", "create_report", "extract_text"])

    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success"}

class ProductivityAgent(AstraAgent):
    def __init__(self):
        super().__init__("ProductivityAgent", ["set_reminder", "read_calendar", "draft_email"])

    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success"}

class OSAgent(AstraAgent):
    """
    Executes raw OS commands on the user's local machine. 
    God Mode.
    """
    def __init__(self):
        super().__init__("OSAgent", [
            "run_terminal_command", 
            "open_application", 
            "open_all_applications", 
            "open_multiple_applications", 
            "close_application", 
            "close_all_applications", 
            "focus_application", 
            "calculation", 
            "type_message", 
            "contact_search"
        ])

    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes generic OS actions and pipes UI commands to ComputerUseEngine.
        """
        action = task.get('action')
        command = task.get('command') or task.get('target') or task.get('query') or ""
        
        print(f"[OSAgent] Executing {action} with target/command: {command}")
        
        try:
            # Handle explicit UI actions passed by the Fast Path
            if action in ["click", "type", "press", "scroll", "select"]:
                from packages.device.computer_use_engine import ComputerUseEngine
                from packages.core.models import UIAction
                engine = ComputerUseEngine()
                
                ui_action = action.upper()
                target_desc = command
                data = None
                
                if ui_action == "TYPE":
                    # For TYPE, command contains the target, task['message'] contains the text
                    # Wait, fast classifier gives {"action": "type_message", "message": target_or_query}
                    pass # We handle type_message separately below
                    
                if ui_action == "PRESS":
                    data = command
                    target_desc = "active window"
                    
                return engine.execute_ui_action(UIAction(ui_action), target_desc, context, data=data)

            if action == "execute_command":
                if command:
                    print(f"[OSAgent] Received command: {command}")
                
                    # Check if it's a UI Action
                    ui_actions_map = {
                        "click": "CLICK",
                        "type": "TYPE",
                        "press": "PRESS",
                        "scroll": "SCROLL",
                        "select": "SELECT"
                    }
                    
                    if command.startswith(("click", "type", "press", "scroll", "select")):
                        # Simple heuristic parser for UI commands
                        parts = command.split(" ", 1)
                        verb = parts[0].lower()
                        ui_action = ui_actions_map.get(verb)
                        
                        if ui_action:
                            from packages.device.computer_use_engine import ComputerUseEngine
                            from packages.core.models import UIAction
                            engine = ComputerUseEngine()
                            
                            target_desc = parts[1] if len(parts) > 1 else ""
                            data = None
                            
                            if ui_action == "TYPE":
                                # Extract target and data
                                # e.g., "type 'hello' in search bar" - simplified for now
                                target_desc = "active field" # Fallback
                                data = parts[1] if len(parts) > 1 else ""
                                
                            elif ui_action == "PRESS":
                                target_desc = "active window"
                                data = parts[1] if len(parts) > 1 else ""
                                
                            return engine.execute_ui_action(UIAction(ui_action), target_desc, context, data=data)
                            
            elif action == "search":
                # General action "search" in OSAgent should attempt Universal UI search for the active app
                active_app = context.get("active_application") or context.get("active_target") or ""
                query = task.get("query", str(command))
                
                from packages.device.browser_session_manager import BrowserSessionManager
                bm = BrowserSessionManager()
                bctx = bm.get_active_context()
                if bctx.get("url") and not active_app:
                    bm.search_website(query)
                    return {"status": "dispatched", "message": f"Website search dispatched: {query}"}
                    
                print(f"[OSAgent] Universal UI Search for '{query}' in '{active_app}'")
                
                # Use ComputerUseEngine to find search field, click, type and press Enter
                from packages.device.computer_use_engine import ComputerUseEngine
                from packages.core.models import UIAction
                engine = ComputerUseEngine()
                
                # First resolve and click
                target_desc = "search field"
                result = engine.execute_ui_action(UIAction.SEARCH, target_desc, context, data=query)
                
                # If UI search failed and it's not a native app, we fallback to generic web search if explicitly requested
                if result.get("status") == "error":
                    if not active_app:
                        search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
                        subprocess.Popen(["powershell", "-Command", f"Start-Process '{search_url}'"])
                        return {"status": "dispatched", "message": f"Web search for {query} dispatched."}
                    else:
                        return {"status": "error", "message": f"Could not find or use search field in {active_app}"}
                        
                return result
            elif action == "youtube_search":
                query = task.get("query") or str(command)
                search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
                subprocess.Popen(["powershell", "-Command", f"Start-Process '{search_url}'"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return {"status": "dispatched", "message": f"YouTube search dispatched for: {query}"}

            elif action == "web_search":
                query = task.get("query") or str(command)
                search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
                subprocess.Popen(["powershell", "-Command", f"Start-Process '{search_url}'"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return {"status": "dispatched", "message": f"Web search dispatched for: {query}"}

            elif action == "get_time":
                import datetime
                now_str = datetime.datetime.now().strftime("%I:%M %p")
                return {"status": "success", "result": f"The current time is {now_str}."}

            elif action == "get_date":
                import datetime
                date_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
                return {"status": "success", "result": f"Today is {date_str}."}

            elif action == "take_screenshot":
                try:
                    from PIL import ImageGrab
                    import os, time
                    os.makedirs("screenshots", exist_ok=True)
                    filename = f"screenshots/screenshot_{int(time.time())}.png"
                    img = ImageGrab.grab()
                    img.save(filename)
                    return {"status": "success", "result": f"Screenshot captured and saved as {filename}."}
                except Exception as e:
                    return {"status": "error", "message": f"Could not capture screenshot: {e}"}

            elif action == "volume_control":
                vol_cmd = str(command).lower()
                if "mute" in vol_cmd:
                    script = "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"
                elif "increase" in vol_cmd or "up" in vol_cmd or "raise" in vol_cmd:
                    script = "1..5 | ForEach-Object { (New-Object -ComObject WScript.Shell).SendKeys([char]175) }"
                else:
                    script = "1..5 | ForEach-Object { (New-Object -ComObject WScript.Shell).SendKeys([char]174) }"
                subprocess.run(["powershell", "-Command", script], capture_output=True)
                return {"status": "success", "result": f"Volume command executed: {command}"}
            elif action == "perform_ui_action":
                cmd = str(command).lower().strip()
                try:
                    import pyautogui
                    pyautogui.FAILSAFE = False
                    if cmd.startswith("type "):
                        text = command[5:]
                        pyautogui.write(text, interval=0.05)
                        return {"status": "success", "result": f"Typed: {text}"}
                    elif cmd.startswith("press "):
                        key = command[6:].strip()
                        pyautogui.press(key)
                        return {"status": "success", "result": f"Pressed key: {key}"}
                    elif cmd.startswith("click"):
                        pyautogui.click()
                        return {"status": "success", "result": "Clicked mouse"}
                    elif cmd.startswith("scroll up"):
                        pyautogui.scroll(500)
                        return {"status": "success", "result": "Scrolled up"}
                    elif cmd.startswith("scroll down"):
                        pyautogui.scroll(-500)
                        return {"status": "success", "result": "Scrolled down"}
                    else:
                        return {"status": "error", "message": f"Unsupported UI action: {cmd}"}
                except ImportError:
                    return {"status": "error", "message": "pyautogui is required for UI automation."}
                except Exception as e:
                    return {"status": "error", "message": f"UI action failed: {str(e)}"}

            elif action == "open_website":
                from packages.core.application_registry import ApplicationRegistry
                reg = ApplicationRegistry()
                if isinstance(command, dict):
                    url = command.get("url", "https://google.com")
                    name = command.get("name", "Website")
                else:
                    url = f"https://{command}.com" if not str(command).startswith("http") else str(command)
                    name = str(command)
                reg.launch(url)
                return {"status": "success", "result": f"Opened {name.title()} in browser.", "message": f"Website launch dispatched: {url}"}

            elif action in ["open_application", "open_all_applications", "open_multiple_applications"]:
                from packages.core.application_registry import ApplicationRegistry
                reg = ApplicationRegistry()
                
                # Case 1: Open all applications
                if action == "open_all_applications" or str(command).lower().strip() in ["all", "all applications", "all apps", "all the applications", "everything", "all my apps"]:
                    target_apps = reg.get_common_applications()
                    opened = []
                    for app in target_apps:
                        if reg.launch(app):
                            opened.append(app.title())
                    return {
                        "status": "success",
                        "action": "open_all_applications",
                        "result": f"Opened all applications: {', '.join(opened)}",
                        "message": f"Opened all applications: {', '.join(opened)}",
                        "opened_apps": opened
                    }
                
                # Case 2: Open multiple applications
                elif action == "open_multiple_applications" or (" and " in str(command).lower() or "," in str(command)):
                    app_list = reg.parse_multiple(str(command))
                    opened = []
                    for app in app_list:
                        if reg.launch(app):
                            opened.append(app.title())
                    return {
                        "status": "success",
                        "action": "open_multiple_applications",
                        "result": f"Opened: {', '.join(opened)}",
                        "message": f"Opened: {', '.join(opened)}",
                        "opened_apps": opened
                    }
                
                # Case 3: Single application
                else:
                    target_str = str(command).strip()
                    # Check if user specifically requested browser / web
                    if "browser" in target_str.lower() or "web" in target_str.lower():
                        from packages.core.website_registry import WebsiteRegistry
                        w_reg = WebsiteRegistry()
                        w_info = w_reg.resolve_website(target_str)
                        if w_info and w_info.get("url"):
                            reg.launch(w_info["url"])
                            return {"status": "success", "result": f"Opened {w_info.get('name', target_str)} in browser.", "message": f"Opened {w_info['url']}"}
                            
                    reg.launch(target_str)
                    clean_title = target_str.title()
                    return {"status": "success", "result": f"Opened {clean_title}.", "message": f"App launch dispatched: {target_str}", "target": target_str}

            elif action == "calculation":
                safe_expr = str(command).lower()
                safe_expr = safe_expr.replace("times", "*").replace("multiplied by", "*").replace("into", "*")
                safe_expr = safe_expr.replace("plus", "+").replace("minus", "-").replace("divided by", "/").replace("over", "/")
                safe_expr = safe_expr.replace("^", "**")
                clean_expr = re.sub(r'[^0-9\+\-\*\/\.\(\)\s]', '', safe_expr).strip()
                if clean_expr:
                    try:
                        calc_result = eval(clean_expr, {"__builtins__": None}, {})
                        return {"status": "success", "result": str(calc_result)}
                    except Exception:
                        pass
                result = subprocess.run(["powershell", "-Command", safe_expr], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return {"status": "success", "result": result.stdout.strip()}
                else:
                    return {"status": "error", "result": result.stderr.strip()}

            elif action in ["close_application", "close_all_applications"]:
                from packages.core.application_registry import ApplicationRegistry
                reg = ApplicationRegistry()
                
                if action == "close_all_applications" or str(command).lower().strip() in ["all", "all applications", "all apps", "everything", "all of them"]:
                    target_apps = reg.get_common_applications()
                    closed = []
                    for app in target_apps:
                        resolved_app = reg.resolve(app)
                        verify_cmd = f"Stop-Process -Name *{resolved_app}* -ErrorAction SilentlyContinue"
                        subprocess.run(["powershell", "-Command", verify_cmd], capture_output=True, text=True)
                        closed.append(app.title())
                    return {"status": "success", "result": f"Closed applications: {', '.join(closed)}", "message": "Close all apps dispatched."}
                else:
                    resolved_app = reg.resolve(str(command))
                    verify_cmd = f"Stop-Process -Name *{resolved_app}* -ErrorAction SilentlyContinue"
                    subprocess.run(["powershell", "-Command", verify_cmd], capture_output=True, text=True)
                    return {"status": "dispatched", "message": "Close app dispatched."}
                
            elif action == "focus_application":
                script = f"$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('{command}')"
                subprocess.run(["powershell", "-Command", script], capture_output=True, text=True)
                return {"status": "dispatched", "message": "Focus app dispatched."}

            elif action == "type_message":
                message = task.get("message", "")
                target = task.get("target", "")
                if not message:
                    return {"status": "error", "message": "Missing message body."}
                    
                if target:
                    script_focus = f"$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('{target}')"
                    subprocess.run(["powershell", "-Command", script_focus], capture_output=True)
                    time.sleep(1)
                
                script_type = f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{message}'); [System.Windows.Forms.SendKeys]::SendWait('{{ENTER}}')"
                subprocess.run(["powershell", "-Command", script_type], capture_output=True, text=True)
                return {"status": "success", "message": "Typing dispatched."}

            elif action == "contact_search":
                target = task.get("target", "")
                query = task.get("query", "")
                if not query:
                    return {"status": "error", "message": "Missing contact name query."}
                    
                if target:
                    script_focus = f"$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('{target}')"
                    subprocess.run(["powershell", "-Command", script_focus], capture_output=True)
                    time.sleep(1)
                
                script_search = f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^f'); Start-Sleep -Milliseconds 500; [System.Windows.Forms.SendKeys]::SendWait('{query}'); Start-Sleep -Milliseconds 1500; [System.Windows.Forms.SendKeys]::SendWait('{{ENTER}}')"
                subprocess.run(["powershell", "-Command", script_search], capture_output=True)
                return {"status": "success", "message": "Contact search dispatched."}

            else:
                result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, timeout=10)
                output = result.stdout.strip() if result.stdout else "Command executed successfully with no output."
                return {
                    "status": "success" if result.returncode == 0 else "error",
                    "result": output
                }
                
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Command timed out."}
        except Exception as e:
            return {"status": "error", "message": f"Exception during execution: {str(e)}"}

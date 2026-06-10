# import tool modules (we will create them later)
from tools import app_tools, media_tools, system_tools, web_tools, file_tools, storage_tools


class ToolExecutor:

    def __init__(self, prefs=None):
        self.prefs = prefs or {}

        # -----------------------------
        # TOOL REGISTRY
        # -----------------------------
        self.TOOL_REGISTRY = {

            # APP
            "open_app": app_tools.open_app,
            "close_app": app_tools.close_app,
            "list_apps": app_tools.list_apps,

            # MEDIA
            "media_play": media_tools.media_play,
            "media_pause": media_tools.media_pause,
            "media_skip": media_tools.media_skip,
            "media_volume": media_tools.media_volume,

            # SYSTEM
            "set_dark_mode": system_tools.set_dark_mode,
            "set_light_mode": system_tools.set_light_mode,
            "set_wallpaper": system_tools.set_wallpaper,
            "set_random_wallpaper": system_tools.set_random_wallpaper,
            "set_font_size": system_tools.set_font_size,
            "set_brightness": system_tools.set_brightness,
            "empty_trash": system_tools.empty_trash,
            "get_system_info": system_tools.get_system_info,

            # WEB
            "open_url": web_tools.open_url,
            "web_search": web_tools.web_search,

            # FILE
            "read_file": file_tools.read_file,
            "write_file": file_tools.write_file,
            "find_file": file_tools.find_file,

            # STORAGE
            "storage_report": storage_tools.storage_report,
            "find_large_files": storage_tools.find_large_files,
            "find_duplicate_files": storage_tools.find_duplicate_files,
        }

    # -----------------------------
    # EXECUTE ACTION
    # -----------------------------
    def execute(self, action_data: dict):
        action = action_data.get("action")
        params = action_data.get("params", {})

        if action not in self.TOOL_REGISTRY:
            return False, f"Unknown action: {action}"

        tool_func = self.TOOL_REGISTRY[action]

        try:
            result = tool_func(params, self.prefs)

            # normalize output
            if isinstance(result, tuple):
                return result
            else:
                return True, str(result)

        except Exception as e:
            return False, f"Error executing {action}: {str(e)}"
def execute_sequence(self, actions: list):
    results = []

    for action_data in actions:
        success, message = self.execute(action_data)

        results.append({
            "action": action_data.get("action"),
            "success": success,
            "message": message
        })

        if not success:
            break  # stop on failure

    return results

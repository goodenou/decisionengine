import os
import logging
from pathlib import Path

import decisionengine.framework.modules.de_logger as de_logger

def files_with_extensions(dir_path, *extensions):
    '''
    Return all files in dir_path that match the provided extensions.

    If no extensions are given, then all files in dir_path are returned.

    Results are sorted by channel name to ensure stable output.
    '''
    de_logger.log("DEBUG", f"dir_path is {dir_path}!", "")

    if len(extensions) == 0:
        extensions = ('')
        de_logger.log("INFO", "file extensions have zero length", "")

    name_to_path = []

    try:
        for entry in Path(dir_path).iterdir():
            if not entry.is_file():
                continue
            if entry.name.endswith(extensions):
                channel_name = os.path.splitext(entry.name)[0]
                name_to_path.append([channel_name, str(entry)])
    except FileNotFoundError:
        de_logger.log("CRITICAL", "invalid path to config file given", "")
        raise
    except Exception:
        de_logger.log("CRITICAL", "Unexpected error!", "")
        raise
    else:
        return tuple(sorted(name_to_path, key=lambda x: x[0]))

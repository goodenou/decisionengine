import socket
import decisionengine.framework.modules.de_logger as de_logger

def get_random_port():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    except OSError:
        de_logger.log("CRITICAL", "problem with get_random_port", "")
        raise
    except Exception:
        de_logger.log("CRITICAL", "Unexpected error!", "")
        raise

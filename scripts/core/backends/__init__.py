import shutil
import os

def get_backend(config=None):
    """Select spawn backend based on config and environment."""
    from scripts.core.backends.thread_backend import ThreadBackend
    from scripts.core.backends.tmux_backend import TmuxBackend

    backend_choice = getattr(config, 'backend', 'auto') if config else 'auto'

    if backend_choice == "tmux":
        return TmuxBackend()
    elif backend_choice == "thread":
        return ThreadBackend()
    else:  # auto
        if shutil.which("tmux") and "TMUX" not in os.environ:
            return TmuxBackend()
        return ThreadBackend()

"""
storage.py — one place that decides where uploaded files live
=============================================================

Before this module the codebase resolved the upload directory three different
ways, which meant a file written by one code path was invisible to another as
soon as the process CWD differed from the app root (exactly what happens under
Gunicorn on Render):

    services/StudentService.py   'uploads/resumes'                  -> CWD-relative
    resources/api.py (serve)     os.getcwd() + 'uploads/resumes'    -> CWD-relative
    resources/api.py (offers)    current_app.root_path + 'uploads'  -> app-relative

Everything now routes through here, anchored on the absolute UPLOAD_FOLDER
config value.

NOTE ON PERSISTENCE: on Render's default (diskless) instances this directory is
ephemeral — uploaded resumes and offer letters are wiped on every deploy and on
every restart. Attach a Render Disk mounted at UPLOAD_FOLDER, or move to object
storage, before this is used for anything that matters. See DEPLOYMENT.md.
"""

import os

from flask import current_app
from werkzeug.utils import secure_filename

RESUMES = 'resumes'
OFFERS  = 'offers'


def upload_root():
    """Absolute path to the configured upload root."""
    return current_app.config['UPLOAD_FOLDER']


def subdir(kind):
    """
    Absolute path to an upload subdirectory, created if missing.
    `kind` must be one of the module constants, never user input.
    """
    if kind not in (RESUMES, OFFERS):
        raise ValueError(f'Unknown upload kind: {kind!r}')
    path = os.path.join(upload_root(), kind)
    os.makedirs(path, exist_ok=True)
    return path


def safe_name(filename):
    """
    Reject anything that could escape the upload directory.
    Returns None if the name is unsafe.

    secure_filename() alone is not enough here because it silently *rewrites*
    a hostile name into a benign one — for a lookup (as opposed to a save) that
    would turn '../../etc/passwd' into 'etc_passwd' and 404 confusingly instead
    of telling the caller the request was malformed.
    """
    if not filename:
        return None
    if '/' in filename or '\\' in filename or '..' in filename:
        return None
    if filename != secure_filename(filename):
        return None
    return filename


def path_for(kind, filename):
    """
    Absolute path to a stored file, or None if the filename is unsafe.
    Does not check existence — callers decide how to report a miss.
    """
    name = safe_name(filename)
    if name is None:
        return None
    return os.path.join(subdir(kind), name)


def is_allowed(filename, allowed=None):
    """True if the extension is in the configured allow-list."""
    allowed = allowed or current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

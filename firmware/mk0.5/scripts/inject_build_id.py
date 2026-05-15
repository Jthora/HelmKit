"""Inject git SHA + schema version into compile-time build_flags.

Closes critique RP2 (banner has no commit/MK/schema).

Falls back to "nogit" if git is unavailable (fresh clone in CI w/o .git, or
zip download). Build is not blocked by missing git — only the banner field
becomes opaque.
"""
import subprocess
Import("env")

def _git_sha() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short=10", "HEAD"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode("ascii").strip()
    except Exception:
        return "nogit"

def _git_dirty() -> str:
    try:
        out = subprocess.check_output(
            ["git", "status", "--porcelain"],
            stderr=subprocess.DEVNULL,
        )
        return "1" if out.strip() else "0"
    except Exception:
        return "0"

GIT_SHA      = _git_sha()
GIT_DIRTY    = _git_dirty()
# Schema version is the major.minor that this firmware emits, NOT the version
# of psiStabilizer that it is subordinate to. Bump when the wire format
# changes in a way that requires Pi log-sink updates.
SCHEMA_VER   = "0.2-mk0.5"

env.Append(CPPDEFINES=[
    ("HELMKIT_GIT_SHA",        '\\"%s\\"' % GIT_SHA),
    ("HELMKIT_GIT_DIRTY",      GIT_DIRTY),
    ("HELMKIT_SCHEMA_VERSION", '\\"%s\\"' % SCHEMA_VER),
])

print("[helmkit] build id: git=%s dirty=%s schema=%s"
      % (GIT_SHA, GIT_DIRTY, SCHEMA_VER))

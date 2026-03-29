"""Agents package — exports Andres's analysis agents for Zeus to orchestrate.

Import order matters: ares → apollo → hades (dependency chain).
"""

from __future__ import annotations

<<<<<<< HEAD
from agents.apollo import apollo
from agents.ares import ares
from agents.hades import hades

__all__ = ["apollo", "ares", "hades"]
=======
from agents.ares import ares
from agents.apollo import apollo
from agents.hades import hades

__all__ = ["hades", "apollo", "ares"]
>>>>>>> origin/andres/agents

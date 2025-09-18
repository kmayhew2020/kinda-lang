"""
Kinda-Lang Migration Framework

Epic #127: Python Enhancement Bridge - Gradual migration utilities that enable
incremental adoption of kinda-lang constructs in Python projects.
"""

from .decorators import enhance, enhance_class, kinda_migrate
from .strategy import MigrationStrategy, FourPhaseStrategy
from .utilities import MigrationUtilities

__all__ = [
    'enhance',
    'enhance_class',
    'kinda_migrate',
    'MigrationStrategy',
    'FourPhaseStrategy',
    'MigrationUtilities'
]
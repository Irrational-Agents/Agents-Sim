from typing import List, Tuple, Dict, Optional
from collections import deque
import heapq
from enum import Enum
from dataclasses import dataclass
from config.logger_config import setup_logger

logger = setup_logger('PathPlanner')

class MovementType(Enum):
    WALK = 1
    RUN = 2
    IDLE = 0

@dataclass
class MovementConfig:
    """移动配置"""
    tiles_per_time_unit: int  # 每15分钟可以移动的格子数

# 不同移动类型的配置
MOVEMENT_SPEEDS = {
    MovementType.WALK: MovementConfig(tiles_per_time_unit=3),  # 每15分钟走3格
    MovementType.RUN: MovementConfig(tiles_per_time_unit=5),   # 每15分钟跑5格
    MovementType.IDLE: MovementConfig(tiles_per_time_unit=0)   # 静止不动
}

from collections import deque

class PathPlanner:
    def __init__(self, map_instance):
        self.map = map_instance
        self.directions = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1)
        }
        self.reverse_directions = {v: k for k, v in self.directions.items()}
        self.collision_wall = 32125

    def is_valid(self, x, y):
        """Check if a position is within bounds and not an obstacle."""
        vaild = (0 <= x < len(self.map.collision_maze) and
                0 <= y < len(self.map.collision_maze[0]) and
                self.map.collision_maze[x][y] != self.collision_wall)
        return vaild

    def create_path(self, start, end, start_direction=None):
        """Find the shortest path using BFS."""
        queue = deque([(start[0], start[1], [])])
        visited = set()
        visited.add((start[0], start[1]))

        while queue:
            x, y, path = queue.popleft()

            if (x, y) == end:
                return path

            for direction, (dx, dy) in self.directions.items():
                new_x, new_y = x + dx, y + dy

                if self.is_valid(new_x, new_y) and (new_x, new_y) not in visited:
                    visited.add((new_x, new_y))
                    queue.append((new_x, new_y, path + [direction]))

        return []  # No valid path found


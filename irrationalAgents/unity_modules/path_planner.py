from collections import deque
from typing import Tuple, List, Optional
from config.logger_config import setup_logger
from unity_modules.map import Map

logger = setup_logger('PathPlanner')


class PathPlanner:
    def __init__(self, map_instance: Map):
        """
        Initialize the path planner with a map instance.

        Args:
            map_instance: An instance of the game map containing tile information
        """
        self.map = map_instance
        self.directions = {
            "left": (-1, 0),
            "right": (1, 0),
            "up": (0, -1),
            "down": (0, 1)
        }
        self.reverse_directions = {v: k for k, v in self.directions.items()}
        self.cache = {}  # Path cache for optimization

    def _make_cache_key(self, start: Tuple[int, int], end: Tuple[int, int], start_direction: Optional[str] = None) -> Tuple:
        """
        Create a hashable cache key from pathfinding parameters.

        Args:
            start: Starting position (x, y)
            end: Target position (x, y)
            start_direction: Optional starting direction

        Returns:
            A hashable tuple suitable for use as a cache key
        """
        return (start[0], start[1], end[0], end[1], start_direction or '')

    def is_valid_position(self, x: int, y: int) -> bool:
        """
        Check if a position is valid (within bounds and not an obstacle).
        """
        try:
            tile = self.map.get_tile_details((x, y))
            return not tile.get('collision', True)
        except (IndexError, KeyError, TypeError):
            logger.debug(f"Invalid position or tile data at ({x}, {y})")
            return False

    def create_path(self,
                    start: Tuple[int, int],
                    end: Tuple[int, int],
                    start_direction: Optional[str] = None) -> List[str]:
        """
        Find the shortest path between two points using BFS with optimizations.
        """
        # Create proper cache key
        cache_key = self._make_cache_key(start, end, start_direction)

        # Check cache first
        if cache_key in self.cache:
            # Return a copy to prevent cache modification
            return self.cache[cache_key].copy()

        # Validate inputs - fixed tuple concatenation
        if not (isinstance(start, tuple) and isinstance(end, tuple) and
                len(start) == 2 and len(end) == 2 and
                all(isinstance(coord, int) for coord in start) and
                all(isinstance(coord, int) for coord in end)):
            logger.error("Invalid coordinates provided")
            return []

        if not self.is_valid_position(*end):
            logger.debug(f"Target position {end} is invalid")
            return []

        # Initialize BFS
        queue = deque()
        visited = {}

        # If starting direction is provided, prioritize that direction first
        if start_direction and start_direction in self.directions:
            dx, dy = self.directions[start_direction]
            new_x, new_y = start[0] + dx, start[1] + dy
            if self.is_valid_position(new_x, new_y):
                queue.append((new_x, new_y, [start_direction]))
                visited[(new_x, new_y)] = True

        # Add all other possible starting moves
        for direction, (dx, dy) in self.directions.items():
            if start_direction and direction == start_direction:
                continue  # Already added
            new_x, new_y = start[0] + dx, start[1] + dy
            if self.is_valid_position(new_x, new_y) and (new_x, new_y) not in visited:
                queue.append((new_x, new_y, [direction]))
                visited[(new_x, new_y)] = True

        # Main BFS loop
        while queue:
            x, y, path = queue.popleft()

            if (x, y) == end:
                # Store a copy in cache and return a copy
                self.cache[cache_key] = path.copy()
                return path.copy()

            # Explore neighbors
            for direction, (dx, dy) in self.directions.items():
                new_x, new_y = x + dx, y + dy

                if (self.is_valid_position(new_x, new_y) and
                        (new_x, new_y) not in visited):
                    visited[(new_x, new_y)] = True
                    queue.append((new_x, new_y, path + [direction]))

        logger.debug(f"No valid path found from {start} to {end}")
        return []  # No path found

    def clear_cache(self):
        """Clear the path cache."""
        self.cache = {}

    def get_direction_vector(self, direction: str) -> Tuple[int, int]:
        """
        Get the (dx, dy) vector for a given direction.

        Args:
            direction: Direction name ('up', 'down', 'left', 'right')

        Returns:
            Tuple representing the movement vector
        """
        return self.directions.get(direction, (0, 0))

    def smooth_path(self, path: List[str]) -> List[str]:
        """
        Optimize a path by removing unnecessary direction changes.

        Args:
            path: Original path as list of directions

        Returns:
            Smoothed path with fewer direction changes
        """
        if not path or len(path) < 2:
            return path.copy() if path else []

        smoothed = [path[0]]
        for direction in path[1:]:
            if direction != smoothed[-1]:
                smoothed.append(direction)
        return smoothed

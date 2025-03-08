from typing import List, Tuple, Dict, Optional
from collections import deque
import heapq
from enum import Enum
from dataclasses import dataclass
from logger_config import setup_logger

logger = setup_logger('PathPlanner')

class MovementType(Enum):
    WALK = 1
    RUN = 2
    IDLE = 0

@dataclass
class MovementConfig:
    """移动配置"""
    tiles_per_15min: int  # 每15分钟可以移动的格子数
    energy_cost: float    # 每格消耗的能量

# 不同移动类型的配置
MOVEMENT_SPEEDS = {
    MovementType.WALK: MovementConfig(tiles_per_time_unit=3),  # 每15分钟走3格
    MovementType.RUN: MovementConfig(tiles_per_time_unit=5),   # 每15分钟跑5格
    MovementType.IDLE: MovementConfig(tiles_per_time_unit=0)   # 静止不动
}

class PathPlanner:

    def __init__(self, map_instance):
        self.map = map_instance
        
    def plan_path_from_memory(self, memory_action: Dict, current_pos: Tuple[int, int]) -> Dict:
        """
        根据记忆中的行动计划生成具体的路径
        
        Args:
            memory_action: 记忆中的行动，包含description等信息
            current_pos: NPC当前位置 (x, y)
        """
        try:
            # 1. 从描述中提取目标位置
            target_info = self._extract_location_from_memory(memory_action['description'])
            if not target_info:
                logger.warning(f"无法从描述中提取位置信息: {memory_action['description']}")
                return None
                
            # 2. 获取目标位置的具体坐标
            target_coords = self.map.get_address_tiles(target_info)
            if not target_coords:
                logger.warning(f"无法找到目标位置的坐标: {target_info}")
                return None
                
            # 3. 使用A*算法规划路径
            path = self._find_path_astar(current_pos, target_coords)
            
            # 4. 计算移动情况
            """
            MVP版本，假设所有的路径都能在一个时间单位内完成, 仅给出路径和目标位置
            """

            #action_type = self._determine_action_type(memory_action['description'])
            #estimated_steps = self.estimate_total_time(path, action_type)
            
            return {
                'path': path,
                'target_pos': target_coords
            }
            
        except Exception as e:
            logger.error(f"路径规划失败: {str(e)}")
            return None
            
    def _extract_location_from_memory(self, description: str) -> Optional[Dict[str, str]]:
        """
        从记忆描述中提取位置信息
        """
        # 获取地图中所有可能的位置和房间
        locations = set()
        rooms = set()
        
        for i in range(self.map.maze_height):
            for j in range(self.map.maze_width):
                tile = self.map.tiles[i][j]
                if tile['location']:
                    locations.add(tile['location'])
                if tile['room']:
                    rooms.add(tile['room'])
                    
        # 在描述中查找匹配的位置和房间
        found_location = None
        found_room = None
        
        for location in locations:
            if location.lower() in description.lower():
                found_location = location
                break
                
        for room in rooms:
            if room.lower() in description.lower():
                found_room = room
                break
                
        if found_location or found_room:
            return {
                'location': found_location,
                'room': found_room
            }
        return None
                
    def _find_path_astar(self, start: Tuple[int, int], 
                        possible_targets: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        使用A*算法找到到最近目标的路径
        """
        if not possible_targets:
            return []
            
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
            
        def get_neighbors(pos):
            x, y = pos
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_y < self.map.maze_height and 
                    0 <= new_x < self.map.maze_width and 
                    not self.map.tiles[new_y][new_x]['collision']):
                    neighbors.append((new_x, new_y))
            return neighbors
            
        # 对每个可能的目标尝试寻路，选择最短的路径
        best_path = None
        min_length = float('inf')
        
        for target in possible_targets:
            frontier = []
            heapq.heappush(frontier, (0, start))
            came_from = {start: None}
            cost_so_far = {start: 0}
            
            while frontier:
                current = heapq.heappop(frontier)[1]
                
                if current == target:
                    # 构建路径
                    path = []
                    while current:
                        path.append(current)
                        current = came_from[current]
                    path.reverse()
                    
                    if len(path) < min_length:
                        min_length = len(path)
                        best_path = path
                    break
                    
                for next_pos in get_neighbors(current):
                    new_cost = cost_so_far[current] + 1
                    
                    if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                        cost_so_far[next_pos] = new_cost
                        priority = new_cost + heuristic(target, next_pos)
                        heapq.heappush(frontier, (priority, next_pos))
                        came_from[next_pos] = current
                        
        return best_path
        
    def _determine_action_type(self, description: str) -> str:
        """
        根据描述确定行动类型
        """
        for action in MovementType:
            if action.name.lower() in description.lower():
                return action
        return MovementType.IDLE
        
    def calculate_movement(self, 
                         path: List[Tuple[int, int]], 
                         current_step: int,
                         movement_type: MovementType = MovementType.WALK) -> Dict:
        """
        计算下一个15分钟时间单位内的移动情况
        
        Args:
            path: 完整路径点列表
            current_step: 当前在路径上的位置索引
            movement_type: 移动类型（走路/跑步/静止）
            
        Returns:
            Dict: {
                'next_position': (x, y),        # 下一个时间单位结束时的位置
                'steps_taken': int,             # 这个时间单位内移动了多少步
                'path_completed': bool,         # 是否到达终点
                'remaining_path': [(x, y), ...],# 剩余路径
            }
        """
        try:
            if not path or current_step >= len(path):
                return {
                    'next_position': path[-1] if path else None,
                    'steps_taken': 0,
                    'path_completed': True,
                    'remaining_path': []
                }

            movement_config = MOVEMENT_SPEEDS[movement_type]
            max_steps = movement_config.tiles_per_time_unit
            
            # 计算这个时间单位内能走多远
            remaining_path = path[current_step:]
            steps_possible = min(max_steps, len(remaining_path))
            next_position = remaining_path[steps_possible - 1]
            
            # 检查是否完成整个路径
            path_completed = (current_step + steps_possible) >= len(path)
            
            # 更新剩余路径
            new_remaining_path = path[current_step + steps_possible:] if not path_completed else []
            
            return {
                'next_position': next_position,
                'steps_taken': steps_possible,
                'path_completed': path_completed,
                'remaining_path': new_remaining_path
            }
            
        except Exception as e:
            logger.error(f"计算移动时出错: {str(e)}")
            return None

    def estimate_total_time(self, path: List[Tuple[int, int]], 
                          movement_type: MovementType = MovementType.WALK) -> int:
        """
        估算完成整个路径需要的15分钟时间单位数
        
        Args:
            path: 路径点列表
            movement_type: 移动类型
            
        Returns:
            int: 需要的15分钟时间单位数
        """
        if not path:
            return 0
            
        movement_config = MOVEMENT_SPEEDS[movement_type]
        total_steps = len(path) - 1  # 减去起点
        
        # 向上取整，确保有足够的时间单位
        return (total_steps + movement_config.tiles_per_time_unit - 1) // movement_config.tiles_per_time_unit 
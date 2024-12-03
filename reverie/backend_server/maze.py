"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: maze.py
Description: Defines the Maze class, which represents the map of the simulated
world in a 2-dimensional matrix. 
"""
import json
import numpy
import datetime
import pickle
import time
import math

from global_methods import *
from utils import *

class Maze: 
  def __init__(self, maze_name=None, width=None, height=None, layout=None): 
    """
    Initialize the Maze with either a maze name or dimensions
    
    Args:
        maze_name: Name of the maze to load (optional)
        width: Width of the maze (optional)
        height: Height of the maze (optional)
        layout: Optional 2D list representing the maze layout
    """
    if maze_name:
      # Load maze from file
      self._load_maze(maze_name)
    elif width and height:
      # Initialize with given dimensions
      self.width = width
      self.height = height
      self.layout = layout if layout else self._generate_default_layout()
    else:
      # Default size if no parameters provided
      self.width = 10
      self.height = 10
      self.layout = self._generate_default_layout()
      
    # Initialize tiles structure
    self.tiles = self._generate_tiles()
      
    # Initialize events dictionary
    self.events = {}
      
  def _load_maze(self, maze_name):
    """
    Load maze configuration from file
    
    Args:
        maze_name: Name of the maze file to load
    """
    try:
      # Construct path to maze file
      maze_path = f"../../environment/frontend_server/storage/{maze_name}/maze.json"
      
      # Load maze configuration
      with open(maze_path, 'r') as f:
        maze_data = json.load(f)
        
      # Set maze dimensions
      self.width = maze_data.get('width', 10)
      self.height = maze_data.get('height', 10)
      
      # Load layout if available, otherwise generate default
      self.layout = maze_data.get('layout', self._generate_default_layout())
      
      # Load any pre-existing events
      self.events = maze_data.get('events', {})
      
    except Exception as e:
      print(f"Error loading maze {maze_name}: {str(e)}")
      # Fall back to default maze
      self.width = 10
      self.height = 10
      self.layout = self._generate_default_layout()
      self.events = {}
      
  def _generate_default_layout(self):
    """Generate a default empty layout"""
    return [[0 for _ in range(self.width)] for _ in range(self.height)]
    
  def _generate_tiles(self):
    """Generate the tiles structure"""
    tiles = []
    for y in range(self.height):
      row = []
      for x in range(self.width):
        tile = {
          "x": x,
          "y": y,
          "type": "traversable" if self.layout[y][x] == 0 else "wall",
          "events": set(),  # Set to store current events
          "description": "",  # Optional tile description
          "objects": set(),  # Set to store objects on this tile
        }
        row.append(tile)
      tiles.append(row)
    return tiles
    
  def is_traversable(self, tile):
    """
    Check if a tile is traversable (not a wall)
    
    Args:
        tile: Tile coordinates (x, y)
        
    Returns:
        bool: True if the tile is traversable
    """
    x, y = tile
    if not (0 <= x < self.width and 0 <= y < self.height):
      return False
    return self.tiles[y][x]["type"] == "traversable"
    
  def get_events_at(self, tile):
    """
    Get all events at a specific tile
    
    Args:
        tile: Tile coordinates (x, y)
        
    Returns:
        list: List of events at the tile
    """
    x, y = tile
    if not (0 <= x < self.width and 0 <= y < self.height):
      return []
    return list(self.tiles[y][x]["events"])
    
  def add_event(self, tile, event):
    """
    Add an event to a specific tile
    
    Args:
        tile: Tile coordinates (x, y)
        event: Event to add
    """
    x, y = tile
    if 0 <= x < self.width and 0 <= y < self.height:
      self.tiles[y][x]["events"].add(event)
    
  def remove_event(self, tile, event):
    """
    Remove an event from a specific tile
    
    Args:
        tile: Tile coordinates (x, y)
        event: Event to remove
    """
    x, y = tile
    if 0 <= x < self.width and 0 <= y < self.height:
      self.tiles[y][x]["events"].discard(event)
    
  def get_distance(self, start, end):
    """
    Calculate Manhattan distance between two tiles
    
    Args:
        start: Starting tile coordinates (x, y)
        end: Ending tile coordinates (x, y)
        
    Returns:
        int: Manhattan distance between tiles
    """
    return abs(end[0] - start[0]) + abs(end[1] - start[1])
    
  def remove_subject_events_from_tile(self, subject, tile):
    """
    Remove all events with a specific subject from a tile
    
    Args:
        subject: The subject to match in events
        tile: Tile coordinates (x, y)
    """
    x, y = tile
    if not (0 <= x < self.width and 0 <= y < self.height):
        print(f"Warning: Tile coordinates out of bounds: ({x}, {y})")
        return
        
    # Get the events set for this tile
    events = self.tiles[y][x]["events"]
    
    # Create a list of events to remove
    to_remove = set()
    for event in events:
        # Check if event is a tuple and has at least one element
        if isinstance(event, tuple) and len(event) > 0:
            # If the first element (subject) matches, mark for removal
            if event[0] == subject:
                to_remove.add(event)
                
    # Remove the marked events
    for event in to_remove:
        events.discard(event)
        
    # Update the tile's events
    self.tiles[y][x]["events"] = events
    
  def add_event_from_tile(self, event, tile):
    """
    Add an event to a specific tile
    
    Args:
        event: The event to add (typically a tuple of subject, predicate, object, description)
        tile: Tile coordinates (x, y)
    """
    x, y = tile
    if not (0 <= x < self.width and 0 <= y < self.height):
        print(f"Warning: Tile coordinates out of bounds: ({x}, {y})")
        # If coordinates are out of bounds, expand the maze
        new_width = max(self.width, x + 1)
        new_height = max(self.height, y + 1)
        self._expand_maze(new_width, new_height)
        
    # Now add the event to the tile
    self.tiles[y][x]["events"].add(event)
    
  def _expand_maze(self, new_width, new_height):
    """
    Expand the maze to accommodate new dimensions
    
    Args:
        new_width: New width of the maze
        new_height: New height of the maze
    """
    # Expand layout
    old_layout = self.layout
    self.layout = [[0 for _ in range(new_width)] for _ in range(new_height)]
    for y in range(min(self.height, new_height)):
        for x in range(min(self.width, new_width)):
            self.layout[y][x] = old_layout[y][x]
            
    # Expand tiles structure
    old_tiles = self.tiles
    self.tiles = []
    for y in range(new_height):
        row = []
        for x in range(new_width):
            if y < self.height and x < self.width:
                # Copy existing tile
                row.append(old_tiles[y][x])
            else:
                # Create new tile
                tile = {
                    "x": x,
                    "y": y,
                    "type": "traversable",
                    "events": set(),
                    "description": "",
                    "objects": set(),
                }
                row.append(tile)
        self.tiles.append(row)
        
    # Update dimensions
    self.width = new_width
    self.height = new_height
    print(f"Maze expanded to {self.width}x{self.height}")
    
  def remove_event_from_tile(self, event, tile):
    """
    Remove a specific event from a tile
    
    Args:
        event: The event to remove
        tile: Tile coordinates (x, y)
    """
    x, y = tile
    if not (0 <= x < self.width and 0 <= y < self.height):
        print(f"Warning: Tile coordinates out of bounds: ({x}, {y})")
        return
        
    # Get the events set for this tile
    events = self.tiles[y][x]["events"]
    
    # Remove the event if it exists
    if event in events:
        events.discard(event)
    else:
        # If the event is a tuple, try to match its components
        if isinstance(event, tuple):
            matching_events = set()
            for existing_event in events:
                if isinstance(existing_event, tuple):
                    # Match as many components as available in both tuples
                    min_len = min(len(event), len(existing_event))
                    if event[:min_len] == existing_event[:min_len]:
                        matching_events.add(existing_event)
            
            # Remove all matching events
            for matching_event in matching_events:
                events.discard(matching_event)
                
    # Update the tile's events
    self.tiles[y][x]["events"] = events
    
  def get_tiles_in_vision_range(self, center_tile, vision_radius):
    """
    Get all tiles within a given vision radius of a center tile
    
    Args:
        center_tile: The central tile to check from (x, y)
        vision_radius: How far the agent can see (in tiles)
        
    Returns:
        list: List of tile coordinates within vision range
    """
    if not center_tile:
        return []
        
    x, y = center_tile
    if not (0 <= x < self.width and 0 <= y < self.height):
        print(f"Warning: Center tile coordinates out of bounds: ({x}, {y})")
        return []
        
    visible_tiles = []
    
    # Check all tiles in a square around the center
    for dy in range(-vision_radius, vision_radius + 1):
        for dx in range(-vision_radius, vision_radius + 1):
            # Calculate target coordinates
            target_x = x + dx
            target_y = y + dy
            
            # Skip if out of bounds
            if not (0 <= target_x < self.width and 0 <= target_y < self.height):
                continue
                
            # Calculate Manhattan distance
            distance = abs(dx) + abs(dy)
            
            # Add tile if within vision radius and has line of sight
            if distance <= vision_radius and self.has_line_of_sight(center_tile, (target_x, target_y)):
                visible_tiles.append((target_x, target_y))
                
    return visible_tiles
    
  def has_line_of_sight(self, start, end):
    """
    Check if there's a clear line of sight between two tiles using Bresenham's line algorithm
    
    Args:
        start: Starting tile coordinates (x, y)
        end: Ending tile coordinates (x, y)
        
    Returns:
        bool: True if there's a clear line of sight
    """
    x0, y0 = start
    x1, y1 = end
    
    # Use Bresenham's line algorithm to check tiles between start and end
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    n = 1 + dx + dy
    x_inc = 1 if x1 > x0 else -1
    y_inc = 1 if y1 > y0 else -1
    error = dx - dy
    dx *= 2
    dy *= 2
    
    for _ in range(n):
        # Check if current tile blocks vision
        if not self.is_traversable((x, y)):
            # Don't block vision on the target tile
            if (x, y) != end:
                return False
            
        if error > 0:
            x += x_inc
            error -= dy
        else:
            y += y_inc
            error += dx
            
    return True
    
  # Add other methods like get_events_at, get_distance, etc.



































"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: perceive.py
Description: This defines the "Perceive" module for generative agents. 
"""
import sys
sys.path.append('../../')

from operator import itemgetter
from global_methods import *
from persona.prompt_template.gpt_structure import *
from persona.prompt_template.run_gpt_prompt import *

def generate_poig_score(persona, event_type, description): 
  if "is idle" in description: 
    return 1

  if event_type == "event": 
    return run_gpt_prompt_event_poignancy(persona, description)[0]
  elif event_type == "chat": 
    return run_gpt_prompt_chat_poignancy(persona, 
                           persona.scratch.act_description)[0]

def perceive(persona, maze): 
  """
  Perceive the environment and return perceived events
  """
  perceived_events = []
  percept_events_list = []
  
  # Get current location
  curr_tile = persona.scratch.curr_tile
  if not curr_tile:
    return []
  
  # Get all visible tiles within vision radius
  visible_tiles = maze.get_tiles_in_vision_range(curr_tile, 
                                               persona.scratch.vision_r)
  
  # Process each visible tile
  for tile in visible_tiles:
    # Get events at this tile
    events = maze.get_events_at(tile)
    for event in events:
      try:
        # Ensure event has all required components
        if isinstance(event, tuple) and len(event) >= 2:
          subject = event[0] if len(event) > 0 else ""
          predicate = event[1] if len(event) > 1 else ""
          obj = event[2] if len(event) > 2 else ""
          description = event[3] if len(event) > 3 else ""
          
          # Create standardized event tuple
          formatted_event = (subject, predicate, obj, description)
          
          # Calculate event distance and poignancy
          event_dist = maze.get_distance(curr_tile, tile)
          event_poignancy = calculate_event_poignancy(formatted_event)
          
          percept_events_list.append((event_dist, formatted_event))
          
      except Exception as e:
        print(f"Error processing event: {str(e)}")
        continue
  
  # Sort events by distance
  percept_events_list.sort(key=lambda x: x[0])
  
  # Process events within attention bandwidth
  for dist, event in percept_events_list[:persona.scratch.att_bandwidth]:
    try:
      s, p, o, desc = event  # Now this should work with the formatted event
      perceived_events.append(event)
      
      # Update importance triggers
      event_poignancy = calculate_event_poignancy((s, p, o, desc))
      persona.scratch.importance_trigger_curr -= event_poignancy
      persona.scratch.importance_ele_n += 1
      
    except Exception as e:
      print(f"Error processing perceived event: {str(e)}")
      continue
      
  return perceived_events




  












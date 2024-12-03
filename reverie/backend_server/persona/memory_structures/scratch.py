"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: scratch.py
Description: Defines the short-term memory module for generative agents.
"""
import datetime
import json
import sys
sys.path.append('../../')

from global_methods import *

class Scratch: 
  def __init__(self, saved_state=None):
    """
    Initialize the Scratch memory structure
    Args:
        saved_state: Optional dictionary containing saved scratch state
    """
    # First initialize defaults
    self._init_defaults()
    
    # Then load saved state if provided
    if saved_state:
      try:
        # If saved_state is a string (file path), load it
        if isinstance(saved_state, str):
          with open(saved_state, 'r') as f:
            saved_state = json.load(f)
        self._load_saved_state(saved_state)
      except Exception as e:
        print(f"Error loading saved state: {str(e)}")
        self._init_defaults()
      
  def _init_defaults(self):
    """Initialize all default values"""
    # Time tracking
    self.curr_time = None
    
    # Schedule tracking
    self.daily_schedule = []
    self.daily_schedule_hourly_org = []
    self.curr_schedule_step = 0
    
    # Current state
    self.curr_tile = None
    self.curr_event = None
    self.curr_event_description = None
    self.curr_obj_event = None
    self.curr_obj_event_description = None
    
    # Path planning
    self.planned_path = []
    self.curr_path_step = 0
    
    # Vision and perception
    self.vision_r = 4  # Default vision radius
    self.att_bandwidth = 3  # Default attention bandwidth
    self.retention = 5  # Default retention span
    self.perceived_tiles = set()
    self.perceived_objects = {}
    self.perceived_events = []
    self.recent_memories = []  # Store recent memories within retention span
    
    # Importance triggers
    self.importance_trigger_max = 10.0  # Maximum importance trigger value
    self.importance_trigger_curr = 10.0  # Current importance trigger value
    self.importance_trigger_decay = 0.1  # Rate at which importance decays
    self.importance_ele_n = 0  # Number of important elements perceived
    
    # Chat state
    self.chatting_with = None
    self.chatting_with_buffer = {}
    self.chat = None
    
    # Basic identity
    self.name = None
    self.first_name = None
    self.last_name = None
    self.full_name = None
    
    # Current activity/event
    self.act_event = None  # Initialize act_event
    self.act_address = None  # Current activity location/address
    
  def _load_saved_state(self, saved_state):
    """Load state from saved dictionary"""
    try:
      # Load time if exists
      if "curr_time" in saved_state and saved_state["curr_time"]:
        self.curr_time = datetime.datetime.strptime(
          saved_state["curr_time"], 
          "%B %d, %Y, %H:%M:%S"
        )
      
      # Load schedule data
      self.daily_schedule = saved_state.get("daily_schedule", [])
      self.daily_schedule_hourly_org = saved_state.get("daily_schedule_hourly_org", [])
      self.curr_schedule_step = saved_state.get("curr_schedule_step", 0)
      
      # Load current state
      self.curr_tile = saved_state.get("curr_tile", None)
      self.curr_event = saved_state.get("curr_event", None)
      self.curr_event_description = saved_state.get("curr_event_description", None)
      self.curr_obj_event = saved_state.get("curr_obj_event", None)
      self.curr_obj_event_description = saved_state.get("curr_obj_event_description", None)
      
      # Load path planning
      self.planned_path = saved_state.get("planned_path", [])
      self.curr_path_step = saved_state.get("curr_path_step", 0)
      
      # Load vision and perception
      self.vision_r = saved_state.get("vision_r", 4)
      self.att_bandwidth = saved_state.get("att_bandwidth", 3)
      self.retention = saved_state.get("retention", 5)
      self.perceived_tiles = set(saved_state.get("perceived_tiles", []))
      self.perceived_objects = saved_state.get("perceived_objects", {})
      self.perceived_events = saved_state.get("perceived_events", [])
      self.recent_memories = saved_state.get("recent_memories", [])
      
      # Load importance triggers
      self.importance_trigger_max = saved_state.get("importance_trigger_max", 10.0)
      self.importance_trigger_curr = saved_state.get("importance_trigger_curr", 10.0)
      self.importance_trigger_decay = saved_state.get("importance_trigger_decay", 0.1)
      self.importance_ele_n = saved_state.get("importance_ele_n", 0)
      
      # Load chat state
      self.chatting_with = saved_state.get("chatting_with", None)
      self.chatting_with_buffer = saved_state.get("chatting_with_buffer", {})
      self.chat = saved_state.get("chat", None)
      
      # Load identity information
      self.name = saved_state.get("name")
      self.first_name = saved_state.get("first_name")
      self.last_name = saved_state.get("last_name")
      self.full_name = saved_state.get("full_name")
      
      # Load current activity/event
      self.act_event = saved_state.get("act_event", None)
      self.act_address = saved_state.get("act_address", None)
      
    except Exception as e:
      print(f"Error loading saved state: {str(e)}")
      self._init_defaults()

  def get_curr_event_and_desc(self):
    """
    Get the current event and description
    Returns:
        tuple: (current_event, current_event_description)
    """
    return (self.curr_event or "", self.curr_event_description or "")
    
  def get_curr_obj_event_and_desc(self):
    """
    Get the current object event and description
    Returns:
        tuple: (current_obj_event, current_obj_event_description)
    """
    return (self.curr_obj_event or "", self.curr_obj_event_description or "")
    
  def save(self, save_file):
    """Save the current state with proper attribute checking"""
    try:
      # Ensure all required attributes exist
      if not hasattr(self, 'daily_schedule'):
        self._init_defaults()
        
      save_dict = {
        "curr_time": self.curr_time.strftime("%B %d, %Y, %H:%M:%S") if self.curr_time else None,
        "daily_schedule": self.daily_schedule,
        "daily_schedule_hourly_org": self.daily_schedule_hourly_org,
        "curr_schedule_step": self.curr_schedule_step,
        "curr_tile": self.curr_tile,
        "curr_event": self.curr_event,
        "curr_event_description": self.curr_event_description,
        "curr_obj_event": self.curr_obj_event,
        "curr_obj_event_description": self.curr_obj_event_description,
        "planned_path": self.planned_path,
        "curr_path_step": self.curr_path_step,
        "vision_r": self.vision_r,
        "att_bandwidth": self.att_bandwidth,
        "retention": self.retention,
        "perceived_tiles": list(self.perceived_tiles),
        "perceived_objects": self.perceived_objects,
        "perceived_events": self.perceived_events,
        "recent_memories": self.recent_memories,
        "importance_trigger_max": self.importance_trigger_max,
        "importance_trigger_curr": self.importance_trigger_curr,
        "importance_trigger_decay": self.importance_trigger_decay,
        "importance_ele_n": self.importance_ele_n,
        "chatting_with": self.chatting_with,
        "chatting_with_buffer": self.chatting_with_buffer,
        "chat": self.chat,
        "name": self.name,
        "first_name": self.first_name,
        "last_name": self.last_name,
        "full_name": self.full_name,
        "act_event": self.act_event,
        "act_address": self.act_address
      }
      
      with open(save_file, "w") as outfile:
        json.dump(save_dict, outfile, indent=2)
        
    except Exception as e:
      print(f"Error saving scratch memory: {str(e)}")
      # Fallback save state
      fallback_save = {
        "curr_time": None,
        "daily_schedule": [],
        "daily_schedule_hourly_org": [],
        "curr_schedule_step": 0,
        "curr_tile": None,
        "curr_event": None,
        "curr_event_description": None,
        "curr_obj_event": None,
        "curr_obj_event_description": None,
        "planned_path": [],
        "curr_path_step": 0,
        "vision_r": 4,
        "att_bandwidth": 3,
        "retention": 5,
        "perceived_tiles": [],
        "perceived_objects": {},
        "perceived_events": [],
        "recent_memories": [],
        "importance_trigger_max": 10.0,
        "importance_trigger_curr": 10.0,
        "importance_trigger_decay": 0.1,
        "importance_ele_n": 0,
        "chatting_with": None,
        "chatting_with_buffer": {},
        "chat": None,
        "name": None,
        "first_name": None,
        "last_name": None,
        "full_name": None,
        "act_event": None,
        "act_address": None
      }
      with open(save_file, "w") as outfile:
        json.dump(fallback_save, outfile, indent=2)

  def get_str_iss(self):
    """
    Get a string representation of the current inner state status (ISS)
    
    Returns:
        str: A description of the current inner state
    """
    # Get current time string
    time_str = self.curr_time.strftime("%B %d, %Y, %H:%M:%S") if self.curr_time else "Unknown time"
    
    # Get current location
    location = f"({self.curr_tile[0]}, {self.curr_tile[1]})" if self.curr_tile else "Unknown location"
    
    # Get current event
    curr_event, curr_desc = self.get_curr_event_and_desc()
    event_str = f"{curr_event}: {curr_desc}" if curr_event else "No current event"
    
    # Format the inner state string
    iss = f"""Current time: {time_str}
Location: {location}
Current activity: {event_str}
"""
    
    # Add chat state if exists
    if self.chatting_with:
        chat_str = f"Currently chatting with: {self.chatting_with}"
        if self.chat:
            chat_str += f"\nChat context: {self.chat}"
        iss += chat_str
        
    # Add any perceived events
    if self.perceived_events:
        iss += "\nRecently perceived events:"
        for event in self.perceived_events[-5:]:  # Show last 5 events
            if isinstance(event, tuple):
                event_desc = " ".join(str(x) for x in event if x)
                iss += f"\n- {event_desc}"
                
    # Add any recent memories
    if self.recent_memories:
        iss += "\nRecent memories:"
        for memory in self.recent_memories[-3:]:  # Show last 3 memories
            iss += f"\n- {memory}"
            
    return iss

  def get_str_lifestyle(self):
    """
    Get a string representation of the persona's lifestyle and daily patterns
    
    Returns:
        str: A description of the persona's lifestyle
    """
    lifestyle = "Daily Schedule and Lifestyle:\n"
    
    # Add daily schedule if available
    if self.daily_schedule:
        lifestyle += "Typical daily activities:\n"
        for i, activity in enumerate(self.daily_schedule):
            if isinstance(activity, dict):
                start_time = activity.get('start_time', 'Unknown')
                end_time = activity.get('end_time', 'Unknown')
                description = activity.get('description', 'Unknown activity')
                lifestyle += f"- {start_time}-{end_time}: {description}\n"
            else:
                lifestyle += f"- Activity {i+1}: {activity}\n"
    else:
        lifestyle += "No regular daily schedule recorded\n"
        
    # Add hourly organization if available
    if self.daily_schedule_hourly_org:
        lifestyle += "\nHourly breakdown:\n"
        for hour, activities in enumerate(self.daily_schedule_hourly_org):
            if activities:
                if isinstance(activities, list):
                    act_str = ", ".join(str(a) for a in activities)
                else:
                    act_str = str(activities)
                lifestyle += f"{hour:02d}:00 - {act_str}\n"
                
    # Add current schedule step
    lifestyle += f"\nCurrent schedule progress: Step {self.curr_schedule_step}\n"
    
    # Add any recurring patterns or preferences
    if hasattr(self, 'wake_up_hour'):
        lifestyle += f"Typical wake-up time: {self.wake_up_hour:02d}:00\n"
    if hasattr(self, 'sleep_hour'):
        lifestyle += f"Typical bedtime: {self.sleep_hour:02d}:00\n"
        
    # Add any special routines or preferences
    if hasattr(self, 'routines'):
        lifestyle += "\nRegular routines:\n"
        for routine in self.routines:
            lifestyle += f"- {routine}\n"
            
    return lifestyle

  def get_str_firstname(self):
    """
    Get the first name of the persona
    
    Returns:
        str: The first name, or full name if first name cannot be determined
    """
    # Try to get the name from various possible attributes
    name = None
    
    # Check if we have a first_name attribute
    if hasattr(self, 'first_name'):
        name = self.first_name
    # Check if we have a full_name attribute
    elif hasattr(self, 'full_name'):
        # Try to split the full name and get the first part
        name = self.full_name.split()[0]
    # Check if we have a name attribute
    elif hasattr(self, 'name'):
        # Try to split the name and get the first part
        name = self.name.split()[0]
        
    # If we still don't have a name, try to get it from current events
    if not name:
        curr_event = self.get_curr_event_and_desc()[0]
        if curr_event and isinstance(curr_event, str):
            # Try to extract name from event if it starts with a name
            possible_name = curr_event.split()[0]
            if possible_name.isalpha():  # Check if it's a word (not numbers/symbols)
                name = possible_name
                
    # If we still don't have a name, return a default
    if not name:
        name = "Unknown"
        
    return name

  def get_str_curr_date_str(self):
    """
    Get a string representation of the current date
    
    Returns:
        str: The current date in a readable format
    """
    if not self.curr_time:
        return "Unknown date"
        
    try:
        # Format the date in a natural way
        # Example: "Monday, January 1st, 2024"
        
        # Get day suffix (1st, 2nd, 3rd, etc.)
        day = self.curr_time.day
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            
        # Format the full date string
        date_str = self.curr_time.strftime(f"%A, %B {day}{suffix}, %Y")
        
        # Add time of day context
        hour = self.curr_time.hour
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 22:
            time_of_day = "evening"
        else:
            time_of_day = "night"
            
        # Combine date and time of day
        return f"{date_str} ({time_of_day})"
        
    except Exception as e:
        print(f"Error formatting date: {str(e)}")
        # Fallback to basic format
        return self.curr_time.strftime("%B %d, %Y")

  def act_check_finished(self):
    """
    Check if the current activity is finished based on the schedule
    
    Returns:
        bool: True if the current activity is finished, False otherwise
    """
    if not self.curr_time or not self.daily_schedule:
        return False
    
    # Get the current hour
    current_hour = self.curr_time.hour
    
    # Check if the current schedule step is valid
    if 0 <= self.curr_schedule_step < len(self.daily_schedule):
        current_activity = self.daily_schedule[self.curr_schedule_step]
        
        # Check if the activity has an end time
        if isinstance(current_activity, dict) and 'end_time' in current_activity:
            end_time = current_activity['end_time']
            
            # Convert end_time to an integer hour if it's a string
            if isinstance(end_time, str):
                try:
                    end_hour = int(end_time.split(':')[0])
                except ValueError:
                    print(f"Error parsing end_time: {end_time}")
                    return False
            else:
                end_hour = end_time
            
            # Check if the current hour is past the end time
            return current_hour >= end_hour
    
    return False





















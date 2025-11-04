"""
Database Manager for Activity Tracker Calendar
Handles all database operations for storing and retrieving activity data
"""

import json
import os
from datetime import datetime

class DatabaseManager:
    """Manages database operations for the Activity Tracker application"""
    
    def __init__(self, db_path=None):
        """Initialize database manager with optional custom path"""
        self.activities_file = db_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), "activity_tracker_data.json")
        self.journal_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), "journal_data.json")
        
        # Initialize database files if they don't exist
        self._initialize_db()
    
    def _initialize_db(self):
        """Create database files if they don't exist"""
        # Activities database
        if not os.path.exists(self.activities_file):
            with open(self.activities_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "categories": [
                        {"id": 1, "name": "Sport", "color": "#FF5733"},
                        {"id": 2, "name": "Lecture", "color": "#33A8FF"},
                        {"id": 3, "name": "Méditation", "color": "#B033FF"},
                        {"id": 4, "name": "Travail", "color": "#33FF57"}
                    ],
                    "activities": []
                }, f, ensure_ascii=False, indent=4)
        
        # Journal database
        if not os.path.exists(self.journal_file):
            with open(self.journal_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "journal_entries": []
                }, f, ensure_ascii=False, indent=4)
    
    def get_categories(self):
        """Get all activity categories"""
        with open(self.activities_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("categories", [])
    
    def add_category(self, name, color):
        """Add a new activity category"""
        with open(self.activities_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Generate new ID
        new_id = 1
        if data["categories"]:
            new_id = max(cat["id"] for cat in data["categories"]) + 1
        
        # Add new category
        data["categories"].append({
            "id": new_id,
            "name": name,
            "color": color
        })
        
        # Save changes
        with open(self.activities_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return new_id
    
    def delete_category(self, category_id):
        """Delete a category by ID"""
        with open(self.activities_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter out the category to delete
        data["categories"] = [c for c in data["categories"] if c["id"] != category_id]
        
        # Save changes
        with open(self.activities_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return True
    
    def get_activities(self, start_date=None, end_date=None, category_id=None):
        """Get activities with optional filters"""
        with open(self.activities_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        activities = data.get("activities", [])
        
        # Apply filters
        if start_date:
            activities = [a for a in activities if a["date"] >= start_date]
        if end_date:
            activities = [a for a in activities if a["date"] <= end_date]
        if category_id is not None:
            activities = [a for a in activities if a["category_id"] == category_id]
        
        return activities
    
    def add_activity(self, title, category_id, date, duration, notes=""):
        """Add a new activity entry"""
        with open(self.activities_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Generate new ID
        new_id = 1
        if data["activities"]:
            new_id = max(act["id"] for act in data["activities"]) + 1
        
        # Add new activity
        data["activities"].append({
            "id": new_id,
            "title": title,
            "category_id": category_id,
            "date": date,
            "duration": duration,
            "notes": notes
        })
        
        # Save changes
        with open(self.activities_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return new_id
    
    def update_activity(self, activity_id, title, category_id, duration, notes=""):
        """Update an existing activity"""
        with open(self.activities_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Find activity by ID
        for activity in data["activities"]:
            if activity["id"] == activity_id:
                # Update fields
                activity["title"] = title
                activity["category_id"] = category_id
                activity["duration"] = duration
                activity["notes"] = notes
                break
        
        # Save changes
        with open(self.activities_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return True
    
    def delete_activity(self, activity_id):
        """Delete an activity by ID"""
        with open(self.activities_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter out the activity to delete
        data["activities"] = [a for a in data["activities"] if a["id"] != activity_id]
        
        # Save changes
        with open(self.activities_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return True
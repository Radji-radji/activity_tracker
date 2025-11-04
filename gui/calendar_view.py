"""
Calendar View for Activity Tracker
Provides an interactive calendar interface for visualizing and managing activities
"""

import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime, timedelta

class CalendarView(ttk.Frame):
    """Interactive calendar widget for activity tracking"""
    
    def __init__(self, parent, db_manager, **kwargs):
        """Initialize calendar view with database manager"""
        super().__init__(parent, **kwargs)
        self.db_manager = db_manager
        self.today = datetime.now()
        self.current_date = datetime.now()
        self.selected_date = None
        self.activity_callback = None
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('Calendar.TFrame', background='white')
        self.style.configure('CalendarHeader.TLabel', 
                            font=('Arial', 12, 'bold'),
                            background='#3366CC', 
                            foreground='white',
                            padding=5)
        self.style.configure('CalendarDay.TLabel', 
                            font=('Arial', 10),
                            background='white',
                            padding=2)
        self.style.configure('CalendarToday.TLabel', 
                            font=('Arial', 10, 'bold'),
                            background='#E6F0FF',
                            padding=2)
        self.style.configure('CalendarSelected.TLabel', 
                            font=('Arial', 10, 'bold'),
                            background='#3366CC',
                            foreground='white',
                            padding=2)
        
        # Create calendar layout
        self._create_widgets()
        self._update_calendar()
    
    def _create_widgets(self):
        """Create calendar UI components"""
        # Calendar header with navigation
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', padx=5, pady=5)
        
        # Previous month button
        self.prev_btn = ttk.Button(header_frame, text="<", width=3, 
                                  command=self._prev_month)
        self.prev_btn.pack(side='left', padx=5)
        
        # Month/Year label
        self.header_label = ttk.Label(header_frame, style='CalendarHeader.TLabel')
        self.header_label.pack(side='left', fill='x', expand=True)
        
        # Next month button
        self.next_btn = ttk.Button(header_frame, text=">", width=3,
                                  command=self._next_month)
        self.next_btn.pack(side='right', padx=5)
        
        # Days of week header
        days_frame = ttk.Frame(self)
        days_frame.pack(fill='x', padx=5)
        
        for i, day in enumerate(['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']):
            lbl = ttk.Label(days_frame, text=day, anchor='center', width=4,
                           style='CalendarHeader.TLabel')
            lbl.grid(row=0, column=i, sticky='nsew', padx=1, pady=1)
        
        # Calendar grid for days
        self.calendar_frame = ttk.Frame(self, style='Calendar.TFrame')
        self.calendar_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create 6 rows x 7 columns grid for calendar days
        self.day_labels = []
        for row in range(6):
            for col in range(7):
                frame = ttk.Frame(self.calendar_frame, borderwidth=1, relief='solid')
                frame.grid(row=row, column=col, sticky='nsew', padx=1, pady=1)
                
                # Day number label
                day_label = ttk.Label(frame, text="", anchor='nw', 
                                     style='CalendarDay.TLabel')
                day_label.pack(side='top', fill='both', expand=True)
                
                # Activity indicator frame
                indicator_frame = ttk.Frame(frame)
                indicator_frame.pack(side='bottom', fill='x', padx=2, pady=2)
                
                self.day_labels.append({
                    'frame': frame,
                    'label': day_label,
                    'indicator': indicator_frame,
                    'date': None
                })
        
        # Make grid cells expandable
        for i in range(7):
            self.calendar_frame.columnconfigure(i, weight=1)
        for i in range(6):
            self.calendar_frame.rowconfigure(i, weight=1)
    
    def _update_calendar(self):
        """Update calendar display for current month"""
        # Update header with month and year
        month_name = self.current_date.strftime("%B %Y")
        self.header_label.config(text=month_name.capitalize())
        
        # Get calendar for current month
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # Clear previous indicators
        for day_item in self.day_labels:
            for widget in day_item['indicator'].winfo_children():
                widget.destroy()
            day_item['label'].config(text="", style='CalendarDay.TLabel')
            day_item['date'] = None
        
        # Fill calendar with days
        day_index = 0
        for week in cal:
            for day in week:
                day_item = self.day_labels[day_index]
                
                if day != 0:
                    # Set date for this cell
                    cell_date = datetime(self.current_date.year, 
                                        self.current_date.month, day)
                    day_item['date'] = cell_date
                    day_item['label'].config(text=str(day))
                    
                    # Check if this is today
                    if (cell_date.year == self.today.year and 
                        cell_date.month == self.today.month and 
                        cell_date.day == self.today.day):
                        day_item['label'].config(style='CalendarToday.TLabel')
                    
                    # Check if this is selected date
                    if (self.selected_date and
                        cell_date.year == self.selected_date.year and 
                        cell_date.month == self.selected_date.month and 
                        cell_date.day == self.selected_date.day):
                        day_item['label'].config(style='CalendarSelected.TLabel')
                    
                    # Add click event
                    day_item['label'].bind('<Button-1>', 
                                         lambda e, d=cell_date: self._on_date_click(d))
                    
                    # Add activity indicators
                    self._add_activity_indicators(day_item)
                
                day_index += 1
    
    def _add_activity_indicators(self, day_item):
        """Add colored indicators for activities on this day"""
        if not day_item['date']:
            return
            
        # Format date for database query
        date_str = day_item['date'].strftime("%Y-%m-%d")
        
        # Get activities for this day
        activities = self.db_manager.get_activities(
            start_date=date_str, 
            end_date=date_str
        )
        
        # Get categories for color mapping
        categories = {cat["id"]: cat for cat in self.db_manager.get_categories()}
        
        # Group activities by category
        by_category = {}
        for activity in activities:
            cat_id = activity["category_id"]
            if cat_id not in by_category:
                by_category[cat_id] = []
            by_category[cat_id].append(activity)
        
        # Add indicator for each category
        for cat_id, acts in by_category.items():
            if cat_id in categories:
                color = categories[cat_id]["color"]
                indicator = tk.Frame(day_item['indicator'], 
                                    background=color,
                                    width=8, height=4)
                indicator.pack(side='left', padx=1)
    
    def _prev_month(self):
        """Go to previous month"""
        year = self.current_date.year
        month = self.current_date.month - 1
        
        if month < 1:
            month = 12
            year -= 1
            
        self.current_date = datetime(year, month, 1)
        self._update_calendar()
    
    def _next_month(self):
        """Go to next month"""
        year = self.current_date.year
        month = self.current_date.month + 1
        
        if month > 12:
            month = 1
            year += 1
            
        self.current_date = datetime(year, month, 1)
        self._update_calendar()
    
    def _on_date_click(self, date):
        """Handle date selection"""
        self.selected_date = date
        self._update_calendar()
        
        # Call callback if registered
        if self.activity_callback:
            self.activity_callback(date)
    
    def set_activity_callback(self, callback):
        """Set callback function for date selection"""
        self.activity_callback = callback
    
    def refresh(self):
        """Refresh calendar view"""
        self._update_calendar()
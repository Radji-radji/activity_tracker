"""
Activity Tracker Calendar - Main Application
A comprehensive activity tracking application with calendar interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
import sys
import os

# Import local modules using absolute imports
from database.db_manager import DatabaseManager
from gui.calendar_view import CalendarView
from utils.validators import *


class MainWindow:
    """Main application window"""
    
    def __init__(self, root):
        """Initialize main window"""
        self.root = root
        self.root.title("Activity Tracker Calendar")
        self.root.geometry("1200x800")
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Create main interface
        self._create_menu()
        self._create_main_layout()
        
        # Load initial data
        self._load_categories()
        self._refresh_all()
    
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Categories menu
        cat_menu = tk.Menu(menubar, tearoff=0)
        cat_menu.add_command(label="Manage categories", command=self._manage_categories)
        menubar.add_cascade(label="Categories", menu=cat_menu)
        
        # Statistics menu
        stats_menu = tk.Menu(menubar, tearoff=0)
        stats_menu.add_command(label="View statistics", command=self._show_statistics)
        menubar.add_cascade(label="Statistics", menu=stats_menu)
    
    def _create_main_layout(self):
        """Create main application layout"""
        # Main container with two panels
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Calendar
        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=2)
        
        # Calendar view
        self.calendar = CalendarView(left_frame, self.db)
        self.calendar.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.calendar.set_activity_callback(self._on_date_selected)
        
        # Right panel - Activity details
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=1)
        
        # Selected date label
        self.date_label = ttk.Label(right_frame, text="No date selected", 
                                   font=('Arial', 14, 'bold'))
        self.date_label.pack(fill=tk.X, padx=5, pady=10)
        
        # Activities for selected date
        activities_frame = ttk.LabelFrame(right_frame, text="Activities")
        activities_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Activities list
        self.activities_list = ttk.Treeview(activities_frame, 
                                           columns=('title', 'category', 'duration'),
                                           show='headings')
        self.activities_list.heading('title', text='Title')
        self.activities_list.heading('category', text='Category')
        self.activities_list.heading('duration', text='Duration (min)')
        self.activities_list.column('title', width=150)
        self.activities_list.column('category', width=100)
        self.activities_list.column('duration', width=80)
        self.activities_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for activities list
        scrollbar = ttk.Scrollbar(self.activities_list, orient=tk.VERTICAL, 
                                 command=self.activities_list.yview)
        self.activities_list.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Activity buttons
        btn_frame = ttk.Frame(activities_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Add", command=self._add_activity).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit", command=self._edit_activity).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", command=self._delete_activity).pack(side=tk.LEFT, padx=5)
    
    def _load_categories(self):
        """Load activity categories"""
        self.categories = self.db.get_categories()
        self.category_map = {cat["id"]: cat for cat in self.categories}
    
    def _on_date_selected(self, date):
        """Handle date selection in calendar"""
        # Update date label
        self.date_label.config(text=date.strftime("%A %d %B %Y").capitalize())
        
        # Store the selected date for use in other functions
        self.selected_date = date
        
        # Load activities for this date
        self._load_activities(date)
    
    def _load_activities(self, date):
        """Load activities for selected date"""
        # Clear current list
        for item in self.activities_list.get_children():
            self.activities_list.delete(item)
        
        # Format date for database query
        date_str = date.strftime("%Y-%m-%d")
        
        # Get activities for this day
        activities = self.db.get_activities(start_date=date_str, end_date=date_str)
        
        # Add to list
        for activity in activities:
            category_name = "Inconnu"
            if activity["category_id"] in self.category_map:
                category_name = self.category_map[activity["category_id"]]["name"]
            
            self.activities_list.insert('', 'end', 
                                       values=(activity["title"], 
                                              category_name, 
                                              activity["duration"]),
                                       tags=(str(activity["id"]),))
    
    def _add_activity(self):
        """Add new activity"""
        # Check if a date is selected
        if not hasattr(self, 'selected_date') or not self.selected_date:
            messagebox.showwarning("Warning", "Please select a date first.")
            return
        
        # Create activity dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add an activity")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form fields
        ttk.Label(dialog, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        title_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=title_var, width=30).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Category:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        category_var = tk.StringVar()
        category_cb = ttk.Combobox(dialog, textvariable=category_var, width=28)
        category_cb.grid(row=1, column=1, padx=10, pady=5)
        
        # Fill categories dropdown
        categories = self.db.get_categories()
        category_cb['values'] = [cat["name"] for cat in categories]
        if categories:
            category_cb.current(0)
        
        ttk.Label(dialog, text="Duration (minutes):").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        duration_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=duration_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(dialog, text="Notes:").grid(row=3, column=0, sticky=tk.NW, padx=10, pady=5)
        notes_text = scrolledtext.ScrolledText(dialog, width=30, height=5)
        notes_text.grid(row=3, column=1, padx=10, pady=5)
        
        # Save button
        def save_activity():
            # Validate inputs
            title = sanitize_input(title_var.get())
            if not title:
                messagebox.showwarning("Error", "Title is required.")
                return
            
            try:
                duration = int(duration_var.get())
                if duration <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showwarning("Error", "Duration must be a positive number.")
                return
            
            # Get category ID
            cat_name = category_var.get()
            cat_id = None
            for cat in categories:
                if cat["name"] == cat_name:
                    cat_id = cat["id"]
                    break
            
            if cat_id is None:
                messagebox.showwarning("Error", "Invalid category.")
                return
            
            # Format date
            date_str = self.selected_date.strftime("%Y-%m-%d")
            
            # Add activity
            self.db.add_activity(
                title=title,
                category_id=cat_id,
                date=date_str,
                duration=duration,
                notes=notes_text.get("1.0", tk.END).strip()
            )
            
            # Refresh view
            self._load_activities(self.selected_date)
            self.calendar.refresh()
            
            # Close dialog
            dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save_activity).grid(row=4, column=1, sticky=tk.E, padx=10, pady=10)
    
    def _edit_activity(self):
        """Edit selected activity"""
        # Check if an activity is selected
        selected_items = self.activities_list.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select an activity to edit.")
            return
        
        # Get selected activity ID
        selected_item = selected_items[0]
        activity_id = int(self.activities_list.item(selected_item, "tags")[0])
        
        # Get activity data
        activities = self.db.get_activities()
        activity = next((a for a in activities if a["id"] == activity_id), None)
        
        if not activity:
            messagebox.showerror("Error", "Activity not found.")
            return
        
        # Create edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit activity")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form fields
        ttk.Label(dialog, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        title_var = tk.StringVar(value=activity["title"])
        ttk.Entry(dialog, textvariable=title_var, width=30).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Category:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        category_var = tk.StringVar()
        category_cb = ttk.Combobox(dialog, textvariable=category_var, width=28)
        category_cb.grid(row=1, column=1, padx=10, pady=5)
        
        # Fill categories dropdown
        categories = self.db.get_categories()
        category_cb['values'] = [cat["name"] for cat in categories]
        
        # Set current category
        for i, cat in enumerate(categories):
            if cat["id"] == activity["category_id"]:
                category_cb.current(i)
                break
        
        ttk.Label(dialog, text="Duration (minutes):").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        duration_var = tk.StringVar(value=str(activity["duration"]))
        ttk.Entry(dialog, textvariable=duration_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(dialog, text="Notes:").grid(row=3, column=0, sticky=tk.NW, padx=10, pady=5)
        notes_text = scrolledtext.ScrolledText(dialog, width=30, height=5)
        notes_text.grid(row=3, column=1, padx=10, pady=5)
        notes_text.insert("1.0", activity.get("notes", ""))
        
        # Save button
        def save_activity():
            # Validate inputs
            title = sanitize_input(title_var.get())
            if not title:
                messagebox.showwarning("Error", "Title is required.")
                return
            
            try:
                duration = int(duration_var.get())
                if duration <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showwarning("Error", "Duration must be a positive number.")
                return
            
            # Get category ID
            cat_name = category_var.get()
            cat_id = None
            for cat in categories:
                if cat["name"] == cat_name:
                    cat_id = cat["id"]
                    break
            
            if cat_id is None:
                messagebox.showwarning("Error", "Invalid category.")
                return
            
            # Update activity
            self.db.update_activity(
                activity_id=activity_id,
                title=title,
                category_id=cat_id,
                duration=duration,
                notes=notes_text.get("1.0", tk.END).strip()
            )
            
            # Refresh view
            self._load_activities(self.selected_date)
            self.calendar.refresh()
            
            # Close dialog
            dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save_activity).grid(row=4, column=1, sticky=tk.E, padx=10, pady=10)
    
    def _delete_activity(self):
        """Delete selected activity"""
        # Check if an activity is selected
        selected_items = self.activities_list.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select an activity to delete.")
            return
        
        # Get selected activity ID
        selected_item = selected_items[0]
        activity_id = int(self.activities_list.item(selected_item, "tags")[0])
        
        # Confirm deletion
        if messagebox.askyesno("Confirmation", "Are you sure you want to delete this activity?"):
            # Delete activity
            self.db.delete_activity(activity_id)
            
            # Refresh view
            self._load_activities(self.selected_date)
            self.calendar.refresh()
    
    def _manage_categories(self):
        """Open category management dialog"""
        # Create category management dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Category Management")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Categories list
        ttk.Label(dialog, text="Existing categories:", font=('Arial', 11)).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Create treeview for categories
        columns = ('name', 'color')
        cat_tree = ttk.Treeview(dialog, columns=columns, show='headings', height=10)
        cat_tree.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=tk.NSEW)
        
        # Configure columns
        cat_tree.heading('name', text='Name')
        cat_tree.heading('color', text='Color')
        cat_tree.column('name', width=200)
        cat_tree.column('color', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=cat_tree.yview)
        cat_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky=tk.NS, pady=5)
        
        # Load categories
        def load_categories():
            # Clear current list
            for item in cat_tree.get_children():
                cat_tree.delete(item)
            
            # Get categories
            categories = self.db.get_categories()
            
            # Add to list
            for cat in categories:
                cat_tree.insert('', 'end', values=(cat["name"], cat["color"]), tags=(str(cat["id"]),))
                
                # Add color preview
                cat_tree.tag_configure(str(cat["id"]), background=cat["color"])
        
        # Load initial categories
        load_categories()
        
        # Add new category frame
        add_frame = ttk.LabelFrame(dialog, text="Add a category")
        add_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky=tk.EW)
        
        ttk.Label(add_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=name_var, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Color:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        color_var = tk.StringVar(value="#3366FF")
        color_entry = ttk.Entry(add_frame, textvariable=color_var, width=10)
        color_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Color preview
        color_preview = tk.Canvas(add_frame, width=20, height=20, bg=color_var.get())
        color_preview.grid(row=0, column=4, padx=5, pady=5)
        
        # Update color preview when color changes
        def update_preview(*args):
            try:
                color = color_var.get()
                if validate_hex_color(color):
                    color_preview.config(bg=color)
            except:
                pass
        
        color_var.trace("w", update_preview)
        
        # Add category button
        def add_category():
            name = sanitize_input(name_var.get())
            color = color_var.get()
            
            if not name:
                messagebox.showwarning("Error", "Category name is required.")
                return
                
            if not validate_hex_color(color):
                messagebox.showwarning("Error", "Color must be in hexadecimal format (e.g., #FF5733).")
                return
            
            # Add category
            self.db.add_category(name, color)
            
            # Refresh list
            load_categories()
            
            # Clear inputs
            name_var.set("")
            color_var.set("#3366FF")
            update_preview()
            
            # Refresh main window
            self._load_categories()
            self.calendar.refresh()
            
            messagebox.showinfo("Success", "Category added successfully.")
        
        ttk.Button(add_frame, text="Add", command=add_category).grid(row=0, column=5, padx=5, pady=5)
        
        # Delete category button
        def delete_category():
            selected = cat_tree.selection()
            if not selected:
                messagebox.showwarning("Attention", "Veuillez sélectionner une catégorie à supprimer.")
                return
            
            # Get category ID
            cat_id = int(cat_tree.item(selected[0], "tags")[0])
            
            # Check if category is used
            activities = self.db.get_activities(category_id=cat_id)
            if activities:
                messagebox.showwarning("Attention", 
                                     f"Cette catégorie est utilisée par {len(activities)} activité(s).\n"
                                     "Veuillez d'abord supprimer ou modifier ces activités.")
                return
            
            # Confirm deletion
            if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette catégorie ?"):
                # Delete category
                self.db.delete_category(cat_id)
                
                # Refresh list
                load_categories()
                
                # Refresh main window
                self._load_categories()
                self.calendar.refresh()
        
        # Buttons frame
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky=tk.E)
        
        ttk.Button(btn_frame, text="Delete", command=delete_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _show_statistics(self):
        """Show activity statistics"""
        # Import matplotlib
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import numpy as np
        
        # Create statistics dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Activity Statistics")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Get all activities
        activities = self.db.get_activities()
        categories = self.db.get_categories()
        cat_map = {cat["id"]: cat for cat in categories}
        
        # Create notebook for tabs
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Summary statistics
        summary_frame = ttk.Frame(notebook)
        notebook.add(summary_frame, text="Summary")
        
        # Calculate summary statistics
        total_activities = len(activities)
        total_duration = sum(act["duration"] for act in activities)
        
        # Group by category
        cat_stats = {}
        for act in activities:
            cat_id = act["category_id"]
            if cat_id not in cat_stats:
                cat_stats[cat_id] = {"count": 0, "duration": 0}
            cat_stats[cat_id]["count"] += 1
            cat_stats[cat_id]["duration"] += act["duration"]
        
        # Display summary
        ttk.Label(summary_frame, text="Global Statistics", font=('Arial', 12, 'bold')).pack(pady=10)
        
        summary_text = f"Total number of activities: {total_activities}\n"
        summary_text += f"Total duration: {total_duration} minutes ({total_duration//60} hours and {total_duration%60} minutes)\n\n"
        summary_text += "Distribution by category:\n"
        
        for cat_id, stats in cat_stats.items():
            cat_name = "Unknown"
            if cat_id in cat_map:
                cat_name = cat_map[cat_id]["name"]
            
            percent = (stats["duration"] / total_duration * 100) if total_duration > 0 else 0
            summary_text += f"- {cat_name}: {stats['count']} activities, {stats['duration']} minutes ({percent:.1f}%)\n"
        
        summary_box = scrolledtext.ScrolledText(summary_frame, width=60, height=15)
        summary_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        summary_box.insert("1.0", summary_text)
        summary_box.config(state=tk.DISABLED)
        
        # Tab 2: Pie Chart
        pie_frame = ttk.Frame(notebook)
        notebook.add(pie_frame, text="Pie Chart")
        
        if total_duration > 0:
            # Create figure for pie chart
            fig_pie = plt.Figure(figsize=(6, 5))
            ax_pie = fig_pie.add_subplot(111)
            
            # Prepare data for pie chart
            labels = []
            sizes = []
            colors = []
            
            for cat_id, stats in cat_stats.items():
                cat_name = "Unknown"
                cat_color = "#CCCCCC"
                if cat_id in cat_map:
                    cat_name = cat_map[cat_id]["name"]
                    cat_color = cat_map[cat_id]["color"]
                
                labels.append(cat_name)
                sizes.append(stats["duration"])
                colors.append(cat_color)
            
            # Create pie chart
            wedges, texts, autotexts = ax_pie.pie(
                sizes, 
                labels=labels, 
                autopct='%1.1f%%',
                startangle=90,
                colors=colors
            )
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax_pie.axis('equal')
            ax_pie.set_title('Répartition du temps par catégorie')
            
            # Make text more readable
            for text in texts:
                text.set_fontsize(9)
            for autotext in autotexts:
                autotext.set_fontsize(9)
                autotext.set_color('white')
            
            # Embed the chart in tkinter
            canvas_pie = FigureCanvasTkAgg(fig_pie, master=pie_frame)
            canvas_pie.draw()
            canvas_pie.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            ttk.Label(pie_frame, text="Pas de données disponibles").pack(pady=50)
        
        # Tab 3: Bar Chart
        bar_frame = ttk.Frame(notebook)
        notebook.add(bar_frame, text="Histogramme")
        
        if total_activities > 0:
            # Create figure for bar chart
            fig_bar = plt.Figure(figsize=(6, 5))
            ax_bar = fig_bar.add_subplot(111)
            
            # Prepare data for bar chart
            cat_names = []
            durations = []
            bar_colors = []
            
            for cat_id, stats in cat_stats.items():
                cat_name = "Inconnu"
                cat_color = "#CCCCCC"
                if cat_id in cat_map:
                    cat_name = cat_map[cat_id]["name"]
                    cat_color = cat_map[cat_id]["color"]
                
                cat_names.append(cat_name)
                durations.append(stats["duration"])
                bar_colors.append(cat_color)
            
            # Create bar chart
            bars = ax_bar.bar(cat_names, durations, color=bar_colors)
            
            # Add labels and title
            ax_bar.set_ylabel('Durée (minutes)')
            ax_bar.set_title('Durée totale par catégorie')
            
            # Rotate x-axis labels for better readability
            plt.setp(ax_bar.get_xticklabels(), rotation=45, ha='right')
            
            # Add values on top of bars
            for bar in bars:
                height = bar.get_height()
                ax_bar.text(bar.get_x() + bar.get_width()/2., height + 5,
                        f'{int(height)}',
                        ha='center', va='bottom', rotation=0)
            
            # Adjust layout
            fig_bar.tight_layout()
            
            # Embed the chart in tkinter
            canvas_bar = FigureCanvasTkAgg(fig_bar, master=bar_frame)
            canvas_bar.draw()
            canvas_bar.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            ttk.Label(bar_frame, text="Pas de données disponibles").pack(pady=50)
        
        # Close button
        ttk.Button(dialog, text="Fermer", command=dialog.destroy).pack(pady=10)
    
    def _export_data(self):
        """Export activity data"""
        from tkinter import filedialog
        import csv
        
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Exporter les données"
        )
        
        if not file_path:
            return
        
        try:
            # Get all activities
            activities = self.db.get_activities()
            categories = self.db.get_categories()
            cat_map = {cat["id"]: cat for cat in categories}
            
            # Write to CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Date', 'Titre', 'Catégorie', 'Durée (min)', 'Notes'])
                
                # Write data
                for act in activities:
                    cat_name = "Inconnu"
                    if act["category_id"] in cat_map:
                        cat_name = cat_map[act["category_id"]]["name"]
                    
                    writer.writerow([
                        act["date"],
                        act["title"],
                        cat_name,
                        act["duration"],
                        act.get("notes", "")
                    ])
            
            messagebox.showinfo("Exportation réussie", f"Les données ont été exportées vers {file_path}")
        
        except Exception as e:
            messagebox.showerror("Erreur d'exportation", f"Une erreur est survenue: {str(e)}")
    
    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo("À propos", 
                           "Activity Tracker Calendar\n\n"
                           "Une application pour suivre et visualiser vos activités quotidiennes.\n\n"
                           "Développé dans le cadre du cours de Python.")
    
    def _refresh_all(self):
        """Refresh all views"""
        self.calendar.refresh()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
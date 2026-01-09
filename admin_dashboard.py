"""
Admin Dashboard for Soul Sense EQ Test
Provides interactive data visualization for admin panel including:
- Score distribution by age group
- Score distribution by gender (if available)
- Histograms and pivot charts
- Statistical summaries
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import sqlite3
import sys
from typing import Dict, List, Tuple, Optional

# Database connection helper
def get_db_connection():
    """Get database connection"""
    try:
        conn = sqlite3.connect("soulsense_db")
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None


class AdminDashboard:
    """Admin Dashboard with interactive data visualizations"""
    
    def __init__(self, parent_root=None):
        """Initialize the admin dashboard"""
        self.parent_root = parent_root
        self.window = None
        
    def launch(self):
        """Launch the admin dashboard"""
        if self.parent_root:
            self.window = tk.Toplevel(self.parent_root)
        else:
            self.window = tk.Tk()
        
        self.window.title("🎯 Admin Data Visualization Dashboard")
        self.window.geometry("1000x700")
        self.window.configure(bg='#f0f0f0')
        
        # Header
        header_frame = tk.Frame(self.window, bg='#2196F3', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, 
                text="🎯 Admin Data Visualization Dashboard",
                font=("Arial", 20, "bold"),
                bg='#2196F3',
                fg='white').pack(pady=25)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Overview Statistics
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="📊 Overview")
        self.create_overview_tab(overview_frame)
        
        # Tab 2: Age Group Analysis
        age_frame = ttk.Frame(notebook)
        notebook.add(age_frame, text="👥 Age Groups")
        self.create_age_analysis_tab(age_frame)
        
        # Tab 3: Score Distribution
        distribution_frame = ttk.Frame(notebook)
        notebook.add(distribution_frame, text="📈 Distribution")
        self.create_distribution_tab(distribution_frame)
        
        # Tab 4: Pivot Tables
        pivot_frame = ttk.Frame(notebook)
        notebook.add(pivot_frame, text="📋 Pivot Data")
        self.create_pivot_tab(pivot_frame)
        
        # Tab 5: Console View
        console_frame = ttk.Frame(notebook)
        notebook.add(console_frame, text="💻 Console")
        self.create_console_tab(console_frame)
        
        # Refresh button
        button_frame = tk.Frame(self.window, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(button_frame,
                 text="🔄 Refresh Data",
                 command=self.refresh_all_data,
                 bg='#4CAF50',
                 fg='white',
                 font=("Arial", 11, "bold"),
                 padx=20,
                 pady=5,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame,
                 text="❌ Close",
                 command=self.window.destroy,
                 bg='#f44336',
                 fg='white',
                 font=("Arial", 11, "bold"),
                 padx=20,
                 pady=5,
                 cursor='hand2').pack(side=tk.RIGHT, padx=5)
        
        # Store references to tabs for refresh
        self.tabs = {
            'overview': overview_frame,
            'age': age_frame,
            'distribution': distribution_frame,
            'pivot': pivot_frame
        }
        
        if not self.parent_root:
            self.window.mainloop()
    
    def create_overview_tab(self, parent):
        """Create overview statistics tab"""
        # Create canvas with scrollbar
        canvas = tk.Canvas(parent, bg='white')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Get statistics
        conn = get_db_connection()
        if not conn:
            tk.Label(scrollable_frame, text="Database connection error", 
                    font=("Arial", 14), bg='white', fg='red').pack(pady=50)
            return
        
        cursor = conn.cursor()
        
        # Title
        tk.Label(scrollable_frame, 
                text="📊 System Overview Statistics",
                font=("Arial", 16, "bold"),
                bg='white').pack(pady=15)
        
        # Stats container
        stats_container = tk.Frame(scrollable_frame, bg='white')
        stats_container.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # User statistics
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT username) FROM scores")
        users_with_scores = cursor.fetchone()[0]
        
        # Score statistics
        cursor.execute("SELECT COUNT(*) FROM scores")
        total_attempts = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(total_score), MIN(total_score), MAX(total_score) FROM scores")
        avg_score, min_score, max_score = cursor.fetchone()
        
        # Age group statistics
        cursor.execute("""
            SELECT detailed_age_group, COUNT(*) as count 
            FROM scores 
            WHERE detailed_age_group IS NOT NULL 
            GROUP BY detailed_age_group
            ORDER BY count DESC
        """)
        age_groups = cursor.fetchall()
        
        # Question statistics
        cursor.execute("SELECT COUNT(*) FROM question_bank WHERE is_active = 1")
        active_questions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM question_bank")
        total_questions = cursor.fetchone()[0]
        
        conn.close()
        
        # Display statistics in cards
        self._create_stat_card(stats_container, "👤 Total Users", total_users, 0, 0)
        self._create_stat_card(stats_container, "🎯 Users with Scores", users_with_scores, 0, 1)
        self._create_stat_card(stats_container, "📝 Total Test Attempts", total_attempts, 0, 2)
        
        self._create_stat_card(stats_container, "📊 Average Score", 
                              f"{avg_score:.1f}" if avg_score else "N/A", 1, 0)
        self._create_stat_card(stats_container, "⬇️ Minimum Score", 
                              min_score if min_score else "N/A", 1, 1)
        self._create_stat_card(stats_container, "⬆️ Maximum Score", 
                              max_score if max_score else "N/A", 1, 2)
        
        self._create_stat_card(stats_container, "❓ Active Questions", active_questions, 2, 0)
        self._create_stat_card(stats_container, "📚 Total Questions", total_questions, 2, 1)
        self._create_stat_card(stats_container, "👥 Age Groups", len(age_groups), 2, 2)
        
        # Age group breakdown
        if age_groups:
            tk.Label(scrollable_frame,
                    text="\n📊 Age Group Distribution",
                    font=("Arial", 14, "bold"),
                    bg='white').pack(pady=10)
            
            age_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.RIDGE, bd=2)
            age_frame.pack(fill=tk.X, padx=20, pady=10)
            
            for age_group, count in age_groups[:10]:  # Top 10
                row = tk.Frame(age_frame, bg='white')
                row.pack(fill=tk.X, padx=10, pady=5)
                
                tk.Label(row, text=f"{age_group}:", 
                        font=("Arial", 11, "bold"),
                        bg='white', width=15, anchor='w').pack(side=tk.LEFT)
                
                tk.Label(row, text=f"{count} attempts",
                        font=("Arial", 11),
                        bg='white', anchor='w').pack(side=tk.LEFT, padx=10)
                
                # Progress bar
                if total_attempts > 0:
                    percentage = (count / total_attempts) * 100
                    bar_length = int(percentage * 3)
                    tk.Label(row, text="█" * bar_length,
                            font=("Arial", 8),
                            bg='white', fg='#4CAF50').pack(side=tk.LEFT)
                    tk.Label(row, text=f"{percentage:.1f}%",
                            font=("Arial", 10),
                            bg='white', fg='#666').pack(side=tk.LEFT, padx=5)
    
    def _create_stat_card(self, parent, title, value, row, col):
        """Create a statistics card"""
        card = tk.Frame(parent, bg='#e3f2fd', relief=tk.RAISED, bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        tk.Label(card, text=title,
                font=("Arial", 11),
                bg='#e3f2fd',
                fg='#1976D2').pack(pady=(10, 5))
        
        tk.Label(card, text=str(value),
                font=("Arial", 24, "bold"),
                bg='#e3f2fd',
                fg='#0D47A1').pack(pady=(5, 10))
        
        # Configure grid weights
        parent.grid_columnconfigure(col, weight=1)
    
    def create_age_analysis_tab(self, parent):
        """Create age group analysis tab with visualizations"""
        # Control panel
        control_frame = tk.Frame(parent, bg='#f0f0f0', relief=tk.RIDGE, bd=2)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(control_frame, 
                text="👥 Age Group Analysis",
                font=("Arial", 14, "bold"),
                bg='#f0f0f0').pack(pady=10)
        
        # Get data
        conn = get_db_connection()
        if not conn:
            tk.Label(parent, text="Database connection error", 
                    font=("Arial", 14), fg='red').pack(pady=50)
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT detailed_age_group, total_score 
            FROM scores 
            WHERE detailed_age_group IS NOT NULL
            ORDER BY detailed_age_group
        """)
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            tk.Label(parent, text="No age group data available", 
                    font=("Arial", 14)).pack(pady=50)
            return
        
        # Process data
        age_scores = defaultdict(list)
        for age_group, score in data:
            age_scores[age_group].append(score)
        
        # Sort age groups
        sorted_groups = sorted(age_scores.keys())
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 6), dpi=100)
        
        # Plot 1: Average scores by age group
        ax1 = fig.add_subplot(121)
        avg_scores = [np.mean(age_scores[group]) for group in sorted_groups]
        colors = plt.cm.viridis(np.linspace(0, 1, len(sorted_groups)))
        
        bars = ax1.bar(range(len(sorted_groups)), avg_scores, color=colors, alpha=0.8, edgecolor='black')
        ax1.set_xlabel('Age Group', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Average EQ Score', fontsize=11, fontweight='bold')
        ax1.set_title('Average EQ Score by Age Group', fontsize=12, fontweight='bold')
        ax1.set_xticks(range(len(sorted_groups)))
        ax1.set_xticklabels(sorted_groups, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for i, (bar, score) in enumerate(zip(bars, avg_scores)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{score:.1f}',
                    ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        # Plot 2: Box plot for distribution
        ax2 = fig.add_subplot(122)
        score_data = [age_scores[group] for group in sorted_groups]
        bp = ax2.boxplot(score_data, labels=sorted_groups, patch_artist=True)
        
        # Color the boxes
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax2.set_xlabel('Age Group', fontsize=11, fontweight='bold')
        ax2.set_ylabel('EQ Score Distribution', fontsize=11, fontweight='bold')
        ax2.set_title('Score Distribution by Age Group', fontsize=12, fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Statistics table
        stats_frame = tk.Frame(parent, bg='white', relief=tk.RIDGE, bd=2)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(stats_frame, 
                text="📊 Detailed Statistics by Age Group",
                font=("Arial", 12, "bold"),
                bg='white').pack(pady=10)
        
        # Create table
        table_frame = tk.Frame(stats_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        headers = ['Age Group', 'Count', 'Avg Score', 'Min', 'Max', 'Std Dev']
        for col, header in enumerate(headers):
            tk.Label(table_frame, text=header,
                    font=("Arial", 10, "bold"),
                    bg='#2196F3', fg='white',
                    relief=tk.RIDGE, bd=1,
                    padx=10, pady=5).grid(row=0, column=col, sticky='nsew')
        
        for row, group in enumerate(sorted_groups, start=1):
            scores = age_scores[group]
            stats = [
                group,
                len(scores),
                f"{np.mean(scores):.1f}",
                min(scores),
                max(scores),
                f"{np.std(scores):.1f}"
            ]
            
            bg_color = '#f0f0f0' if row % 2 == 0 else 'white'
            for col, stat in enumerate(stats):
                tk.Label(table_frame, text=str(stat),
                        font=("Arial", 10),
                        bg=bg_color,
                        relief=tk.RIDGE, bd=1,
                        padx=10, pady=5).grid(row=row, column=col, sticky='nsew')
        
        # Configure column weights
        for col in range(len(headers)):
            table_frame.grid_columnconfigure(col, weight=1)
    
    def create_distribution_tab(self, parent):
        """Create score distribution tab with histograms"""
        # Get data
        conn = get_db_connection()
        if not conn:
            tk.Label(parent, text="Database connection error", 
                    font=("Arial", 14), fg='red').pack(pady=50)
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT total_score FROM scores")
        scores = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not scores:
            tk.Label(parent, text="No score data available", 
                    font=("Arial", 14)).pack(pady=50)
            return
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 8), dpi=100)
        
        # Plot 1: Overall histogram
        ax1 = fig.add_subplot(221)
        n, bins, patches = ax1.hist(scores, bins=20, color='#4CAF50', 
                                     alpha=0.7, edgecolor='black')
        
        # Color bars by height
        cm = plt.cm.viridis
        norm = plt.Normalize(vmin=n.min(), vmax=n.max())
        for patch, count in zip(patches, n):
            patch.set_facecolor(cm(norm(count)))
        
        ax1.set_xlabel('EQ Score', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax1.set_title('Overall Score Distribution', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add mean line
        mean_score = np.mean(scores)
        ax1.axvline(mean_score, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_score:.1f}')
        ax1.legend()
        
        # Plot 2: Cumulative distribution
        ax2 = fig.add_subplot(222)
        sorted_scores = np.sort(scores)
        cumulative = np.arange(1, len(sorted_scores) + 1) / len(sorted_scores) * 100
        ax2.plot(sorted_scores, cumulative, color='#2196F3', linewidth=2)
        ax2.fill_between(sorted_scores, cumulative, alpha=0.3, color='#2196F3')
        ax2.set_xlabel('EQ Score', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Cumulative Percentage', fontsize=11, fontweight='bold')
        ax2.set_title('Cumulative Distribution', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Score ranges
        ax3 = fig.add_subplot(223)
        ranges = ['0-20', '21-40', '41-60', '61-80', '81-100']
        range_counts = [
            sum(1 for s in scores if 0 <= s <= 20),
            sum(1 for s in scores if 21 <= s <= 40),
            sum(1 for s in scores if 41 <= s <= 60),
            sum(1 for s in scores if 61 <= s <= 80),
            sum(1 for s in scores if 81 <= s <= 100)
        ]
        
        colors = ['#f44336', '#FF9800', '#FFC107', '#4CAF50', '#2196F3']
        wedges, texts, autotexts = ax3.pie(range_counts, labels=ranges, autopct='%1.1f%%',
                                            colors=colors, startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax3.set_title('Score Range Distribution', fontsize=12, fontweight='bold')
        
        # Plot 4: Statistics summary
        ax4 = fig.add_subplot(224)
        ax4.axis('off')
        
        stats_text = f"""
        📊 Statistical Summary
        
        Total Attempts: {len(scores)}
        
        Mean Score: {np.mean(scores):.2f}
        Median Score: {np.median(scores):.2f}
        Mode Score: {max(set(scores), key=scores.count)}
        
        Std Deviation: {np.std(scores):.2f}
        Variance: {np.var(scores):.2f}
        
        Minimum: {min(scores)}
        Maximum: {max(scores)}
        Range: {max(scores) - min(scores)}
        
        25th Percentile: {np.percentile(scores, 25):.1f}
        75th Percentile: {np.percentile(scores, 75):.1f}
        IQR: {np.percentile(scores, 75) - np.percentile(scores, 25):.1f}
        """
        
        ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes,
                fontsize=11, verticalalignment='top',
                fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_pivot_tab(self, parent):
        """Create pivot table view"""
        # Title
        tk.Label(parent, 
                text="📋 Pivot Table: Scores by Age Group",
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Get data
        conn = get_db_connection()
        if not conn:
            tk.Label(parent, text="Database connection error", 
                    font=("Arial", 14), fg='red').pack(pady=50)
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                detailed_age_group,
                COUNT(*) as count,
                AVG(total_score) as avg_score,
                MIN(total_score) as min_score,
                MAX(total_score) as max_score
            FROM scores 
            WHERE detailed_age_group IS NOT NULL
            GROUP BY detailed_age_group
            ORDER BY detailed_age_group
        """)
        data = cursor.fetchall()
        
        # Also get temporal data
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', timestamp) as month,
                COUNT(*) as count,
                AVG(total_score) as avg_score
            FROM scores 
            WHERE timestamp IS NOT NULL
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        """)
        temporal_data = cursor.fetchall()
        
        conn.close()
        
        if not data:
            tk.Label(parent, text="No pivot data available", 
                    font=("Arial", 14)).pack(pady=50)
            return
        
        # Create notebook for different pivot views
        pivot_notebook = ttk.Notebook(parent)
        pivot_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Age Group Pivot
        age_pivot_frame = tk.Frame(pivot_notebook, bg='white')
        pivot_notebook.add(age_pivot_frame, text="By Age Group")
        
        # Create scrollable frame
        canvas = tk.Canvas(age_pivot_frame, bg='white')
        scrollbar = ttk.Scrollbar(age_pivot_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg='white')
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create pivot table
        headers = ['Age Group', 'Test Count', 'Avg Score', 'Min Score', 'Max Score', 'Score Range']
        
        header_frame = tk.Frame(scrollable, bg='white')
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        for col, header in enumerate(headers):
            tk.Label(header_frame, text=header,
                    font=("Arial", 11, "bold"),
                    bg='#1976D2', fg='white',
                    relief=tk.RIDGE, bd=1,
                    padx=15, pady=8).grid(row=0, column=col, sticky='ew')
        
        for i, row in enumerate(data):
            age_group = row[0] if row[0] else 'Unknown'
            count = row[1]
            avg_score = f"{row[2]:.1f}" if row[2] else 'N/A'
            min_score = row[3] if row[3] else 'N/A'
            max_score = row[4] if row[4] else 'N/A'
            score_range = f"{row[4] - row[3]}" if row[3] and row[4] else 'N/A'
            
            values = [age_group, count, avg_score, min_score, max_score, score_range]
            
            row_frame = tk.Frame(scrollable, bg='white')
            row_frame.pack(fill=tk.X, padx=5, pady=2)
            
            bg_color = '#e3f2fd' if i % 2 == 0 else 'white'
            
            for col, value in enumerate(values):
                tk.Label(row_frame, text=str(value),
                        font=("Arial", 10),
                        bg=bg_color,
                        relief=tk.RIDGE, bd=1,
                        padx=15, pady=6).grid(row=0, column=col, sticky='ew')
        
        # Temporal Pivot
        if temporal_data:
            time_pivot_frame = tk.Frame(pivot_notebook, bg='white')
            pivot_notebook.add(time_pivot_frame, text="By Month")
            
            tk.Label(time_pivot_frame,
                    text="📅 Monthly Statistics",
                    font=("Arial", 12, "bold"),
                    bg='white').pack(pady=10)
            
            time_table = tk.Frame(time_pivot_frame, bg='white')
            time_table.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            time_headers = ['Month', 'Test Count', 'Average Score']
            for col, header in enumerate(time_headers):
                tk.Label(time_table, text=header,
                        font=("Arial", 11, "bold"),
                        bg='#1976D2', fg='white',
                        relief=tk.RIDGE, bd=1,
                        padx=20, pady=8).grid(row=0, column=col, sticky='ew')
            
            for i, row in enumerate(temporal_data):
                month = row[0] if row[0] else 'Unknown'
                count = row[1]
                avg_score = f"{row[2]:.1f}" if row[2] else 'N/A'
                
                values = [month, count, avg_score]
                bg_color = '#e3f2fd' if i % 2 == 0 else 'white'
                
                for col, value in enumerate(values):
                    tk.Label(time_table, text=str(value),
                            font=("Arial", 10),
                            bg=bg_color,
                            relief=tk.RIDGE, bd=1,
                            padx=20, pady=6).grid(row=i+1, column=col, sticky='ew')
    
    def create_console_tab(self, parent):
        """Create console view with text-based statistics"""
        # Title
        tk.Label(parent, 
                text="💻 Console View",
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Text area
        text_area = scrolledtext.ScrolledText(parent, 
                                              font=("Courier", 10),
                                              bg='#1e1e1e',
                                              fg='#00ff00',
                                              wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Get all data and format as console output
        conn = get_db_connection()
        if not conn:
            text_area.insert(tk.END, "ERROR: Database connection failed\n")
            return
        
        cursor = conn.cursor()
        
        output = []
        output.append("=" * 80)
        output.append("SOUL SENSE EQ TEST - ADMIN CONSOLE VIEW")
        output.append("=" * 80)
        output.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # System stats
        output.append("\n" + "=" * 80)
        output.append("SYSTEM STATISTICS")
        output.append("=" * 80)
        
        cursor.execute("SELECT COUNT(*) FROM users")
        output.append(f"Total Users: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM scores")
        total_attempts = cursor.fetchone()[0]
        output.append(f"Total Test Attempts: {total_attempts}")
        
        cursor.execute("SELECT COUNT(*) FROM question_bank WHERE is_active = 1")
        output.append(f"Active Questions: {cursor.fetchone()[0]}")
        
        # Score statistics
        output.append("\n" + "=" * 80)
        output.append("SCORE STATISTICS")
        output.append("=" * 80)
        
        cursor.execute("""
            SELECT AVG(total_score), MIN(total_score), MAX(total_score), 
                   COUNT(DISTINCT username)
            FROM scores
        """)
        avg, min_s, max_s, unique_users = cursor.fetchone()
        
        if avg:
            output.append(f"Average Score: {avg:.2f}")
            output.append(f"Minimum Score: {min_s}")
            output.append(f"Maximum Score: {max_s}")
            output.append(f"Score Range: {max_s - min_s}")
            output.append(f"Unique Test Takers: {unique_users}")
            output.append(f"Average Attempts per User: {total_attempts / unique_users:.2f}")
        
        # Age group breakdown
        output.append("\n" + "=" * 80)
        output.append("AGE GROUP BREAKDOWN")
        output.append("=" * 80)
        
        cursor.execute("""
            SELECT detailed_age_group, 
                   COUNT(*) as count,
                   AVG(total_score) as avg_score,
                   MIN(total_score) as min_score,
                   MAX(total_score) as max_score
            FROM scores 
            WHERE detailed_age_group IS NOT NULL
            GROUP BY detailed_age_group
            ORDER BY detailed_age_group
        """)
        
        age_data = cursor.fetchall()
        
        if age_data:
            output.append(f"\n{'Age Group':<15} {'Count':<10} {'Avg':<10} {'Min':<10} {'Max':<10}")
            output.append("-" * 55)
            
            for row in age_data:
                age_group = row[0]
                count = row[1]
                avg_score = row[2]
                min_score = row[3]
                max_score = row[4]
                
                output.append(f"{age_group:<15} {count:<10} {avg_score:<10.1f} {min_score:<10} {max_score:<10}")
        
        # Recent activity
        output.append("\n" + "=" * 80)
        output.append("RECENT ACTIVITY (Last 10 Tests)")
        output.append("=" * 80)
        
        cursor.execute("""
            SELECT username, total_score, detailed_age_group, timestamp
            FROM scores
            ORDER BY id DESC
            LIMIT 10
        """)
        
        recent = cursor.fetchall()
        
        if recent:
            output.append(f"\n{'Username':<20} {'Score':<10} {'Age Group':<15} {'Timestamp':<20}")
            output.append("-" * 65)
            
            for row in recent:
                username = row[0] if row[0] else 'Unknown'
                score = row[1]
                age_group = row[2] if row[2] else 'N/A'
                timestamp = row[3] if row[3] else 'N/A'
                
                # Truncate timestamp if too long
                if len(str(timestamp)) > 19:
                    timestamp = str(timestamp)[:19]
                
                output.append(f"{username:<20} {score:<10} {age_group:<15} {timestamp:<20}")
        
        # Top performers
        output.append("\n" + "=" * 80)
        output.append("TOP 10 PERFORMERS")
        output.append("=" * 80)
        
        cursor.execute("""
            SELECT username, MAX(total_score) as best_score, detailed_age_group
            FROM scores
            GROUP BY username
            ORDER BY best_score DESC
            LIMIT 10
        """)
        
        top_performers = cursor.fetchall()
        
        if top_performers:
            output.append(f"\n{'Rank':<6} {'Username':<20} {'Best Score':<12} {'Age Group':<15}")
            output.append("-" * 53)
            
            for i, row in enumerate(top_performers, 1):
                username = row[0] if row[0] else 'Unknown'
                score = row[1]
                age_group = row[2] if row[2] else 'N/A'
                
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
                output.append(f"{i:<6} {username:<20} {score:<12} {age_group:<15} {medal}")
        
        output.append("\n" + "=" * 80)
        output.append("END OF REPORT")
        output.append("=" * 80)
        
        conn.close()
        
        # Insert all output
        text_area.insert(tk.END, "\n".join(output))
        text_area.config(state=tk.DISABLED)
    
    def refresh_all_data(self):
        """Refresh all data in all tabs"""
        if self.window:
            messagebox.showinfo("Refresh", "Refreshing all data...\nPlease wait.")
            # Destroy and recreate the window
            self.window.destroy()
            self.launch()


def main():
    """Main function to launch admin dashboard"""
    print("Launching Admin Dashboard...")
    dashboard = AdminDashboard()
    dashboard.launch()


if __name__ == "__main__":
    main()

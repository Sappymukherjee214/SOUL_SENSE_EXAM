# app/ui/journal.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
import logging

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sqlalchemy import desc, text

from app.i18n_manager import get_i18n
from app.models import JournalEntry
from app.db import get_session

# Lazy imports to avoid circular dependencies
# These will be imported only when needed
AnalyticsDashboard = None
DailyHistoryView = None


class JournalFeature:
    def __init__(self, parent_root, app=None):
        """
        Initialize Journal Feature
        
        Args:
            parent_root: The parent tkinter root window
            app: Optional SoulSenseApp instance. If None, feature works in standalone mode
        """
        self.parent_root = parent_root
        self.app = app  # Store app reference for theming (can be None)
        self.i18n = get_i18n()
        
        # Initialize theme colors (with defaults)
        # Initialize theme colors (standardized)
        self.colors = {
            "bg": "#f0f0f0",
            "surface": "white",
            "text_primary": "black",
            "text_secondary": "#666",
            "primary": "#8B5CF6",
            "secondary": "#EC4899"
        }
        
        # Use app colors if available
        if app and hasattr(app, 'colors'):
            self.colors = app.colors
        
        # Initialize VADER sentiment analyzer
        self._initialize_sentiment_analyzer()
        
    def _initialize_sentiment_analyzer(self):
        """Initialize the VADER sentiment analyzer"""
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon', quiet=True)
            
        try:
            self.sia = SentimentIntensityAnalyzer()
        except Exception as e:
            logging.error(f"Failed to initialize sentiment analyzer: {e}")
            self.sia = None

    def render_journal_view(self, parent_frame, username):
        """Render journal view inside a parent frame (Embedded Mode)"""
        self.username = username
        self.journal_window = parent_frame # Alias for compatibility
        
        # Determine colors
        colors = self.colors
        
        # Header Section
        header_frame = tk.Frame(parent_frame, bg=colors["bg"], pady=10)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text=self.i18n.get("journal.title"), 
                 font=("Segoe UI", 24, "bold"), bg=colors["bg"], 
                 fg=colors["text_primary"]).pack(anchor="w", padx=20)
                 
        today = datetime.now().strftime("%Y-%m-%d")
        tk.Label(header_frame, text=self.i18n.get("journal.date", date=today), 
                 font=("Segoe UI", 12), bg=colors["bg"], 
                 fg=colors["text_secondary"]).pack(anchor="w", padx=20)

        # Scrollable Content
        container = tk.Frame(parent_frame, bg=colors["bg"])
        container.pack(fill="both", expand=True, padx=20)
        
        # --- Metrics Section ---
        metrics_frame = tk.LabelFrame(container, text="Daily Assessment", 
                                     font=("Segoe UI", 12, "bold"), bg=colors["surface"],
                                     fg=colors["text_primary"], padx=15, pady=15)
        metrics_frame.pack(fill="x", pady=10)
        
        metrics_frame.columnconfigure(1, weight=1)
        metrics_frame.columnconfigure(3, weight=1)
        
        # Configure Theme for Sliders
        style = ttk.Style()
        style.configure("TScale", background=colors["surface"], troughcolor=colors.get("border", "#ccc"),
                        sliderthickness=15)

        def create_slider(parent, label_text, from_, to_, row, col, variable, resolution=1):
            lbl = tk.Label(parent, text=label_text, font=("Segoe UI", 11), 
                    bg=colors["surface"], fg=colors["text_primary"])
            lbl.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            
            val_lbl = tk.Label(parent, text=f"{variable.get():g}", width=4, font=("Segoe UI", 11, "bold"),
                              bg=colors["surface"], fg=colors["primary"])
            val_lbl.grid(row=row, column=col+2, padx=5)
            
            def on_scroll(val):
                v = float(val)
                v = int(v) if resolution==1 else round(v, 1)
                variable.set(v)
                val_lbl.config(text=f"{v:g}")

            # Use "TScale" style implicitly or explicitly if needed, but configure sets global default for TScale
            s = ttk.Scale(parent, from_=from_, to=to_, orient="horizontal", variable=variable, command=on_scroll)
            s.grid(row=row, column=col+1, sticky="ew", padx=5)

        # Row 0
        self.sleep_hours_var = tk.DoubleVar(value=7.0)
        create_slider(metrics_frame, "Sleep (hrs)", 0, 16, 0, 0, self.sleep_hours_var, 0.5)

        self.sleep_quality_var = tk.IntVar(value=7)
        create_slider(metrics_frame, "Sleep Quality (1-10)", 1, 10, 0, 3, self.sleep_quality_var, 1)
        
        # Row 1
        self.energy_level_var = tk.IntVar(value=7)
        create_slider(metrics_frame, "Energy (1-10)", 1, 10, 1, 0, self.energy_level_var, 1)
        
        self.work_hours_var = tk.DoubleVar(value=8.0)
        create_slider(metrics_frame, "Work (hrs)", 0, 16, 1, 3, self.work_hours_var, 0.5)

        # Row 2 (PR #6 Expansion)
        self.stress_level_var = tk.IntVar(value=3)
        create_slider(metrics_frame, "Stress (1-10)", 1, 10, 2, 0, self.stress_level_var, 1)

        # Screen Time (Slider)
        self.screen_time_var = tk.IntVar(value=120)
        create_slider(metrics_frame, "Screen Time (mins)", 0, 720, 2, 3, self.screen_time_var, 15)

        # --- Daily Context Section (PR #6) ---
        context_frame = tk.LabelFrame(container, text="Daily Context", 
                                     font=("Segoe UI", 12, "bold"), bg=colors["surface"],
                                     fg=colors["text_primary"], padx=15, pady=10)
        context_frame.pack(fill="x", pady=5)
        
        def create_compact_text(parent, label, ht=3):
            frame = tk.Frame(parent, bg=colors["surface"])
            frame.pack(fill="x", pady=5)
            tk.Label(frame, text=label, font=("Segoe UI", 10, "bold"), 
                    bg=colors["surface"], fg=colors["text_secondary"]).pack(anchor="w")
            txt = tk.Text(frame, height=ht, font=("Segoe UI", 10),
                         bg=colors.get("input_bg", "#fff"), fg=colors.get("input_fg", "#000"),
                         relief="flat", highlightthickness=1,
                         highlightbackground=colors.get("border", "#ccc"))
            txt.pack(fill="x")
            return txt

        self.schedule_text = create_compact_text(context_frame, "Daily Schedule / Key Events")
        self.triggers_text = create_compact_text(context_frame, "Stress Triggers (if any)")

        # --- Reflection Section ---
        tk.Label(container, text="Your thoughts today...", 
                font=("Segoe UI", 12, "bold"), bg=colors["bg"], 
                fg=colors["text_primary"]).pack(anchor="w", pady=(15, 5))
        
        self.text_area = scrolledtext.ScrolledText(container, width=60, height=8, 
                                                  font=("Segoe UI", 11),
                                                  bg=colors["surface"], fg=colors["text_primary"],
                                                  relief="flat", highlightthickness=1,
                                                  highlightbackground=colors.get("border", "#ccc"))
        self.text_area.pack(fill="x", expand=True)
        
        # Buttons
        btn_frame = tk.Frame(container, bg=colors["bg"])
        btn_frame.pack(fill="x", pady=20)
        
        tk.Button(btn_frame, text="Save Entry", command=self.save_and_analyze,
                 font=("Segoe UI", 11, "bold"), bg=colors["primary"], fg=colors.get("text_inverse", "white"),
                 padx=20, pady=8, relief="flat").pack(side="right")
                 
        if hasattr(self.app, 'switch_view'):
             tk.Button(btn_frame, text="Cancel", command=lambda: self.app.switch_view('home'),
                     font=("Segoe UI", 11), bg=colors["bg"], fg=colors["text_secondary"],
                     relief="flat").pack(side="right", padx=10)

    def open_journal_window(self, username):
        """Standalone Window Mode (Deprecated but kept for compat)"""
        self.username = username
        self.journal_window = tk.Toplevel(self.parent_root)
        self.journal_window.title(self.i18n.get("journal.title"))
        self.journal_window.geometry("800x600")
        self.journal_window.configure(bg=self.colors.get("bg"))
        self.render_journal_view(self.journal_window, username)
    
    def analyze_sentiment(self, text):
        """Analyze sentiment using NLTK VADER"""
        if not text.strip():
            return 0.0
            
        if self.sia:
            try:
                scores = self.sia.polarity_scores(text)
                # Convert compound (-1 to 1) to -100 to 100
                return scores['compound'] * 100
            except Exception as e:
                logging.error(f"Sentiment analysis error: {e}")
                return 0.0
        else:
            # Fallback to simple keyword matching if VADER fails
            positive_words = ['happy', 'joy', 'excited', 'grateful', 'peaceful', 'confident']
            negative_words = ['sad', 'angry', 'frustrated', 'anxious', 'worried', 'stressed']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            total_words = len(text.split())
            if total_words == 0: 
                return 0.0
            
            score = (positive_count - negative_count) / max(total_words, 1) * 100
            return max(-100, min(100, score))
    
    def extract_emotional_patterns(self, text):
        """Extract emotional patterns from text"""
        patterns = []
        text_lower = text.lower()
        
        # Stress indicators
        stress_words = ['stress', 'pressure', 'overwhelm', 'burden', 'exhausted']
        if any(word in text_lower for word in stress_words):
            patterns.append(self.i18n.get("patterns.stress_indicators"))
        
        # Relationship mentions
        relationship_words = ['friend', 'family', 'colleague', 'partner', 'relationship']
        if any(word in text_lower for word in relationship_words):
            patterns.append(self.i18n.get("patterns.social_focus"))
        
        # Growth mindset
        growth_words = ['learn', 'grow', 'improve', 'better', 'progress', 'develop']
        if any(word in text_lower for word in growth_words):
            patterns.append(self.i18n.get("patterns.growth_oriented"))
        
        # Self-reflection
        reflection_words = ['realize', 'understand', 'reflect', 'think', 'feel', 'notice']
        if any(word in text_lower for word in reflection_words):
            patterns.append(self.i18n.get("patterns.self_reflective"))
        
        return "; ".join(patterns) if patterns else self.i18n.get("patterns.general_expression")
    
    def save_and_analyze(self):
        """Save journal entry and perform AI analysis"""
        content = self.text_area.get("1.0", tk.END).strip()
        
        if not content:
            messagebox.showwarning(self.i18n.get("journal.empty_entry"), 
                                  self.i18n.get("journal.empty_warning"))
            return
        
        if len(content) < 10:
            messagebox.showwarning(self.i18n.get("journal.too_short"), 
                                  self.i18n.get("journal.short_warning"))
            return
        
        # Perform analysis
        sentiment_score = self.analyze_sentiment(content)
        emotional_patterns = self.extract_emotional_patterns(content)
        
        # Save to database
        session = get_session()
        try:
            entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = JournalEntry(
                username=self.username,
                entry_date=entry_date,
                content=content,
                sentiment_score=sentiment_score,
                emotional_patterns=emotional_patterns,
                # Metrics
                sleep_hours=self.sleep_hours_var.get(),
                sleep_quality=self.sleep_quality_var.get(),
                energy_level=self.energy_level_var.get(),
                work_hours=self.work_hours_var.get(),
                # PR #6 Expansion
                screen_time_mins=self.screen_time_var.get(),
                stress_level=self.stress_level_var.get(),
                daily_schedule=self.schedule_text.get("1.0", tk.END).strip(),
                stress_triggers=self.triggers_text.get("1.0", tk.END).strip()
            )
            session.add(entry)
            session.commit()
            
            # Check for expanded health insights
            health_insights = self.generate_health_insights()
            
            # Show analysis results with insights
            self.show_analysis_results(sentiment_score, emotional_patterns, health_insights)
            
            # Clear text area
            # Clear inputs
            self.text_area.delete("1.0", tk.END)
            self.schedule_text.delete("1.0", tk.END)
            self.triggers_text.delete("1.0", tk.END)
            
        except Exception as e:
            logging.error("Failed to save journal entry", exc_info=True)
            messagebox.showerror("Error", f"Failed to save entry: {e}")
            session.rollback()
        finally:
            session.close()
    
    def show_analysis_results(self, sentiment_score, patterns, nudge_advice=None):
        """Display AI analysis results"""
        # Use stored colors
        bg_color = self.colors.get("bg", "#f5f5f5")
        card_bg = self.colors.get("surface", "white")
        text_color = self.colors.get("text_primary", "black")
        subtext_color = self.colors.get("text_secondary", "#666")
        nudge_bg = "#FFF3E0"
        nudge_text_color = "#333"
        nudge_title_color = "#EF6C00"
        
        # Adjust for dark mode if theme is known
        if self.app and hasattr(self.app, 'current_theme') and self.app.current_theme == 'dark':
            nudge_bg = self.colors.get("bg_tertiary", "#334155")
            nudge_text_color = self.colors.get("text_primary", "#F8FAFC")
            nudge_title_color = "#FFA726"
        
        result_window = tk.Toplevel(self.journal_window)
        result_window.title(self.i18n.get("journal.analysis_title"))
        result_window.geometry("450x450")
        result_window.configure(bg=bg_color)
        
        main_frame = tk.Frame(result_window, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        tk.Label(main_frame, text=self.i18n.get("journal.emotional_analysis"), 
                font=("Arial", 16, "bold"), bg=bg_color, fg=text_color).pack(pady=(0, 15))
        
        # Sentiment Card
        card_frame = tk.Frame(main_frame, bg=card_bg, relief=tk.RIDGE, bd=1)
        card_frame.pack(fill=tk.X, pady=5)
        
        # Sentiment interpretation
        if sentiment_score > 20:
            sentiment_text = self.i18n.get("journal.positive_tone")
            color = "#4CAF50"
            emoji = "😊"
        elif sentiment_score < -20:
            sentiment_text = self.i18n.get("journal.negative_tone")
            color = "#F44336"
            emoji = "😔"
        else:
            sentiment_text = self.i18n.get("journal.neutral_tone")
            color = "#2196F3"
            emoji = "😐"
        
        tk.Label(card_frame, text=f"{emoji} Sentiment Score: {sentiment_score:.1f}", 
                font=("Arial", 14, "bold"), fg=color, bg=card_bg).pack(pady=(15, 5))
        tk.Label(card_frame, text=sentiment_text, 
                font=("Arial", 11), fg=subtext_color, bg=card_bg).pack(pady=(0, 15))
        
        # Patterns Section
        tk.Label(main_frame, text=self.i18n.get("journal.emotional_patterns"), 
                font=("Arial", 12, "bold"), bg=bg_color, fg=text_color).pack(pady=(15, 5))
        
        lbl_patterns = tk.Label(main_frame, text=patterns, 
                font=("Arial", 11), wraplength=380, bg=bg_color, fg=text_color)
        lbl_patterns.pack(pady=5)
        
        # --- Nudge Section ---
        if nudge_advice:
            nudge_frame = tk.Frame(main_frame, bg=nudge_bg, relief=tk.FLAT, bd=0)
            nudge_frame.pack(fill=tk.X, pady=15, ipadx=10, ipady=10)
            
            tk.Label(nudge_frame, text="💡 AI Health Assistant", 
                    font=("Arial", 11, "bold"), bg=nudge_bg, fg=nudge_title_color).pack(anchor="w")
            
            tk.Label(nudge_frame, text=nudge_advice, 
                    font=("Arial", 10), bg=nudge_bg, fg=nudge_text_color, 
                    justify="left", wraplength=360).pack(anchor="w", pady=(5,0))
        
        tk.Button(main_frame, text=self.i18n.get("journal.close"), 
                 command=result_window.destroy, 
                 font=("Arial", 11), bg="#ddd", relief=tk.FLAT, padx=15).pack(pady=20)
    
    def view_past_entries(self):
        """View past journal entries"""
        entries_window = tk.Toplevel(self.journal_window)
        entries_window.title(self.i18n.get("journal.past_entries_title"))
        entries_window.geometry("700x500")
        entries_window.configure(bg=self.colors["bg_primary"])
        
        tk.Label(entries_window, text=self.i18n.get("journal.emotional_journey"), 
                font=("Arial", 16, "bold"), bg=self.colors["bg_primary"],
                fg=self.colors["text_primary"]).pack(pady=10)

        def open_history_view():
            """Open daily history view with lazy import"""
            try:
                # Lazy import to avoid circular dependency
                from app.ui.daily_view import DailyHistoryView
                top = tk.Toplevel(self.parent_root)
                DailyHistoryView(top, self.app, self.username)
                entries_window.destroy()
            except ImportError as e:
                logging.error(f"Failed to import DailyHistoryView: {e}")
                messagebox.showerror("Error", "Calendar view feature not available")

        tk.Button(entries_window, text="📅 Calendar View", command=open_history_view,
                 bg=self.colors.get("secondary", "#8B5CF6"), fg="white", 
                 relief="flat", padx=10).pack(pady=5)
        

        # Filter Frame
        filter_frame = tk.Frame(entries_window, bg=self.colors["bg"], pady=10)
        filter_frame.pack(fill="x", padx=20)
        
        tk.Label(filter_frame, text="🔍 Filter:", bg=self.colors["bg"]).pack(side="left")
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(filter_frame, textvariable=search_var, width=20)
        search_entry.pack(side="left", padx=5)
        
        type_var = tk.StringVar(value="All")
        type_combo = ttk.Combobox(filter_frame, textvariable=type_var, values=["All", "High Stress (>7)", "Great Days (Energy > 7)", "Bad Sleep (<6h)"], state="readonly")
        type_combo.pack(side="left", padx=5)
        
        # Scrollable Area
        canvas = tk.Canvas(entries_window, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(entries_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["bg"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        def render_entries():
            # Clear existing
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
                
            search_term = search_var.get().lower()
            filter_type = type_var.get()
            
            session = get_session()
            try:
                entries = session.query(JournalEntry)\
                    .filter_by(username=self.username)\
                    .order_by(desc(JournalEntry.entry_date))\
                    .all()
                
                filtered_count = 0
                for entry in entries:
                    # Apply Filters
                    if search_term and search_term not in entry.content.lower():
                        continue
                        
                    if filter_type == "High Stress (>7)" and (entry.stress_level or 0) <= 7:
                        continue
                    if filter_type == "Great Days (Energy > 7)" and (entry.energy_level or 0) <= 7:
                        continue
                    if filter_type == "Bad Sleep (<6h)" and (entry.sleep_hours or 7) >= 6:
                        continue
                        
                    filtered_count += 1
                    self._create_entry_card(scrollable_frame, entry)
                    
                if filtered_count == 0:
                    tk.Label(scrollable_frame, text="No entries found matching filters.", 
                            font=("Segoe UI", 12), bg=self.colors["bg"], fg=self.colors["text_secondary"]).pack(pady=20)
            finally:
                session.close()

        # Update on filter change
        tk.Button(filter_frame, text="Search", command=render_entries, bg=self.colors["primary"], fg="white").pack(side="left", padx=5)
        type_combo.bind("<<ComboboxSelected>>", lambda e: render_entries())
        
        # Initial Render
        render_entries()

        # Configure canvas width
        def _configure_canvas(event):
            canvas.itemconfig(canvas.create_window((0,0), window=scrollable_frame, anchor="nw"), width=event.width)
        canvas.bind("<Configure>", _configure_canvas)

    def _create_entry_card(self, parent, entry):
        """Create a styled card for a journal entry"""
        card = tk.Frame(parent, bg=self.colors["surface"], bd=1, relief="ridge")
        card.pack(fill="x", pady=5)
        
        # Header
        header = tk.Frame(card, bg=self.colors["surface"])
        header.pack(fill="x", padx=10, pady=5)
        
        stress_icon = "🔴" if (entry.stress_level or 0) > 7 else "🟢"
        date_str = datetime.strptime(str(entry.entry_date).split('.')[0], "%Y-%m-%d %H:%M:%S").strftime("%b %d, %I:%M %p")
        
        tk.Label(header, text=f"{stress_icon} {date_str}", 
                font=("Segoe UI", 10, "bold"), bg=self.colors["surface"], fg=self.colors["text_primary"]).pack(side="left")
        
        score = getattr(entry, 'sentiment_score', 0)
        mood = "😊" if score > 50 else "😐" if score > -20 else "😔"
        tk.Label(header, text=mood, font=("Segoe UI", 14), bg=self.colors["surface"]).pack(side="right")
        
        # Content Preview
        preview = entry.content[:150] + "..." if len(entry.content) > 150 else entry.content
        tk.Label(card, text=preview, font=("Segoe UI", 10), 
                bg=self.colors["surface"], fg=self.colors["text_primary"], 
                wraplength=500, justify="left").pack(fill="x", padx=10, pady=5)
        
        # Footer Tags
        footer = tk.Frame(card, bg=self.colors["surface"])
        footer.pack(fill="x", padx=10, pady=5)
        
        def add_tag(text, color):
            lbl = tk.Label(footer, text=text, font=("Segoe UI", 8), bg=color, fg="white", padx=5, pady=2)
            lbl.pack(side="left", padx=2)
            
        if entry.stress_level: add_tag(f"Stress: {entry.stress_level}", "#EF4444" if entry.stress_level > 7 else "#3B82F6")
        if entry.sleep_hours: add_tag(f"Sleep: {entry.sleep_hours}h", "#8B5CF6")
        if entry.screen_time_mins: add_tag(f"Screen: {entry.screen_time_mins//60}h", "#F59E0B")
    
    def open_dashboard(self):
        """Open analytics dashboard with lazy import"""
        try:
            # Lazy import to avoid circular dependency
            from app.ui.dashboard import AnalyticsDashboard
            colors = getattr(self.app, 'colors', self.colors)
            theme = self.app.settings.get("theme", "light") if self.app else "light"
            dashboard = AnalyticsDashboard(self.journal_window, self.username, colors=colors, theme=theme)
            dashboard.open_dashboard()
        except ImportError as e:
            logging.error(f"Failed to import AnalyticsDashboard: {e}")
            messagebox.showerror("Error", "Dashboard feature not available")

    # ========== HEALTH INSIGHTS & NUDGES ==========
    def generate_health_insights(self):
        """Check for recent trends and return comprehensive health insights"""
        session = get_session()
        try:
            # Query last 3 days
            three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
            
            # Use SQLAlchemy query instead of raw SQL for better compatibility
            entries = session.query(JournalEntry)\
                .filter(JournalEntry.username == self.username)\
                .filter(JournalEntry.entry_date >= three_days_ago)\
                .order_by(JournalEntry.entry_date.desc())\
                .all()
            
            if not entries:
                return "Start tracking your sleep and energy to get personalized health insights!"
            
            # Data extraction
            sleeps = []
            qualities = []
            energies = []
            works = []
            screens = []
            stresses = []
            
            for entry in entries:
                sleeps.append(entry.sleep_hours)
                qualities.append(entry.sleep_quality)
                energies.append(entry.energy_level)
                works.append(entry.work_hours)
                screens.append(getattr(entry, 'screen_time_mins', None))
                stresses.append(getattr(entry, 'stress_level', None))
            
            # 1. Digital Overload (High Screen + High Stress)
            avg_screen = sum(s for s in screens if s)/len([s for s in screens if s]) if any(screens) else 0
            avg_stress = sum(s for s in stresses if s)/len([s for s in stresses if s]) if any(stresses) else 0
            
            insights = []
            
            if avg_screen > 240 and avg_stress > 6:
                insights.append("⚠️ **Digital Overload**: Your high screen time (>4h) correlates with elevated stress. Try a 'tech-free' hour before bed.")
                
            # 2. Burnout Risk (High Work + Low Energy)
            avg_work = sum(w for w in works if w)/len([w for w in works if w]) if any(works) else 0
            avg_energy = sum(e for e in energies if e)/len([e for e in energies if e]) if any(energies) else 0
            
            if avg_work > 9 and avg_energy < 5:
                 insights.append("🔥 **Burnout Warning**: You're working long hours while energy is low. Schedule a mandatory break tomorrow.")
            
            # 3. Recovery Deficit (Low Sleep)
            avg_sleep = sum(s for s in sleeps if s)/len([s for s in sleeps if s]) if any(sleeps) else 0
            if avg_sleep < 6:
                insights.append("💤 **Sleep Debt**: You're averaging <6 hours. This significantly impacts mood regulation.")

            # 4. Trigger Awareness (New)
            recent_triggers = [t for t in [getattr(e, 'stress_triggers', '') for e in entries] if t]
            if recent_triggers:
                common_trigger = recent_triggers[0][:20] + "..." # Simplified "topic extraction"
                insights.append(f"🧠 **Trigger Awareness**: You noted '{common_trigger}'. Awareness is the first step to management.")

            # 5. Schedule Optimization (New)
            schedules = [s for s in [getattr(e, 'daily_schedule', '') for e in entries] if s]
            if schedules and len(schedules[0]) > 50: # Arbitrary length check for "busy"
                 insights.append("🗓️ **Schedule Check**: Your days look packed. Ensure you have 15 mins of 'white space' for transition time.")

            if insights:
                return "\n\n".join(insights)
            else:
                return "You're balancing well! No major risk factors detected this week."
            
            # Calculate Averages
            avg_sleep = sum(sleeps) / len(sleeps) if sleeps else 0
            avg_quality = sum(qualities) / len(qualities) if qualities else 0
            avg_energy = sum(energies) / len(energies) if energies else 0
            avg_work = sum(works) / len(works) if works else 0
            
            insights = []
            
            # --- Logic Rule Engine ---
            
            # 1. Sleep Logic (Duration & Quality)
            if avg_sleep < 6.0:
                insights.append("🌙 You've been averaging less than 6 hours of sleep.")
            elif avg_sleep >= 7.5 and avg_quality >= 7:
                insights.append("🛌 You're getting great sleep quantity and quality!")
            
            # Quality specific
            if qualities and avg_quality < 5:
                insights.append("📉 Your sleep quality is reported low. Ensure your room is cool and dark.")
            elif sleeps and qualities and avg_sleep > 8 and avg_quality < 5:
                insights.append("🤔 You're sleeping long hours but quality is low. This might indicate restless sleep.")

            # 2. Energy Logic
            if len(energies) >= 2 and all(e <= 4 for e in energies[:3]):
                insights.append("🔋 Warning: Consistent low energy detected. Prevent burnout by taking a break.")
            elif avg_energy >= 8.0:
                insights.append("⚡ You're continuously reporting high energy!")
            elif len(energies) >= 2 and energies[0] > energies[-1] + 2:
                 insights.append("🚀 Energy trend: Improving compared to recent days.")

            # 3. Work Logic
            if avg_work > 10:
                 insights.append("💼 Heavy Workload Alert: Averaging >10h/day. Don't forget to disconnect.")
            elif avg_work > 8:
                 insights.append("👔 You're having a standard productive work week.")
            elif avg_work < 2 and avg_energy > 5:
                 insights.append("🧘 Low work hours + High energy = Great recovery period!")

            # Construct final message
            if insights:
                insight_text = " ".join(insights)
            else:
                insight_text = "Your health metrics are stable. Consistent tracking discovers hidden patterns!"
                
        except Exception as e:
            logging.error(f"Insight generation failed: {e}")
            insight_text = "Could not generate insights at this moment."
        finally:
            session.close()
            
        return insight_text


# Standalone test function
if __name__ == "__main__":
    root = tk.Tk()
    journal = JournalFeature(root)
    journal.open_journal_window("test_user")
    root.mainloop()
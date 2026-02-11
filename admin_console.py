"""
Admin Console Dashboard for Soul Sense EQ Test
Provides console-based data visualization with ASCII charts
Alternative to GUI dashboard for terminal-only environments
"""

import sqlite3
from datetime import datetime
from collections import defaultdict
import sys
from typing import Dict, List, Tuple


class AdminConsoleDashboard:
    """Console-based admin dashboard with ASCII visualizations"""
    
    def __init__(self, db_path="soulsense_db"):
        """Initialize the console dashboard"""
        self.db_path = db_path
        self.width = 80
    
    def get_db_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print(f"ERROR: Database connection failed - {e}")
            return None
    
    def print_header(self, title):
        """Print a formatted header"""
        print("\n" + "=" * self.width)
        print(title.center(self.width))
        print("=" * self.width)
    
    def print_section(self, title):
        """Print a section header"""
        print(f"\n{'-' * self.width}")
        print(title)
        print(f"{'-' * self.width}")
    
    def create_bar_chart(self, data: Dict[str, float], max_width=50):
        """Create ASCII bar chart"""
        if not data:
            return "No data available"
        
        max_value = max(data.values()) if data else 1
        
        lines = []
        for label, value in sorted(data.items()):
            bar_length = int((value / max_value) * max_width)
            bar = "█" * bar_length
            lines.append(f"{label:<20} {bar} {value:.1f}")
        
        return "\n".join(lines)
    
    def create_histogram(self, values: List[int], bins=10):
        """Create ASCII histogram"""
        if not values:
            return "No data available"
        
        min_val = min(values)
        max_val = max(values)
        bin_width = (max_val - min_val) / bins
        
        # Create bins
        bin_counts = defaultdict(int)
        for value in values:
            bin_idx = min(int((value - min_val) / bin_width), bins - 1)
            bin_counts[bin_idx] += 1
        
        # Find max count for scaling
        max_count = max(bin_counts.values()) if bin_counts else 1
        
        lines = []
        for i in range(bins):
            bin_start = min_val + i * bin_width
            bin_end = bin_start + bin_width
            count = bin_counts[i]
            bar_length = int((count / max_count) * 40)
            bar = "█" * bar_length
            lines.append(f"{bin_start:6.1f}-{bin_end:6.1f} | {bar} ({count})")
        
        return "\n".join(lines)
    
    def show_overview(self):
        """Display overview statistics"""
        self.print_header("SOUL SENSE EQ TEST - ADMIN DASHBOARD")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        conn = self.get_db_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        self.print_section("SYSTEM OVERVIEW")
        
        # User statistics
        try:
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            print(f"Total Users: {total_users}")
            
            cursor.execute("SELECT COUNT(DISTINCT username) FROM scores")
            users_with_scores = cursor.fetchone()[0]
            print(f"Users with Scores: {users_with_scores}")
        except sqlite3.OperationalError:
            # Users table might not exist, use scores table instead
            cursor.execute("SELECT COUNT(DISTINCT username) FROM scores")
            users_with_scores = cursor.fetchone()[0]
            print(f"Users with Scores: {users_with_scores}")
        
        # Score statistics
        cursor.execute("SELECT COUNT(*) FROM scores")
        total_attempts = cursor.fetchone()[0]
        print(f"Total Test Attempts: {total_attempts}")
        
        cursor.execute("""
            SELECT AVG(total_score), MIN(total_score), MAX(total_score)
            FROM scores
        """)
        avg_score, min_score, max_score = cursor.fetchone()
        
        if avg_score:
            print(f"\nAverage Score: {avg_score:.2f}")
            print(f"Minimum Score: {min_score}")
            print(f"Maximum Score: {max_score}")
            print(f"Score Range: {max_score - min_score}")
        
        # Question statistics
        try:
            cursor.execute("SELECT COUNT(*) FROM question_bank WHERE is_active = 1")
            active_questions = cursor.fetchone()[0]
            print(f"\nActive Questions: {active_questions}")
            
            cursor.execute("SELECT COUNT(*) FROM question_bank")
            total_questions = cursor.fetchone()[0]
            print(f"Total Questions in Bank: {total_questions}")
        except sqlite3.OperationalError:
            # Question bank might not exist
            print(f"\nQuestion bank not available")
        
        conn.close()
    
    def show_age_group_analysis(self):
        """Display age group analysis with bar charts"""
        self.print_section("AGE GROUP ANALYSIS")
        
        conn = self.get_db_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
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
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("No age group data available")
            return
        
        # Display table
        print(f"\n{'Age Group':<15} {'Count':<10} {'Avg Score':<12} {'Min':<8} {'Max':<8} {'Range':<8}")
        print("-" * 70)
        
        avg_scores = {}
        for row in data:
            age_group = row[0]
            count = row[1]
            avg_score = row[2]
            min_score = row[3]
            max_score = row[4]
            score_range = max_score - min_score
            
            print(f"{age_group:<15} {count:<10} {avg_score:<12.1f} {min_score:<8} {max_score:<8} {score_range:<8}")
            avg_scores[age_group] = avg_score
        
        # Bar chart of average scores
        print("\n[CHART] Average Score by Age Group:")
        print(self.create_bar_chart(avg_scores))
        
        # Count distribution
        print("\n[CHART] Test Count by Age Group:")
        count_data = {row[0]: row[1] for row in data}
        print(self.create_bar_chart(count_data))
    
    def show_score_distribution(self):
        """Display score distribution with histogram"""
        self.print_section("SCORE DISTRIBUTION")
        
        conn = self.get_db_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT total_score FROM scores")
        scores = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not scores:
            print("No score data available")
            return
        
        # Statistics
        import statistics
        
        print(f"\nTotal Scores: {len(scores)}")
        print(f"Mean: {statistics.mean(scores):.2f}")
        print(f"Median: {statistics.median(scores):.2f}")
        
        if len(scores) > 1:
            print(f"Std Dev: {statistics.stdev(scores):.2f}")
        
        # Histogram
        print("\n[HISTOGRAM] Score Distribution:")
        print(self.create_histogram(scores, bins=10))
        
        # Score ranges
        print("\n[CHART] Score Range Breakdown:")
        ranges = {
            '0-20': sum(1 for s in scores if 0 <= s <= 20),
            '21-40': sum(1 for s in scores if 21 <= s <= 40),
            '41-60': sum(1 for s in scores if 41 <= s <= 60),
            '61-80': sum(1 for s in scores if 61 <= s <= 80),
            '81-100': sum(1 for s in scores if 81 <= s <= 100)
        }
        
        for range_name, count in ranges.items():
            percentage = (count / len(scores)) * 100
            bar_length = int(percentage / 2)  # Scale to 50 chars max
            bar = "█" * bar_length
            print(f"{range_name:>8} | {bar:<50} {count:4d} ({percentage:5.1f}%)")
    
    def show_pivot_tables(self):
        """Display pivot table data"""
        self.print_section("PIVOT TABLE: Scores by Age Group")
        
        conn = self.get_db_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Age group pivot
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
        
        if data:
            print(f"\n{'Age Group':<15} {'Count':<10} {'Avg':<10} {'Min':<10} {'Max':<10} {'Range':<10}")
            print("=" * 70)
            
            for row in data:
                age_group = row[0]
                count = row[1]
                avg_score = row[2]
                min_score = row[3]
                max_score = row[4]
                score_range = max_score - min_score
                
                print(f"{age_group:<15} {count:<10} {avg_score:<10.1f} {min_score:<10} {max_score:<10} {score_range:<10}")
        
        # Temporal pivot
        print("\n[TEMPORAL] Monthly Statistics (Last 12 Months):")
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
        
        if temporal_data:
            print(f"\n{'Month':<15} {'Count':<10} {'Avg Score':<12}")
            print("-" * 40)
            
            for row in temporal_data:
                month = row[0]
                count = row[1]
                avg_score = row[2]
                
                print(f"{month:<15} {count:<10} {avg_score:<12.1f}")
        
        conn.close()
    
    def show_top_performers(self):
        """Display top performers"""
        self.print_section("TOP 10 PERFORMERS")
        
        conn = self.get_db_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, MAX(total_score) as best_score, detailed_age_group
            FROM scores
            GROUP BY username
            ORDER BY best_score DESC
            LIMIT 10
        """)
        
        top_performers = cursor.fetchall()
        
        if top_performers:
            print(f"\n{'Rank':<6} {'Username':<20} {'Best Score':<12} {'Age Group':<15}")
            print("=" * 60)
            
            for i, row in enumerate(top_performers, 1):
                username = row[0] if row[0] else 'Unknown'
                score = row[1]
                age_group = row[2] if row[2] else 'N/A'
                
                medal = "[1]" if i == 1 else "[2]" if i == 2 else "[3]" if i == 3 else "   "
                print(f"{i:<6} {username:<20} {score:<12} {age_group:<15} {medal}")
        
        conn.close()
    
    def show_recent_activity(self):
        """Display recent activity"""
        self.print_section("RECENT ACTIVITY (Last 15 Tests)")
        
        conn = self.get_db_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, total_score, detailed_age_group, timestamp
            FROM scores
            ORDER BY id DESC
            LIMIT 15
        """)
        
        recent = cursor.fetchall()
        
        if recent:
            print(f"\n{'Username':<20} {'Score':<10} {'Age Group':<15} {'Timestamp':<20}")
            print("=" * 70)
            
            for row in recent:
                username = row[0] if row[0] else 'Unknown'
                score = row[1]
                age_group = row[2] if row[2] else 'N/A'
                timestamp = row[3] if row[3] else 'N/A'
                
                # Truncate timestamp
                if len(str(timestamp)) > 19:
                    timestamp = str(timestamp)[:19]
                
                print(f"{username:<20} {score:<10} {age_group:<15} {timestamp:<20}")
        
        conn.close()
    
    def run(self):
        """Run the complete dashboard"""
        self.show_overview()
        self.show_age_group_analysis()
        self.show_score_distribution()
        self.show_pivot_tables()
        self.show_top_performers()
        self.show_recent_activity()
        
        print("\n" + "=" * self.width)
        print("END OF REPORT".center(self.width))
        print("=" * self.width + "\n")
    
    def interactive_menu(self):
        """Run interactive menu"""
        while True:
            self.print_header("ADMIN DASHBOARD - MENU")
            print("\n1. System Overview")
            print("2. Age Group Analysis")
            print("3. Score Distribution")
            print("4. Pivot Tables")
            print("5. Top Performers")
            print("6. Recent Activity")
            print("7. Complete Report")
            print("8. Exit")
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                self.show_overview()
            elif choice == '2':
                self.show_age_group_analysis()
            elif choice == '3':
                self.show_score_distribution()
            elif choice == '4':
                self.show_pivot_tables()
            elif choice == '5':
                self.show_top_performers()
            elif choice == '6':
                self.show_recent_activity()
            elif choice == '7':
                self.run()
            elif choice == '8':
                print("\nExiting dashboard. Goodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")
            
            input("\nPress Enter to continue...")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Soul Sense Admin Console Dashboard')
    parser.add_argument('--db', default='soulsense_db', help='Database path')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Run in interactive menu mode')
    
    args = parser.parse_args()
    
    dashboard = AdminConsoleDashboard(args.db)
    
    if args.interactive:
        dashboard.interactive_menu()
    else:
        dashboard.run()


if __name__ == "__main__":
    main()

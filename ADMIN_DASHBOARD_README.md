# Admin Dashboard Documentation

## Overview

The Soul Sense Admin Dashboard provides comprehensive data visualization and analytics for administrators to monitor and analyze EQ test results across the system.

## Features

### 📊 Interactive GUI Dashboard (`admin_dashboard.py`)

A full-featured Tkinter-based dashboard with:

#### 1. **Overview Tab**

- System-wide statistics (users, attempts, scores)
- Average, min, and max scores
- Active questions count
- Visual stat cards with color coding
- Age group distribution breakdown

#### 2. **Age Group Analysis Tab**

- Bar charts showing average scores by age group
- Box plots for score distribution
- Detailed statistics table with:
  - Test count per age group
  - Average, min, max scores
  - Standard deviation
- Color-coded visualizations using matplotlib

#### 3. **Score Distribution Tab**

- Overall histogram with 20 bins
- Cumulative distribution curve
- Score range pie chart (0-20, 21-40, 41-60, 61-80, 81-100)
- Statistical summary panel with:
  - Mean, median, mode
  - Standard deviation and variance
  - Percentiles and IQR

#### 4. **Pivot Tables Tab**

- Age group pivot with aggregated statistics
- Monthly statistics (last 12 months)
- Count, average, min, max scores per category
- Sortable and scrollable tables

#### 5. **Console View Tab**

- Text-based report in terminal style
- Recent activity (last 10 tests)
- Top 10 performers with medals
- Full system report

### 💻 Console Dashboard (`admin_console.py`)

A lightweight console-based alternative for terminal-only environments:

#### Features:

- ASCII bar charts and histograms
- Complete statistical analysis
- Age group breakdown
- Score distribution visualization
- Pivot tables
- Top performers leaderboard
- Recent activity log

#### Modes:

1. **Full Report Mode** (default)

   ```bash
   python admin_console.py
   ```

   Displays complete analytics report

2. **Interactive Menu Mode**
   ```bash
   python admin_console.py --interactive
   ```
   Interactive menu to view specific sections

## Installation

### Requirements

Both dashboards require:

```bash
pip install matplotlib numpy
```

GUI dashboard additionally requires:

- tkinter (usually included with Python)

## Usage

### GUI Dashboard

#### Launch from Python:

```python
from admin_dashboard import AdminDashboard

# Standalone launch
dashboard = AdminDashboard()
dashboard.launch()

# Or integrate with existing Tkinter app
import tkinter as tk
root = tk.Tk()
dashboard = AdminDashboard(parent_root=root)
dashboard.launch()
```

#### Direct launch:

```bash
python admin_dashboard.py
```

### Console Dashboard

#### Full Report:

```bash
python admin_console.py
```

#### Interactive Mode:

```bash
python admin_console.py --interactive
```

#### Custom Database Path:

```bash
python admin_console.py --db /path/to/database
```

## Database Schema

The dashboards query the following tables:

### `users`

- User account information
- Creation and login timestamps

### `scores`

- EQ test results
- Fields: username, total_score, age, detailed_age_group, timestamp

### `question_bank`

- Available questions
- Active/inactive status

### `responses`

- Individual question responses
- Detailed tracking per user

## Visualization Types

### 1. Bar Charts

- Average scores by age group
- Test count distribution
- Categorical comparisons

### 2. Box Plots

- Score distribution within age groups
- Outlier detection
- Quartile visualization

### 3. Histograms

- Overall score distribution
- Frequency analysis
- Pattern identification

### 4. Pie Charts

- Score range proportions
- Category percentages

### 5. Cumulative Distribution

- Percentile rankings
- Score progression

### 6. Pivot Tables

- Multi-dimensional data aggregation
- Group-by statistics
- Temporal analysis

## Data Metrics

### Overview Metrics

- Total users
- Users with test scores
- Total test attempts
- Average EQ score
- Score range (min/max)
- Active questions count

### Age Group Metrics

- Count per age group
- Average score per group
- Min/max scores
- Standard deviation
- Score distribution

### Distribution Metrics

- Mean, median, mode
- Standard deviation
- Variance
- Percentiles (25th, 75th)
- Interquartile range (IQR)

### Performance Metrics

- Top performers
- Score improvements
- Recent activity
- Temporal trends

## Customization

### Modify Chart Colors

Edit color schemes in the visualization functions:

```python
# In admin_dashboard.py
colors = plt.cm.viridis(np.linspace(0, 1, len(sorted_groups)))
```

### Adjust Display Limits

Change data limits in query functions:

```python
# Show more/fewer recent activities
cursor.execute("... LIMIT 15")  # Change limit value
```

### Add New Visualizations

Create new tabs by adding to the notebook:

```python
new_frame = ttk.Frame(notebook)
notebook.add(new_frame, text="New Tab")
self.create_new_visualization(new_frame)
```

## Refresh Data

Both dashboards support data refresh:

**GUI Dashboard:**

- Click "🔄 Refresh Data" button
- Automatically reloads all tabs

**Console Dashboard:**

- Re-run the command
- In interactive mode, each view shows latest data

## Performance Considerations

### For Large Databases:

1. Queries are optimized with proper indexing
2. Limit clauses prevent excessive data loading
3. Aggregations done at database level
4. Results cached where appropriate

### Memory Usage:

- GUI: ~50-100 MB for typical datasets
- Console: ~10-20 MB for typical datasets

## Troubleshooting

### Database Connection Issues

```python
# Check database path
conn = sqlite3.connect("soulsense_db")
# Ensure database file exists in current directory
```

### Tkinter Not Available

Use console dashboard instead:

```bash
python admin_console.py
```

### Matplotlib Display Issues

```python
# For non-GUI backends
import matplotlib
matplotlib.use('Agg')
```

### No Data Displayed

- Ensure database has test results
- Check that `scores` table has records
- Verify age_group fields are populated

## Integration Examples

### Add to Main Application

```python
# In main app menu
def open_admin_dashboard():
    from admin_dashboard import AdminDashboard
    dashboard = AdminDashboard(parent_root=root)
    dashboard.launch()

admin_button = tk.Button(menu_frame,
                         text="Admin Dashboard",
                         command=open_admin_dashboard)
```

### Export to PDF

```python
# In admin_console.py
import sys
sys.stdout = open('admin_report.txt', 'w')
dashboard.run()
sys.stdout.close()
```

### Schedule Reports

```bash
# Linux/Mac crontab
0 9 * * * cd /path/to/project && python admin_console.py > daily_report.txt

# Windows Task Scheduler
python C:\path\to\admin_console.py > C:\path\to\report.txt
```

## Security Notes

⚠️ **Important**: This dashboard displays sensitive user data:

- Implement authentication before granting access
- Use role-based access control (RBAC)
- Log all admin activities
- Consider data anonymization for demos

Example authentication:

```python
def launch_admin_dashboard(user):
    if user.role != 'admin':
        messagebox.showerror("Access Denied", "Admin privileges required")
        return

    dashboard = AdminDashboard()
    dashboard.launch()
```

## Future Enhancements

Planned features:

- [ ] Export to CSV/Excel
- [ ] PDF report generation
- [ ] Email scheduled reports
- [ ] Real-time data updates
- [ ] User comparison tools
- [ ] Trend prediction
- [ ] Gender-based analytics (when data available)
- [ ] Custom date range filters
- [ ] Data export functionality

## Support

For issues or questions:

1. Check database connection
2. Verify required packages installed
3. Review error logs
4. Ensure database schema is up-to-date

## License

Part of the Soul Sense EQ Test project.
See LICENSE.txt for details.

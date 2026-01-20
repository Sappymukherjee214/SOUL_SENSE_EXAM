# Privacy Policy — SOUL_SENSE_EXAM

This Privacy Policy explains how **SOUL_SENSE_EXAM** collects, stores, uses, and retains personal data, and how users can request deletion of their data. The project is designed with privacy-first principles and stores data locally only.

---

## What Personal Data Is Collected

The application may collect the following personal or semi-personal data **only during app usage**:

- **Age group** (used for scoring and analysis, not exact date of birth)
- **Questionnaire answers** provided during the EQ assessment
- **Mood journal entries** (free-text reflections entered by the user, including optional daily wellbeing metrics such as sleep hours, stress levels, energy levels, work hours, screen time, and daily schedule)
- **Calculated EQ score and interpretation**

The application **does not collect names, email addresses, phone numbers, or network identifiers**.

---

## How Data Is Stored

- All personal data is stored **locally** on the user’s device
- Storage is handled using a **local SQLite database (`soulsense.db`)**
- No data is transmitted to external servers or third parties
- No cloud storage, analytics, or tracking tools are used

**Database Location (default):**

```
db/soulsense.db
```

---

## Data Processing and Analysis

### Journal Feature Data Handling

**Mood journal entries** are processed locally on the user's device using AI-powered sentiment analysis to provide emotional insights and patterns. This processing includes:

- **Sentiment Analysis**: Free-text reflections are analyzed using natural language processing (NLTK VADER) to generate sentiment scores (-100 to +100) and identify emotional patterns (e.g., stress indicators, growth-oriented thinking)
- **Pattern Recognition**: Text is scanned for keywords and phrases to categorize emotional themes (e.g., social focus, self-reflection)
- **Health Insights**: Recent journal entries (last 3 days) are analyzed for trends in wellbeing metrics to generate personalized health recommendations

**Important Notes:**
- All AI processing occurs **locally** on the user's device
- No journal content is transmitted to external servers or AI services
- Sentiment scores and patterns are stored alongside the original text for user review
- Users can view, edit, or delete their journal entries and associated analysis at any time

### Separation of Data Types

- **EQ Assessment Data** (questionnaire answers and calculated scores) is processed separately from journal data
- Journal entries are not used to modify or influence EQ scoring calculations
- Wellbeing metrics from journals (sleep, stress, etc.) are analyzed independently for health insights only

---

## Data Retention Policy

- Data is retained **only as long as it exists on the user’s local system**
- The application does **not enforce automatic expiration** by default
- Users have full control and may delete their data at any time

---

## Data Deletion Process

Users can request or perform data deletion using **one of the following methods**:

### Option 1: In-App Deletion (Recommended)

If supported in the UI:

- Use the **“Delete My Data”** or **“Reset App Data”** button
- This permanently removes all stored personal data from the local database

### Option 2: Manual Deletion (Always Available)

Users can manually delete their data by:

1. Closing the application
2. Deleting the database file:

   ```
   db/soulsense.db
   ```

3. Restarting the application (a fresh database will be created)

### Option 3: Documented Request

If using a shared or supervised setup:

- Users may contact the project maintainer via GitHub Issues
- Open an issue with the label **`data-deletion-request`**
- No justification is required

---

## Data Security

- Data is stored locally and never shared
- No external network access is required for app functionality
- Users are encouraged to protect their local system with appropriate OS-level security

---

## User Rights

Users have the right to:

- Access their locally stored data
- Delete all personal data at any time
- Use the application anonymously

---

## Policy Updates

This Privacy Policy may be updated to reflect future features or improvements. Changes will be documented in this file.

---

## Contact

For privacy-related questions or concerns:

- Open a GitHub Issue in this repository
- Use the **privacy** or **data-deletion-request** label

---

_Last updated: February 2026_

# 📔 Emotional Journal MVP

An AI-powered emotional journaling platform that helps you track, understand, and reflect on your emotional well-being through automated sentiment analysis and insightful visualizations.

## 🌟 Features

### Core Functionality
- ✍️ **Journal Entry Creation** - Write and save journal entries with rich text
- 🤖 **AI Sentiment Analysis** - Automatic emotion detection using Hugging Face Transformers
- 📊 **Interactive Dashboard** - Visualize your mood trends over time
- 💡 **Smart Insights** - Pattern detection and personalized emotional journey analysis
- 🔍 **Advanced Search** - Filter and search through all your entries
- 📥 **Data Export** - Download all your data as CSV for backup

### Visualizations
- 📈 Mood trend line charts with customizable time ranges
- 🎭 Emotion distribution pie charts
- ☁️ Word clouds of frequently used terms
- 📅 Day-of-week mood analysis
- 🔥 Journaling streak tracking
- 📊 Activity calendar heatmap

### Privacy & Security
- 🔒 **100% Local Storage** - All data stored on your device using SQLite
- 🚫 **No Cloud Sync** - Your private thoughts never leave your computer
- 🔐 **No Account Required** - No signup, no login, no tracking

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- 2GB free disk space (for AI models)

### Installation

1. **Navigate to the project directory**
   ```bash
   cd emotional_journal_mvp
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv

   # On macOS/Linux:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   **Note:** First-time installation will download ~300MB of AI models. This is a one-time process.

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**

   The app will automatically open at `http://localhost:8501`

### First-Time Setup

On first run, the application will:
- Create a `data/` directory for your journal database
- Download necessary AI models (Hugging Face Transformers)
- Initialize an empty SQLite database

**No configuration needed!** Just start writing.

## 📖 How to Use

### Creating Your First Entry

1. Click on **"📝 New Entry"** in the sidebar
2. (Optional) Select your current mood using the emoji buttons
3. Write your journal entry (minimum 20 characters)
4. Click **"Submit Entry"**
5. View AI-detected sentiment, emotions, and keywords
6. Navigate to the Dashboard to see your mood trends

### Viewing Your Dashboard

The dashboard provides:
- **Summary Cards**: Total entries, current streak, average mood, top emotion
- **Mood Trend Chart**: Interactive line chart of your emotional journey
- **Emotion Distribution**: Pie chart showing your most common emotions
- **Word Cloud**: Visual representation of frequently used words
- **Recent Entries**: Quick access to your last 10 journal entries

### Exploring Insights

Visit the **"💡 Insights"** page to discover:
- **Weekly Summary**: Auto-generated summary of your week
- **Pattern Detection**: Which days you feel best/worst
- **Streak Tracking**: Current and longest journaling streaks
- **Emotional Journey**: Your highest and lowest mood days

### Managing Entries

Go to **"📚 All Entries"** to:
- View all journal entries in a paginated list
- Filter by date range, sentiment, or keyword
- Sort by date or mood score
- Delete individual entries
- Search for specific content

### Exporting Your Data

1. Navigate to **"📥 Export Data"**
2. Preview your data
3. Click **"Download CSV"**
4. Save the timestamped CSV file to your preferred location

## 🛠️ Technical Details

### Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **AI/ML**:
  - Hugging Face Transformers (`distilbert-base-uncased-finetuned-sst-2-english`)
  - Emotion detection (`j-hartmann/emotion-english-distilroberta-base`)
  - TextBlob (fallback sentiment analysis)
- **Database**: SQLite (local file-based database)
- **Visualizations**: Plotly (interactive charts), WordCloud
- **Data Processing**: Pandas, NumPy

### Project Structure

```
emotional_journal_mvp/
├── app.py                       # Main Streamlit application
├── requirements.txt             # Python dependencies
├── create_sample_data.py        # Sample data generator
├── README.md                    # This file
├── utils/
│   ├── __init__.py
│   ├── data_manager.py          # SQLite database operations
│   ├── sentiment_analyzer.py   # AI sentiment analysis
│   └── visualizations.py        # Chart generation
└── data/
    └── journal_entries.db       # Your journal database (auto-created)
```

### Database Schema

```sql
CREATE TABLE journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    entry_text TEXT NOT NULL,
    user_selected_mood TEXT,
    ai_sentiment_label TEXT,        -- POSITIVE, NEGATIVE, NEUTRAL
    ai_sentiment_score REAL,         -- -1 to 1 scale
    ai_confidence REAL,              -- 0 to 1
    word_count INTEGER,
    detected_emotions TEXT,          -- JSON array
    keywords TEXT                    -- JSON array
);
```

## 🎨 Sample Data

Want to see the app in action before writing entries? Generate sample data:

```bash
python create_sample_data.py
```

This creates 16 realistic journal entries spanning the last 16 days with varying sentiments.

**Optional:** Generate a specific number of entries:
```bash
python create_sample_data.py --count 5
```

## 🐛 Troubleshooting

### App won't start

**Problem:** `streamlit: command not found`

**Solution:** Make sure you've activated your virtual environment and installed dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

**Problem:** `ModuleNotFoundError: No module named 'transformers'`

**Solution:** Install requirements again:
```bash
pip install -r requirements.txt
```

### Model download is slow

**Problem:** First run takes a long time

**Solution:** This is normal! The AI models are ~300MB and download only once. Subsequent runs will be fast.

**Tip:** Make sure you have a stable internet connection for the first run.

### Charts not showing

**Problem:** Visualizations appear blank

**Solution:**
1. Clear your browser cache
2. Refresh the page (F5 or Ctrl+R)
3. Try a different browser (Chrome, Firefox, Edge)

### Database errors

**Problem:** `sqlite3.OperationalError: unable to open database file`

**Solution:** Check file permissions:
```bash
# Make sure the data directory is writable
chmod 755 data/
```

### Sentiment analysis fails

**Problem:** Entries save but show "NEUTRAL" for everything

**Solution:** This indicates the AI model failed to load. The app uses TextBlob fallback. Check:
```bash
# Reinstall transformers
pip uninstall transformers torch
pip install transformers torch
```

## 📊 Performance Notes

- **App startup**: < 5 seconds
- **Entry submission**: 2-3 seconds (includes AI analysis)
- **Dashboard load**: < 2 seconds
- **Chart rendering**: < 1 second

**GPU Support:** The app automatically detects and uses GPU if available (CUDA). CPU-only is perfectly fine for this application.

## 🔒 Privacy & Data

### Where is my data stored?

All data is stored locally in `data/journal_entries.db` on your computer. This is a SQLite database file.

### Can I backup my data?

Yes! Multiple ways:
1. Use the built-in **Export to CSV** feature
2. Copy the entire `data/` directory
3. Copy just the `journal_entries.db` file

### What happens to my AI analysis?

Sentiment analysis runs **locally on your machine**. Your journal entries are never sent to any server or cloud service.

### Can I delete my data?

Yes! To completely remove all data:
```bash
rm -rf data/  # macOS/Linux
rmdir /s data  # Windows
```

Or delete individual entries using the "Delete" button in the app.

## 🚧 Known Limitations (MVP Version)

This is a Minimum Viable Product for testing. Current limitations:

- ❌ No user authentication (single user per installation)
- ❌ No cloud backup/sync
- ❌ No mobile app (web only)
- ❌ No voice/video entries
- ❌ No collaborative features
- ❌ No scheduled reminders
- ❌ No data encryption (file system permissions only)

## 🔮 Future Enhancements

Potential features for future versions:

- 🔐 Multi-user support with authentication
- ☁️ Optional cloud backup
- 📱 Mobile-responsive design
- 🎤 Voice recording support
- 🔔 Customizable journaling reminders
- 🌍 Multi-language support
- 📈 Advanced analytics (emotion prediction, trend forecasting)
- 🎨 Customizable themes
- 📎 Attachment support (photos, documents)
- 🤝 Optional therapist/coach sharing

## 🆘 Getting Help

### Common Questions

**Q: How accurate is the sentiment analysis?**

A: The AI model (DistilBERT) achieves ~85% accuracy on benchmark datasets. Results may vary based on writing style.

**Q: Can I use this on multiple computers?**

A: Yes! Just copy the entire project folder (including the `data/` directory) to another computer.

**Q: Is there a word limit for entries?**

A: Minimum 20 characters, maximum 5000 characters per entry.

**Q: Can I edit existing entries?**

A: Not in the MVP version. You can delete and recreate entries.

**Q: Does this work offline?**

A: Yes! After the initial model download, the app works completely offline.

### Reporting Issues

Found a bug or have a suggestion? Please:

1. Check the troubleshooting section above
2. Search existing issues on GitHub
3. Create a new issue with:
   - Description of the problem
   - Steps to reproduce
   - Your OS and Python version
   - Error messages (if any)

## 📝 Usage Tips

### For Best Results

1. **Write regularly** - Daily journaling provides better trend insights
2. **Be authentic** - Write naturally; the AI adapts to your style
3. **Write enough** - Longer entries (100+ words) yield better analysis
4. **Review insights weekly** - Check the Insights page to spot patterns
5. **Export regularly** - Backup your data monthly

### Writing Prompts

Not sure what to write? Try these:

- How was your day?
- What are you grateful for?
- What challenged you today?
- What made you smile?
- What are you looking forward to?
- What did you learn today?

## 🧪 Testing Checklist

For beta testers:

- [ ] Create a new journal entry
- [ ] View entry in dashboard
- [ ] Check sentiment analysis accuracy
- [ ] Navigate all pages (New Entry, Dashboard, Insights, All Entries, Export)
- [ ] Filter entries by date/sentiment/keyword
- [ ] Delete an entry
- [ ] Export data to CSV
- [ ] Restart app and verify data persists
- [ ] Test with entries of varying lengths
- [ ] Check visualizations render correctly

## 📄 License

This is an MVP (Minimum Viable Product) for testing purposes.

## 🙏 Acknowledgments

- **Hugging Face** - For open-source transformer models
- **Streamlit** - For the incredible web framework
- **Contributors** - To all beta testers providing feedback

---

**Version:** 1.0.0 MVP
**Last Updated:** December 2024
**Status:** Beta Testing

---

## Quick Command Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py

# Generate sample data
python create_sample_data.py

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Backup your data
cp -r data/ backup/  # macOS/Linux
xcopy data backup /E /I  # Windows
```

---

**Happy Journaling! 📔✨**

For questions or feedback, please open an issue on GitHub or contact the development team.

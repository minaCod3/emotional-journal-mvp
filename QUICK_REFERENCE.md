# Quick Reference Guide

## 🚀 Installation (First Time)

```bash
cd emotional_journal_mvp
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## ▶️ Running the App

```bash
cd emotional_journal_mvp
source venv/bin/activate  # Windows: venv\Scripts\activate
streamlit run app.py
```

Or use the quick start script (macOS/Linux):
```bash
./quick_start.sh
```

## 📝 Common Tasks

### Generate Sample Data
```bash
python create_sample_data.py
```

### Export Your Data
Use the "📥 Export Data" page in the app, or manually copy:
```bash
cp data/journal_entries.db backup/
```

### Clear All Data
```bash
rm -rf data/
```

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## 🔧 Troubleshooting

### App Won't Start
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Model Download Issues
First run downloads ~300MB. Ensure stable internet connection.

### Database Errors
```bash
# Check permissions
chmod 755 data/
```

## 📊 Features at a Glance

- **📝 New Entry**: Write journal entries (20-5000 chars)
- **📊 Dashboard**: View mood trends and statistics
- **💡 Insights**: Discover patterns and streaks
- **📚 All Entries**: Browse, filter, and search
- **📥 Export**: Download CSV backup

## 🎨 Color Meanings

- 🟢 Green: Positive mood (score > 0.3)
- 🟡 Yellow: Neutral mood (-0.3 to 0.3)
- 🔴 Red: Negative mood (< -0.3)

## 📁 File Locations

- **Database**: `data/journal_entries.db`
- **Exports**: Downloads folder (CSV files)
- **Logs**: Terminal output

## 🆘 Need Help?

1. Check README.md for detailed documentation
2. Check PROJECT_SUMMARY.md for technical details
3. Search error messages in troubleshooting section

## ⌨️ Keyboard Shortcuts

- `Ctrl+C`: Stop the application
- `Ctrl+Shift+R`: Reload browser (clear cache)
- `R`: Rerun Streamlit app (in terminal)

## 🔒 Privacy

All data stored locally in `data/journal_entries.db`
No cloud sync • No tracking • No accounts

# 🚀 START HERE - Quick Setup Guide

Your Emotional Journal MVP is ready to use!

## ✅ Dependencies Installed Successfully!

All Python packages have been installed with Python 3.13.2 compatible versions.

---

## 📝 How to Start the Application

### Option 1: Simple Command (Recommended)

Open Terminal in this directory and run:

```bash
source venv/bin/activate
streamlit run app.py
```

The app will open automatically at: **http://localhost:8501**

---

### Option 2: Full Manual Steps

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Run the application:**
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** to: http://localhost:8501

---

## 🎨 Optional: Generate Sample Data

If you want to test with pre-populated journal entries:

```bash
source venv/bin/activate
python create_sample_data.py
```

**Note:** First run will download AI models (~300MB) and may take 2-5 minutes.

---

## 🛑 To Stop the Application

Press `Ctrl+C` in the terminal

---

## 📱 First-Time Usage

1. Start the app (see above)
2. Click on **"📝 New Entry"** in the sidebar
3. Write your first journal entry (minimum 20 characters)
4. Click **"Submit Entry"**
5. View AI-detected sentiment and emotions
6. Explore the **Dashboard** to see your mood trends

---

## 🔧 Troubleshooting

### If Streamlit asks for email on first run:
- Just press Enter to skip
- Or edit `~/.streamlit/config.toml` to disable prompts

### If sentiment analysis is slow:
- First analysis downloads models (~300MB)
- Subsequent analyses will be fast

### If you get import errors:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📂 Project Files

- **app.py** - Main application
- **utils/** - Core modules (database, sentiment, visualizations)
- **data/** - Your journal database (auto-created)
- **README.md** - Full documentation

---

## 🎯 Next Steps

1. ✅ Dependencies installed
2. ✅ Virtual environment created
3. → **Run:** `streamlit run app.py`
4. → Start journaling!

---

## 🆘 Need Help?

Check **README.md** for comprehensive documentation and troubleshooting.

---

**Ready to start! Run:** `streamlit run app.py`

# How to Share This Application

You have two main options for sharing this program with your friend:

## Option 1: Send Source Code (Recommended for Testing)
**Best for:** Developers or tech-savvy users.
**Pros:** Easy to update, small file size (kB/MB).
**Cons:** The receiver **MUST** have Python installed.

**Instructions:**
1.  Zip the entire project folder.
2.  Send the Zip file.
3.  Tell your friend to:
    *   Install **Python 3.10+** (from python.org).
    *   **Check "Add Python to PATH"** during installation.
    *   Double-click `start_app.bat`.

## Option 2: Standalone Executable (.exe)
**Best for:** End users.
**Pros:** Runs on any Windows PC without installing Python.
**Cons:** Large file size (200MB+), slower first launch.

**Instructions:**
1.  Go to the `dist` folder.
2.  Send the `FinancialPredictorAI.exe` file to your friend.
3.  Tell them to double-click it.
    *   *Note:* The first launch might take 10-20 seconds as it unpacks.
    *   *Note:* Antivirus might flag it because it's unsigned. This is normal for self-built apps.

### Configuration
The `.exe` will look for a `.env` file in the **same folder** where it is located.
If your friend wants to use OKX/Paper Trading, they must create a `.env` file next to the `.exe`.

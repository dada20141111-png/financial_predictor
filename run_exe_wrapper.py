import os
import sys
import streamlit.web.cli as stcli

def resolve_path(path):
    """
    Resolves path to resources whether running from source or frozen in EXE.
    """
    if getattr(sys, "frozen", False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app 
        # path into variable _MEIPASS'.
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

if __name__ == "__main__":
    # 1. Identify the path to the main streamlit app file
    # We assume 'src' is bundled into the root of the EXE
    app_path = resolve_path(os.path.join("src", "app.py"))
    
    # 2. Set environment variables if needed
    # (Streamlit sometimes needs this to know where to look for config)
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    
    # 3. Construct the CLI command arguments
    # Equivalent to: streamlit run src/app.py --global.developmentMode=false
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
    ]
    
    print(f"Launching Financial Predictor from: {app_path}")
    
    # Debug: Check if file exists
    if not os.path.exists(app_path):
        print(f"ERROR: Application file not found at {app_path}")
        if getattr(sys, "frozen", False):
            print(f"PyInstaller _MEIPASS: {sys._MEIPASS}")
            try:
                print(f"Contents of src: {os.listdir(os.path.join(sys._MEIPASS, 'src'))}")
            except Exception as e:
                print(f"Could not list src: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

    # 4. Invoke Streamlit with safety wrapper
    try:
        sys.exit(stcli.main())
    except Exception as e:

        err_msg = "\n\nCRITICAL ERROR DURING EXECUTION:\n"
        import traceback
        traceback_str = traceback.format_exc()
        err_msg += traceback_str
        print(err_msg)
        
        # Self-Diagnostic: Write crash report
        try:
            with open("crash_report.txt", "w", encoding="utf-8") as f:
                f.write(err_msg)
                f.write("\n\n--- BUNDLED FILE INVENTORY ---\n")
                if getattr(sys, "frozen", False):
                    f.write(f"Root: {sys._MEIPASS}\n")
                    for root, dirs, files in os.walk(sys._MEIPASS):
                        for file in files:
                            # relative path for readability
                            rel_path = os.path.relpath(os.path.join(root, file), sys._MEIPASS)
                            f.write(f"{rel_path}\n")
                else:
                    f.write("Not running in frozen mode.\n")
            print("\n>> A 'crash_report.txt' has been generated in this folder.")
            print(">> Please check it to see exactly what files are present.")
        except Exception as write_err:
            print(f"Could not write crash report: {write_err}")

        print("\n")
        input("Press Enter to close window...")

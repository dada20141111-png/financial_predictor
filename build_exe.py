import PyInstaller.__main__
import os
import streamlit
import shutil
from PyInstaller.utils.hooks import copy_metadata

# 1. Get Streamlit Path for static assets
st_path = os.path.dirname(streamlit.__file__)
st_static = os.path.join(st_path, "static")

# 2. Define data to bundle
# Format: (source, destination)
# Windows uses ; as separator in CLI, but PyInstaller list format handles it.
datas = [
    (st_static, "streamlit/static"),  # Streamlit UI assets
    ("src", "src"),                   # Our source code
    ("README.md", "."),               # Docs
    ("USER_MANUAL.md", ".")           # User Manual
]

# Robustly collect xgboost data and binaries, but avoid importing submodules (like testing)
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# 1. Data (includes VERSION)
datas += collect_data_files('xgboost')

# 2. Binaries (includes .dll)
binaries = collect_dynamic_libs('xgboost')

# 3. Hidden imports - relying on static analysis + explicit mention below
# We do NOT use collect_submodules because it triggers imports of testing suites
hiddenimports = []

# Copy metadata for packages that use importlib.metadata
datas += copy_metadata("streamlit")
datas += copy_metadata("click")
datas += copy_metadata("scipy")
datas += copy_metadata("pandas")

if os.path.exists(".env.example"):
    datas.append((".env.example", "."))
if os.path.exists("paper_balance.json"):
    datas.append(("paper_balance.json", "."))

# 3. Construct PyInstaller arguments
args = [
    "run_exe_wrapper.py",             # Main script
    "--name=FinancialPredictorAI",    # Executable name
    "--onefile",                      # Single .exe file
    "--clean",                        # Clean cache
    "--noconfirm",                    # Overwrite output
    "--console",                      # Keep console open to see errors
    
    # Hidden imports - critical for Streamlit
    "--hidden-import=streamlit",
    "--hidden-import=pandas",
    "--hidden-import=numpy",
    "--hidden-import=plotly",
    "--hidden-import=sklearn",
    "--hidden-import=xgboost",
    "--hidden-import=sklearn.neighbors._typedefs",
    "--hidden-import=sklearn.neighbors._quad_tree",
    "--hidden-import=sklearn.tree._utils",
    "--hidden-import=sklearn.utils._cython_blas",
    "--hidden-import=sklearn.neural_network",
    "--hidden-import=sklearn.neural_network._multilayer_perceptron",
    "--hidden-import=sklearn.utils._weight_vector",
    "--hidden-import=yfinance",
    "--hidden-import=ccxt",
    "--hidden-import=python_dotenv",
    "--hidden-import=altair.vegalite.v5",
    "--hidden-import=rich",
    "--hidden-import=click",
    "--hidden-import=toml",
    "--hidden-import=requests",
    "--hidden-import=pyarrow",
    "--hidden-import=PIL",
    "--hidden-import=email_validator", # Often needed by Pydantic/Streamlit
    "--hidden-import=scipy.special.cython_special", # Scipy often needs this
    "--hidden-import=streamlit.runtime.scriptrunner.magic_funcs",
    "--hidden-import=streamlit.runtime.scriptrunner.script_runner",
    "--hidden-import=seaborn",
    "--hidden-import=matplotlib.pyplot",
    "--hidden-import=optuna",
    "--hidden-import=textblob",
    "--hidden-import=feedparser",
    "--hidden-import=nltk",
    "--hidden-import=sqlite3", # Optuna dependency
    "--hidden-import=sqlalchemy.dialects.sqlite", # Optuna dependency
] + [f"--hidden-import={x}" for x in hiddenimports]

# Add datas
for source, dest in datas:
    # Proper formatting for add-data argument: "source;dest" on Windows
    args.append(f"--add-data={source}{os.pathsep}{dest}")

# Add binaries
for source, dest in binaries:
    args.append(f"--add-binary={source}{os.pathsep}{dest}")

# 4. Run Build
print("Building EXE... this may take a few minutes.")
PyInstaller.__main__.run(args)

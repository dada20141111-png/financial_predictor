# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run_exe_wrapper.py'],
    pathex=[],
    binaries=[('C:\\Users\\wh\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\xgboost\\lib\\xgboost.dll', 'xgboost\\lib')],
    datas=[('C:\\Users\\wh\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\streamlit\\static', 'streamlit/static'), ('src', 'src'), ('README.md', '.'), ('USER_MANUAL.md', '.'), ('C:\\Users\\wh\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\xgboost\\py.typed', 'xgboost'), ('C:\\Users\\wh\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\xgboost\\lib\\xgboost.dll', 'xgboost\\lib'), ('C:\\Users\\wh\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\xgboost\\VERSION', 'xgboost'), ('C:\\Users\\wh\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\streamlit-1.53.1.dist-info', 'streamlit-1.53.1.dist-info'), ('C:\\Users\\wh\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\click-8.3.1.dist-info', 'click-8.3.1.dist-info'), ('C:\\Users\\wh\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\scipy-1.17.0.dist-info', 'scipy-1.17.0.dist-info'), ('C:\\Users\\wh\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\pandas-2.3.3.dist-info', 'pandas-2.3.3.dist-info'), ('.env.example', '.')],
    hiddenimports=['streamlit', 'pandas', 'numpy', 'plotly', 'sklearn', 'xgboost', 'sklearn.neighbors._typedefs', 'sklearn.neighbors._quad_tree', 'sklearn.tree._utils', 'sklearn.utils._cython_blas', 'sklearn.neural_network', 'sklearn.neural_network._multilayer_perceptron', 'sklearn.utils._weight_vector', 'yfinance', 'ccxt', 'python_dotenv', 'altair.vegalite.v5', 'rich', 'click', 'toml', 'requests', 'pyarrow', 'PIL', 'email_validator', 'scipy.special.cython_special', 'streamlit.runtime.scriptrunner.magic_funcs', 'streamlit.runtime.scriptrunner.script_runner', 'seaborn', 'matplotlib.pyplot', 'optuna', 'textblob', 'feedparser', 'nltk', 'sqlite3', 'sqlalchemy.dialects.sqlite'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FinancialPredictorAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

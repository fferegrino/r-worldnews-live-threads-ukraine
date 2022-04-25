import os
import shutil

if not os.path.exists("kaggle"):
    os.mkdir("kaggle")
shutil.make_archive("./kaggle/data", "zip", "./data")

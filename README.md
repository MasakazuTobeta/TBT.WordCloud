# TBT.WordCloud
![TBT.WordCloud/Sample](./image/sample.png)

# Setup environment
```
python3 -m venv .venv
./.venv\Scripts\deactivate
pip install -r requirements.txt
```

# Quick start
```
./.venv\Scripts\deactivate
python main.py
```

# User's manual
Please check the [manual](./UserManual.md)

# Build application
```
pyinstaller --collect-data unidic_lite \
            --collect-data wordcloud \
            --hidden-import wordcloud \
            --hidden-import unidic_lite \
            --name 'TBT.WordCloud'\
            --icon ./image/icon.ico\
            --onefile --noconsole main.py
cp -r ./image ./dist/
```

# Executable files
https://www.dropbox.com/sh/xcm3zsxrtq9h9ee/AABmC_rggr3loPwaVys7Nr21a?dl=0

# Commercial License
In principle, the open source license is [LICENSE](./LICENSE) file, but commercial use is prohibited. This software is also available for licensing via TOBETA.

# TBT.WordCloud
WordCloud Generator

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

# User manual
Please check the [user manual(jp)](./UserManual.md)

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

# Commercial License
In principle, the open source license is [LICENSE](. /LICENSE) file, but commercial use is prohibited. This software is also available for licensing via TOBETA.

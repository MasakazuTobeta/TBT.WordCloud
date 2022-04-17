# TBT.WordCloud
WordCloud Generator

# Build application
```
pyinstaller --collect-data unidic_lite \
            --collect-data wordcloud \
            --hidden-import wordcloud \
            --hidden-import unidic_lite \
            --name 'TBT.WordCloud'\
            --icon ./image/icon.ico\
            --splash './image/splash.png'\
            --onefile --noconsole main.py
cp -r ./image ./dist/
```

# Commercial License
In principle, the open source license is [LICENSE](. /LICENSE) file, but commercial use is prohibited. This software is also available for licensing via TOBETA.

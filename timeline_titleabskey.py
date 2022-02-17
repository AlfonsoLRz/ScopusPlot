import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import pandas as pd
from pybliometrics.scopus import ScopusSearch


data_sources = ['thermal', 'multispectral', 'hyperspectral']
data_sources_titles = ['Thermal research', 'Multispectral research', 'Hyperspectral research']

title_font = {'fontname': 'Palatino Linotype', 'size': 11}
regular_font = {'fontname':'Palatino Linotype'}
font = font_manager.FontProperties(family='Palatino Linotype', size=9)

fig = plt.figure(figsize=(6, 3.5))
ax = fig.add_subplot(111)

for i in range(len(data_sources)):
    search = ScopusSearch('TITLE-ABS-KEY((image OR (point AND cloud)) AND ' + data_sources[i] + ' AND (crop OR forest) '
                                                                                                'AND monitoring)',
                          download=True)
    df = pd.DataFrame(pd.DataFrame(search.results))
    df['coverDateFinal'] = pd.to_datetime(df['coverDate'], format="%Y-%m-%d")
    df['year'] = pd.DatetimeIndex(df['coverDateFinal']).year
    df_occurrences = pd.DataFrame(df['year'].value_counts()).sort_index().reset_index()

    if i == 0:
        ax.plot(df_occurrences['index'], df_occurrences['year'], label=data_sources_titles[i], marker='.')
    else:
        ax.plot(df_occurrences['index'], df_occurrences['year'], label=data_sources_titles[i])

for label in ax.get_xticklabels():
    label.set_fontproperties(font)

for label in ax.get_yticklabels():
    label.set_fontproperties(font)

ax.legend(prop=font)
plt.title('2D/3D Thermal, multispectral and hyperspectral research', **title_font, pad=15)
plt.ylabel('Number of Publications', **regular_font)
plt.xlabel('Year', **regular_font)
plt.tight_layout()
plt.savefig('Timeline.png')
plt.show()



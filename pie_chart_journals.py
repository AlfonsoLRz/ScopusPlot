import matplotlib.font_manager as font_manager
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import pandas as pd
from pybliometrics.scopus import ScopusSearch
import re


def process_journal_title(title):
    title = re.sub("[\(\[].*?[\)\]]", "", title)

    count = 0
    title_mod = ""
    for char in range(len(title)):
        title_mod += title[char]
        if count > MAX_STR_LENGTH and title[char] == " ":
            title_mod += '\n'
            count = 0
        count += 1

    return title_mod


RADIUS_SIZE = 0.4
MAX_STR_LENGTH = 25

data_sources = ['thermal', 'multispectral', 'hyperspectral']
data_sources_titles = ['Thermal Publications', 'Multispectral Publications', 'Hyperspectral Publications']

title_font = {'fontname': 'Palatino Linotype', 'size': 11, 'weight': 'bold'}
regular_font = {'fontname': 'Palatino Linotype', 'size': 10}
pie_font = {'fontname': 'Palatino Linotype', 'size': 8}
font = font_manager.FontProperties(family='Palatino Linotype', size=8)

for i in range(len(data_sources)):
    search = ScopusSearch('TITLE-ABS-KEY(3D AND point AND cloud AND ' + data_sources[i] + ')', download=True)
    df = pd.DataFrame(pd.DataFrame(search.results))
    df_occurrences = pd.DataFrame(df['publicationName'].value_counts()).reset_index()
    df_occurrences = df_occurrences.sort_values(['publicationName'], ascending=False).head(6)
    df_occurrences = df_occurrences.rename(columns={'index': 'pubName', 'publicationName': 'count'})
    df_occurrences['pubSummary'] = df_occurrences.apply(lambda row: process_journal_title(row['pubName']), axis=1)

    df_oa_occurrences = pd.DataFrame(df[['publicationName', 'openaccess']])
    df_oa_occurrences = pd.DataFrame(df_oa_occurrences.groupby(by='publicationName').openaccess.sum()).reset_index()

    df_merge = pd.merge(df_occurrences, df_oa_occurrences, how='left', left_on='pubName', right_on='publicationName')
    df_merge['other'] = df_merge.apply(lambda row: row['count'] - row['openaccess'], axis=1)

    flatten_array = df_merge[['openaccess', 'other']].stack().values
    colors = []
    labels = [ "Open Access", "Other Method"]
    for _ in range(len(flatten_array / 2)):
        colors = colors + ['y', 'k']

    fig = plt.figure(figsize=(6, 3))
    ax = fig.add_subplot(111)

    print()
    #ax.pie(df_occurrences['count'], labels=df_occurrences['pubSummary'], autopct='%1.1f%%', shadow=False)
    _, _, pct = ax.pie(df_merge['count'], labels=df_merge['pubSummary'], radius=1, autopct='%1.1f%%', startangle=90,
                       wedgeprops=dict(width=RADIUS_SIZE, edgecolor='w'), textprops=pie_font,
                       pctdistance=0.8, labeldistance=1.2)
    for autotext in pct:
        autotext.set_color('white')

    ax.pie(flatten_array, radius=1 - RADIUS_SIZE, colors=colors,
           wedgeprops=dict(width=RADIUS_SIZE / 4, edgecolor='w'))

    for label in ax.get_xticklabels():
        label.set_fontproperties(font)

    for label in ax.get_yticklabels():
        label.set_fontproperties(font)

    # Compose legends
    legend_elements = [Patch(facecolor=colors[0], label=labels[0]),
                       Patch(facecolor=colors[1], label=labels[1])]

    #ax.legend(prop=font, bbox_to_anchor=[1.3, 0.5])
    ax.legend(prop=font, handles=legend_elements, bbox_to_anchor=[.0, 1.12])
    plt.title('Top-6 journals on publishing research of 3D ' + data_sources[i] + ' modelling', **title_font, pad=25)
    plt.tight_layout()
    plt.savefig('PieChart' + data_sources[i] + '.png', dpi=1000)
    plt.show()
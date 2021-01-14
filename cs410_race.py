import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#%matplotlib inline
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from collections import Counter
from pylab import rcParams

# Open URL and create a BeautifulSoup object to work with:
url = "http://www.hubertiming.com/results/2017GPTR10K"
html = urlopen(url)
soup = BeautifulSoup(html, 'lxml')

# Get all the table rows:
rows = soup.find_all('tr')

# Use BeautifulSoup to to extract and clean table data:
'''
list_rows = []
for row in rows:
    row_td = row.find_all('td')
    str_cells = str(row_td)
    cleantext = BeautifulSoup(str_cells, "lxml").get_text()
    list_rows.append(cleantext)
'''

# Use regex to extract and clean table data:
list_rows = []
for row in rows:
    cells = row.find_all('td')
    str_cells = str(cells)
    clean = re.compile('<.*?>')
    clean2 = (re.sub(clean, '',str_cells))
    list_rows.append(clean2)

# Create dataframe using pandas:
df = pd.DataFrame(list_rows)

# Split into columns and remove opening brackets:
df1 = df[0].str.split(',', expand=True)
df1[0] = df1[0].str.strip('[')

# Extract the headers:
col_labels = soup.find_all('th')
all_header = []
col_str = str(col_labels)
cleantext2 = BeautifulSoup(col_str, "lxml").get_text()
all_header.append(cleantext2)

# Create a dataframe for headers and split into columns:
df2 = pd.DataFrame(all_header)
df3 = df2[0].str.split(',', expand=True)

# Combine the header df and body df: 
frames = [df3, df1]
df4 = pd.concat(frames)

# Use the first row as header row 
df5 = df4.rename(columns=df4.iloc[0])

# Drop any rows with missing data:
df6 = df5.dropna(axis=0, how='any')

# Drop the first row, as it's been copied as header row:
df7 = df6.drop(df6.index[0])

# A little more cleanup:
df7.rename(columns={'[Place': 'Place'},inplace=True)
df7.rename(columns={' Team]': 'Team'},inplace=True)
df7.rename(columns={' Name': 'Name'},inplace=True)
df7['Team'] = df7['Team'].str.strip(']')
df7['Team'] = df7['Team'].str.strip()
df7['Name'] = df7['Name'].str.strip()

# Use a loop to separate hours:mins:secs and convert 'Chip Time' to minutes
time_list = df7[' Chip Time'].tolist()
time_mins = []
for i in time_list:
    count = Counter(i)
    if count[':'] == 2: 
        h, m, s = i.split(':')
        math = (int(h) * 3600 + int(m) * 60 + int(s))/60
    elif count[':'] == 1:
        m, s = i.split(':')
        math = (int(m) * 60 + int(s))/60
    time_mins.append(math)

# Add a column of 'Chip Time' converted to mins:
df7['Runner_mins'] = time_mins

# Show some metrics calculated from our data:
#print(df7.describe(include=[np.number]))

# Set some parameters and create a boxplot of the data:
rcParams['figure.figsize'] = 15, 5
'''
df7.boxplot(column='Runner_mins')
plt.grid(True, axis='y')
plt.ylabel('Chip Time')
plt.xticks([1], ['Runners'])
plt.show()
'''

# distplot() is deprecated and didn't work, so I modified to use histplot() (could have modified for displot() too).
#seaborn.histplot(data=None, *, x=None, y=None, hue=None, weights=None, stat='count', bins='auto', binwidth=None, binrange=None, discrete=None, cumulative=False, common_bins=True, common_norm=True, multiple='layer', element='bars', fill=True, shrink=1, kde=False, kde_kws=None, line_kws=None, thresh=0, pthresh=None, pmax=None, cbar=False, cbar_ax=None, cbar_kws=None, palette=None, hue_order=None, hue_norm=None, color=None, log_scale=None, legend=True, ax=None, **kwargs)

#seaborn.displot(data=None, *, x=None, y=None, hue=None, row=None, col=None, weights=None, kind='hist', rug=False, rug_kws=None, log_scale=None, legend=True, palette=None, hue_order=None, hue_norm=None, color=None, col_wrap=None, row_order=None, col_order=None, height=5, aspect=1, facet_kws=None, **kwargs)

# Set the x-axis and create a histogram of the data:
x = df7['Runner_mins']
'''
#ax = sns.distplot(x, hist=True, kde=True, rug=False, color='m', bins=25, hist_kws={'edgecolor':'black'})
ax = sns.histplot(x, kde=True, color='m', bins=25) # rug=False, hist_kws={'edgecolor':'black'})
#plt.show()
'''

# Create a histogram comparing male and female distributions:
'''
f_fuko = df7.loc[df7[' Gender']==' F']['Runner_mins']
m_fuko = df7.loc[df7[' Gender']==' M']['Runner_mins']
#sns.distplot(f_fuko, hist=True, kde=True, rug=False, hist_kws={'edgecolor':'black'}, label='Female')
sns.histplot(f_fuko, kde=True, label='Female')
#sns.distplot(m_fuko, hist=False, kde=True, rug=False, hist_kws={'edgecolor':'black'}, label='Male')
sns.histplot(m_fuko, kde=True, label='Male')
plt.legend()
plt.show()
'''

# Show stats by gender:
g_stats = df7.groupby(" Gender", as_index=True).describe()
print(g_stats)

# Create boxplots comparing male and female distributions:
df7.boxplot(column='Runner_mins', by=' Gender')
plt.ylabel('Chip Time')
plt.suptitle("")
plt.show()


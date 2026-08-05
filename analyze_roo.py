import pandas as pd
import numpy as np

df = pd.read_csv(r'c:\Users\DELL\Downloads\roo_data.csv')
print('Shape:', df.shape)
print('\nColumns:', list(df.columns))
print('\nTarget distribution:')
print(df['Suggested Job Role'].value_counts())
print('\nMissing values:')
print(df.isnull().sum())
print('\nDtypes:')
print(df.dtypes.value_counts())
print('\nSample target classes:')
print(df['Suggested Job Role'].unique()[:20])
print('\nNumeric columns stats:')
numeric_cols = df.select_dtypes(include=[np.number]).columns
print(df[numeric_cols].describe())
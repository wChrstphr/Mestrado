import pandas as pd
data = pd.read_csv('google-us-data.csv.gz', nrows=100, compression='gzip',
                   error_bad_lines=False)
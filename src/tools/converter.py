import json
import pandas as pd

INPUT_JSON_FILENAME = 'src/utils/interrogation_log.json'
OUTPUT_XLSX_FILENAME = 'src/utils/interrogation_log.xlsx'

with open(INPUT_JSON_FILENAME, 'r') as f:
    d = json.load(f)

df = pd.DataFrame.from_dict(d, 'index')

writer = pd.ExcelWriter(OUTPUT_XLSX_FILENAME)
df.to_excel(writer)
#with open(OUTPUT_XLSX_FILENAME, 'w') as f:
#    writer = pd.ExcelWriter
#    f.write(df.to_excel())
# Script to parse the HTML file and concatenate the relevant tables (from Table 2 onwards)

# Required imports
import pandas as pd
from bs4 import BeautifulSoup

def parse_and_concatenate_tables(html_file_path):
    """
    Parses the given HTML file, extracts tables from Table 2 onwards, 
    and concatenates them into a single DataFrame.

    :param html_file_path: Path to the HTML file.
    :return: Concatenated DataFrame of the tables.
    """
    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract tables
    tables = soup.find_all('table')

    # Parse and concatenate tables from Table 2 onwards
    dataframes = []
    for table in tables[2:]:
        df = pd.read_html(str(table))[0]
        dataframes.append(df)



    concatenated_df = pd.concat(dataframes, ignore_index=True)

    # create new column names from row 0
    concatenated_df.columns = concatenated_df.iloc[0]
    # drop row 0
    concatenated_df = concatenated_df.drop(0)
    # reset index
    concatenated_df = concatenated_df.reset_index(drop=True)

    # drop datas in row if ther similar to  Columnnames
    concatenated_df = concatenated_df[concatenated_df['Material'] != 'Material']

    return concatenated_df

def readstock():
# Usage of the function
    file_path = 'TESTDATEN/Job EC_LE_DE_R_DE2_WM_STOCK_REPORT, Step 1.htm'  # Replace with your actual file path
    concatenated_dataframe = parse_and_concatenate_tables(file_path)
    return concatenated_dataframe

# You can now work with 'concatenated_dataframe' as needed


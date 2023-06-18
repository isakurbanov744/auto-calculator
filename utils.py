import xlrd
import pandas as pd
import sqlite3


def load_category_mapping():
    conn = sqlite3.connect('category_mapping.db')
    c = conn.cursor()
    c.execute("SELECT category, codes FROM mapping")
    rows = c.fetchall()
    conn.close()

    category_mapping = {}
    for row in rows:
        category = row[0]
        codes = row[1].split(',')
        category_mapping[category] = codes

    return category_mapping


def extract_sales_data(sheet):
    """
    Extract sales data from an Excel sheet.

    Args:
        sheet (Object): The Excel sheet.

    Returns:
        List: List of extracted data from the Excel file.
    """
    sales_data = []
    for row in range(1, sheet.nrows):
        try:
            row_data = sheet.row_values(row)
            code = str(int(row_data[0])).zfill(4)
            name = row_data[1]

            # Validate and convert the amount column
            if isinstance(row_data[2], (int, float)):
                amount = int(row_data[2])
            elif isinstance(row_data[2], str) and row_data[2] != '':
                amount = int(row_data[2].replace("'", ""))
            else:
                amount = None

            # Validate and convert the amount reminder column
            if isinstance(row_data[3], (int, float)):
                amount_reminder = int(row_data[3])
            elif isinstance(row_data[3], str) and row_data[3] != '':
                amount_reminder = int(row_data[3].replace("'", ""))
            else:
                amount_reminder = None

            weight = float(str(row_data[9]).replace(',', '.'))

            # Append the row data to the sales data list
            sales_data.append([code, name, amount, amount_reminder, weight])

        except (ValueError, IndexError) as e:
            # Handle any errors during data extraction
            print(f"Error extracting data from row {row + 1}: {e}")

    return sales_data


def add_category_column(df):
    """
    Categorize each product into its own category

    Args:
        df (Object): Dataframe with all the sales data (raw data)

    Returns:
        df: dataframe with categories included
    """

    category_mapping = load_category_mapping()

    categories = []
    for code in df['Code']:
        category = None
        for k, v in category_mapping.items():
            if code in v:
                category = k
                break
        categories.append(category)
    df['Category'] = categories

    df.loc[df['Category'].isnull(), 'Category'] = 'Unmatched'
    # Assign 'Unmatched' category to products with no code match

    return df


def identify_duplicates(df):
    """
    Identifies duplicate values in the dataframe

    Args:
        df (Object): dataframe.

    Returns:
        df: dataframe with categories included and duplicates removed 
    """
    duplicate_codes = set(
        [code for code in all_codes if all_codes.count(code) > 1])
    duplicates_df = pd.DataFrame(columns=[
                                 'Code', 'Product', 'Unit Count', 'Reminder', 'Amount Sold (kg)', 'Amount Sold'])
    for index, row in df.iterrows():
        if row['Code'] in duplicate_codes:
            amount = row['Count'] * row['Amount Sold (kg)']
            duplicates_df = duplicates_df.append({'Code': row['Code'], 'Product': row['Product'], 'Unit Count': row['Count'],
                                                 'Reminder': row['Reminder'], 'Amount Sold (kg)': row['Amount Sold (kg)'], 'Amount Sold': amount}, ignore_index=True)
    return duplicates_df


def process_excel_file(file_path):
    """
    Takes excel files in directory and processes them

    Args:
        file_path (Object): path to the current file.

    """

    global all_codes

    category_mapping = load_category_mapping()

    # Open the Excel file
    workbook = xlrd.open_workbook(file_path)
    sheet = workbook.sheet_by_index(0)

    # Extract the data from the sheet
    sales_data = extract_sales_data(sheet)

    # Create a DataFrame from the sales data
    df = pd.DataFrame(sales_data, columns=[
                      'Code', 'Product', 'Count', 'Reminder', 'Amount Sold (kg)'])

    # Convert the Code column to string
    df['Code'] = df['Code'].astype(str)

    # Add a new column for the category
    df = add_category_column(df)

    # Check for unmatched products
    unmatched_products = df[df['Category'] == 'Unmatched'][[
        'Code', 'Product', 'Amount Sold (kg)']]

    df = df[df['Category'] != 'Unmatched']

    # Check for duplicate codes
    all_codes = [code for sublist in category_mapping.values()
                 for code in sublist]
    duplicates_df = identify_duplicates(df)

    # Drop duplicates from the original DataFrame
    df.drop_duplicates(subset='Code', inplace=True)

    # Group the sales data by category and calculate the total sales
    category_sales = df.groupby(
        'Category')['Amount Sold (kg)'].sum().reset_index()

    # Divide the sales by 1000
    category_sales['Amount Sold (kg)'] = category_sales['Amount Sold (kg)'] / 1000

    unit_count = df.groupby('Category')['Count'].sum().reset_index()
    reminder = df.groupby('Category')['Reminder'].sum().reset_index()

    # Count sums the count

    napkin_25 = unit_count.loc[unit_count['Category']
                               == 'Pecete 25', 'Count'].values
    if napkin_25.size > 0:
        napkin_25 = napkin_25[0]
    else:
        napkin_25 = 0

    napkin_30 = unit_count.loc[unit_count['Category']
                               == 'Pecete 30', 'Count'].values
    if napkin_30.size > 0:
        napkin_30 = napkin_30[0]
    else:
        napkin_30 = 0

    toilet_paper = unit_count.loc[unit_count['Category']
                                  == 'Temizlik Kagidlari', 'Count'].values
    if toilet_paper.size > 0:
        toilet_paper = toilet_paper[0]
    else:
        toilet_paper = 0

    aura = unit_count.loc[unit_count['Category'] == 'AURA', 'Count'].values
    if aura.size > 0:
        aura = aura[0]
    else:
        aura = 0

    wet_wipes = unit_count.loc[unit_count['Category']
                               == 'Islak ve Cep Mendil', 'Count'].values
    if wet_wipes.size > 0:
        wet_wipes = wet_wipes[0]
    else:
        wet_wipes = 0

    stretch = unit_count.loc[unit_count['Category']
                             == 'Strech ve Shrink', 'Count'].values
    if stretch.size > 0:
        stretch = stretch[0]

        category_sales.loc[category_sales['Category'] ==
                           'Strech ve Shrink', 'Amount Sold (kg)'] = stretch

    else:
        stretch = 0

    napkin_25_reminder = reminder.loc[reminder['Category']
                                      == 'Pecete 25', 'Reminder'].values[0] / 8
    napkin_30_reminder = reminder.loc[reminder['Category']
                                      == 'Pecete 30', 'Reminder'].values[0] / 24
    toilet_paper_reminder = reminder.loc[reminder['Category']
                                         == 'Temizlik Kagidlari', 'Reminder'].values[0] / 40
    aura_reminder = reminder.loc[reminder['Category']
                                 == 'AURA', 'Reminder'].values[0] / 12
    wet_wipes_reminder = reminder.loc[reminder['Category']
                                      == 'Islak ve Cep Mendil', 'Reminder'].values[0] / 30

    category_sales.loc[category_sales['Category'] == 'Pecete 25',
                       'Amount Sold (kg)'] = napkin_25 + napkin_25_reminder
    category_sales.loc[category_sales['Category'] == 'Pecete 30',
                       'Amount Sold (kg)'] = napkin_30 + napkin_30_reminder
    category_sales.loc[category_sales['Category'] == 'Temizlik Kagidlari',
                       'Amount Sold (kg)'] = toilet_paper + toilet_paper_reminder
    category_sales.loc[category_sales['Category'] ==
                       'AURA', 'Amount Sold (kg)'] = aura + aura_reminder
    category_sales.loc[category_sales['Category'] == 'Islak ve Cep Mendil',
                       'Amount Sold (kg)'] = wet_wipes + wet_wipes_reminder

    # print(category_sales)
    return category_sales, duplicates_df, unmatched_products


def save_results_to_excel(results, file_path):
    category_sales, duplicates_df, unmatched_products = results

    # Create an Excel writer
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')

    # Writing products to suitable sheets
    category_sales.to_excel(writer, sheet_name='Main', index=False)
    duplicates_df.to_excel(writer, sheet_name='Duplicates', index=False)
    unmatched_products.to_excel(
        writer, sheet_name='Unmatched Products', index=False)

    writer.close()

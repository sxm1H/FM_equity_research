import pandas as pd
def create_dcf():
    # Read the excel file
    df = pd.read_excel('DCF_test_lev.xlsx', sheet_name="Sheet1", usecols='A:L', skiprows=0, nrows=4)

    # We can check if Python and Excel achieve the same NPV value

    excel_npv = df.iloc[-1,1] # get the NPV value from the last row and second column

    python_npv = sum(df.iloc[0, 1:] * df.iloc[1, 1:]) # calculate the NPV using Python

    print(f'Excel NPV: {excel_npv:,.2f}')
    print(f'Python NPV: {python_npv:,.2f}')


    # Read the Excel file into a DataFrame
    df = pd.read_excel('DCF_test_lev.xlsx', sheet_name="Sheet1")

    # Display the DataFrame as a table
    print("Data Table:")
    return df

if __name__ == "__main__":
    print(create_dcf())
import streamlit as st
import pandas as pd
import os
import numpy as np
import re

# Ensure the 'temp' directory exists
if not os.path.exists("temp"):
    os.makedirs("temp")

# Initialize the file list and master file variable
file_list = []  # Will store text files
df_masterfile = None  # Will hold the master Excel file data

# Define your file processing function
def process_files(file_list, df_masterfile):
    st.write("Processing the files...")

    # Regular expression to match the codes (e.g., SC617, SF607)
    code_pattern = re.compile(r"\b([A-Z]{2,}[0-9]+)\b")

    for file in file_list:
        try:
            # Read the text file
            df = pd.read_csv(file, header=None)

            if df.shape[1] < 6:
                print(f"File {file} does not have enough columns.")
                continue

            # Add an auxiliary column for original index
            df['original_index'] = df.index

            # Process column 6 (index 5)
            column6 = df[5].astype(str)
            processed_lines = column6[column6.str.match(code_pattern)]
            unprocessed_lines = column6[~column6.str.match(code_pattern)]

            # Separate DataFrames
            df2 = df[df[5].isin(processed_lines)].drop([0, 2, 4, 6, 7], axis=1)
            df1 = df[df[5].isin(unprocessed_lines)].drop([0, 2, 4, 6, 7], axis=1)

            df2[5] = df2[5].astype(str).str.slice(6, 12)
            df2.columns = ['DATE', 'AMOUNT', 'CODE', 'original_index']
            df1.columns = ['DATE', 'AMOUNT', 'CODE', 'original_index']

            # Merge and process columns
            df2 = pd.merge(df2, df_masterfile[['CODE1', 'DESCRIPTION']], left_on='CODE', right_on='CODE1',
                           how='left')
            df2['DESCRIPTION_CODE'] = df2['DESCRIPTION'].fillna('') + ' ' + df2['CODE'].fillna('')
            df1['DESCRIPTION_CODE'] = df1['CODE'].fillna('')

            # Clean columns
            df2.drop(columns=['CODE', 'DESCRIPTION'], inplace=True)
            df1.drop(columns=['CODE'], inplace=True)
            df1['CODE1'] = None

            def format_date(date):
                try:
                    # Attempt to parse the date
                    return pd.to_datetime(date, format='%Y%m%d').strftime('%d/%m/%Y')
                except Exception:
                    # If parsing fails, return the original value
                    return date

            # Format dates
            df2['DATE'] = pd.to_datetime(df2['DATE'], format='%Y%m%d', errors='coerce').dt.strftime(
                '%d/%m/%Y').fillna(df2['DATE'])
            df1['DATE'] = df1['DATE'].apply(format_date)

            # Process amounts
            for df in [df1, df2]:
                df['DEBIT'] = np.where(df['AMOUNT'] > 0, df['AMOUNT'], 0)
                df['CREDIT'] = np.where(df['AMOUNT'] < 0, -df['AMOUNT'], 0)
                df.drop('AMOUNT', axis=1, inplace=True)

            # Final ordering
            final_order = ['DATE', 'DESCRIPTION_CODE', 'CODE1', 'DEBIT', 'CREDIT', 'original_index']
            df1 = df1[final_order]
            df2 = df2[final_order]

            # Concatenate and save
            df_combined = pd.concat([df1, df2]).sort_values(by='original_index').reset_index(drop=True)

            # Save the file
            try:
                output_path = os.path.join(os.path.expanduser("~"), "Downloads", "final_output.xlsx")
                df_combined.to_excel(output_path, index=False)
                st.write("File saved to:", output_path)
                os.startfile(output_path)
            except Exception as e:
                st.error(f"Failed to save the file: {e}")

        except Exception as e:
            print(f"Error processing file {file}: {e}")

    st.write("Files have been processed successfully.")


# Streamlit UI code
def main():
    st.title("File Upload App")

    # Upload Text File button
    uploaded_text_file = st.file_uploader("Upload Text File", type=["txt"])
    if uploaded_text_file is not None:
        # Save the text file in file_list
        file_path = os.path.join("temp", uploaded_text_file.name)  # Save temporarily
        with open(file_path, "wb") as f:
            f.write(uploaded_text_file.getbuffer())
        file_list.append(file_path)
        st.write(f"Text file {uploaded_text_file.name} uploaded and added to the list.")

    # Upload Master File button
    uploaded_master_file = st.file_uploader("Upload Master File (Excel)", type=["xlsx", "xls"])
    if uploaded_master_file is not None:
        # Save and load the master file into df_masterfile
        file_path = os.path.join("temp", uploaded_master_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_master_file.getbuffer())
        global df_masterfile
        try:
            df_masterfile = pd.read_excel(file_path,)
            df_masterfile.columns = ['CODE1','DESCRIPTION']
            st.write(f"Master file {uploaded_master_file.name} loaded successfully.")
        except Exception as e:
            st.error(f"Failed to load the master file: {e}")

    # Display file list
    if file_list:
        st.write("Text files uploaded so far:")
        for f in file_list:
            st.write(f)

    # 'Go' button to process files
    if st.button("Go"):
        if df_masterfile is not None and file_list:
            process_files(file_list, df_masterfile)
        else:
            st.error("Please upload both the text files and the master file before processing.")

if __name__ == "__main__":
    main()

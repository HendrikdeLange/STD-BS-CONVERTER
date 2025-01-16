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

# Define your file processing function for Standard Bank

def process_standard_bank_files(file_list, df_masterfile):
    st.write("Processing Standard Bank files...")

    # Regular expression to match the codes (e.g., SC617, SF607)
    code_pattern = re.compile(r"\b([A-Z]{2,}[0-9]+)\b")

    for file in file_list:
        try:
            # Read the text file
            df = pd.read_csv(file, header=None)

            if df.shape[1] < 6:
                st.error(f"File {file} does not have enough columns.")
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
            final_order = ['DATE', 'DESCRIPTION_CODE', 'CODE1', 'CREDIT', 'DEBIT', 'original_index']
            df1 = df1[final_order]
            df2 = df2[final_order]

            # Concatenate and save
            df_combined = pd.concat([df1, df2]).sort_values(by='original_index').reset_index(drop=True)
            df_combined.drop('original_index', axis=1, inplace=True)
            try:
                output_path = os.path.join("temp", "final_output_standard.xlsx")
                df_combined.to_excel(output_path, index=False)

                with open(output_path, "rb") as file:
                    st.download_button(
                        label="Download Standard Bank Processed File",
                        data=file,
                        file_name="final_output_standard.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            except Exception as e:
                st.error(f"Failed to save the file: {e}")

        except Exception as e:
            st.error(f"Error processing file {file}: {e}")

    st.write("Standard Bank files have been processed successfully.")

# Define your file processing function for ABSA Bank
def process_absa_bank_files(file_list, df_masterfile):
    st.write("Processing ABSA Bank files...")

    for file in file_list:
        try:
            df_absa = pd.read_csv(file, header=None)

            # Expected column indices
            expected_columns = [2, 4, 5, 6]

            # Ensure the DataFrame has enough columns
            if df_absa.shape[1] < max(expected_columns) + 1:
                raise ValueError(f"File does not have enough columns. Expected at least {max(expected_columns) + 1} columns.")

            # Select only the relevant columns
            df_absa = df_absa.iloc[:, expected_columns]

            # Rename columns
            df_absa.columns = ['DATE', 'DESCRIPTION', 'CODE', 'AMOUNT']
            df_absa['original_index'] = df_absa.index

            # Regex pattern to match relevant codes
            pattern = r'(\b[A-Z]{2}\d{4}\b)'  # Matches CC9054

            # Filter rows based on the regex pattern
            df3 = df_absa[df_absa['DESCRIPTION'].str.contains(pattern, regex=True)].reset_index(drop=True)
            df3['CODE'] = df3['DESCRIPTION'].str.extract(pattern)
            df4 = df_absa[~df_absa['DESCRIPTION'].str.contains(pattern, regex=True)].reset_index(drop=True)

            # Fix df4
            final_order = ['DATE', 'DESCRIPTION', 'CODE', 'AMOUNT', 'original_index']
            df4.drop('CODE', axis='columns', inplace=True)
            df4['CODE'] = ''
            df4 = df4[final_order]

            # ADD back together
            df_absa = pd.concat([df3, df4]).sort_values(by='original_index').reset_index(drop=True)

            # DEBIT and CREDIT
            df_absa['CREDIT'] = np.where(df_absa['AMOUNT'] < 0, -df_absa['AMOUNT'], 0)
            df_absa['DEBIT'] = np.where(df_absa['AMOUNT'] > 0, df_absa['AMOUNT'], 0)
            df_absa.drop('AMOUNT', axis='columns', inplace=True)
            df_absa.drop('original_index', axis='columns', inplace=True)

            # FIX DATE
            df_absa['DATE'] = df_absa['DATE'].astype(str)  # Convert the column to string
            df_absa['DATE'] = pd.to_datetime(df_absa['DATE'], format='%y%m%d', errors='coerce').dt.strftime('%d/%m/%Y').fillna(df_absa['DATE'])

            try:
                output_path = os.path.join("temp", "final_output_ABSA.xlsx")
                df_absa.to_excel(output_path, index=False)

                with open(output_path, "rb") as file:
                    st.download_button(
                        label="Download ABSA Bank Processed File",
                        data=file,
                        file_name="final_output_standard.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            except Exception as e:
                st.error(f"Failed to save the file: {e}")

        except Exception as e:
            st.error(f"Error processing file {file}: {e}")

    st.write("ABSA Bank files have been processed successfully.")

# Streamlit UI code
def main():
    std_bank = 'STANDARD BANK'
    abs_bank = 'ABSA'
    st.markdown(f"<h2 style='color: blue; font-weight: bold;'>{"BANK STATEMENT CONVERTER"}</h2>", unsafe_allow_html=True)

    # Select Bank Type
    bank_type = st.radio("Select Bank Type", (std_bank,abs_bank))

    # Upload Text File button
    uploaded_text_file = st.file_uploader("Upload Text File", type=["txt", "csv", "xlsx"])
    if uploaded_text_file is not None:
        # Save the text file in file_list
        file_path = os.path.join("temp", uploaded_text_file.name)  # Save temporarily
        with open(file_path, "wb") as f:
            f.write(uploaded_text_file.getbuffer())
        file_list.append(file_path)
        st.write(f"Text file {uploaded_text_file.name} uploaded and added to the list.")

    # Upload Master File button (only if Standard Bank is selected)
    if bank_type == std_bank:
        uploaded_master_file = st.file_uploader("Upload Master File (Excel)", type=["xlsx", "xls"])
        if uploaded_master_file is not None:
            # Save and load the master file into df_masterfile
            file_path = os.path.join("temp", uploaded_master_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_master_file.getbuffer())
            global df_masterfile
            try:
                df_masterfile = pd.read_excel(file_path)
                df_masterfile.columns = ['CODE1', 'DESCRIPTION']
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
        if bank_type == std_bank:
            if df_masterfile is None:
                st.error("Please upload the master file for Standard Bank.")
            elif df_masterfile is not None and file_list:
                process_standard_bank_files(file_list, df_masterfile)
            else:
                st.error("Please upload the text files before processing.")
        elif bank_type == abs_bank:
            if file_list:
                process_absa_bank_files(file_list, df_masterfile)  # No need to check master file for ABSA
            else:
                st.error("Please upload the text files before processing.")

if __name__ == "__main__":
    main()

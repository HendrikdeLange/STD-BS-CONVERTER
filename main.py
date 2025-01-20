#import packages
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
    for file in file_list:
        try:
            # Read the text file with all 8 columns
            df = pd.read_csv(file, header=None)

            # Drop unnecessary columns (0, 2, 4, 6, 7)
            df.drop(columns=[0, 2, 4, 6, 7], inplace=True)

            # Rename remaining columns to 'DATE', 'AMOUNT', 'DESCRIPTION'
            df.columns = ['DATE', 'AMOUNT', 'DESCRIPTION']
            df['DESCRIPTION'] = df['DESCRIPTION'].str.strip()  # Remove leading/trailing spaces

            print(f"Data after cleaning and renaming:")
            print(df.head())  # Check the cleaned data

            # Add an auxiliary column for the original index
            df['original_index'] = df.index

            #remove faulty first 7 chars
            df['First_Seven_Chars'] = df['DESCRIPTION'].str[:6]

            # Remove the first 6 characters from the original column
            df['DESCRIPTION'] = df['DESCRIPTION'].str[6:]

            def get_matching_code(line):
                line = str(line).strip()  # Ensure it's a string and remove any surrounding spaces

                # Pattern 6: 2 numbers, 3 letters, 4 numbers (start of line)
                match6 = re.search(r'^\d{2}[A-Z]{3}\d{4}\b', line)
                if match6:
                    code = match6.group(0)
                    if code + ':' in line:  # Check if code is followed by ':'
                        return None, None
                    return code, 'pattern6'

                # Pattern 2: 2 numbers, 4 letters, 3 numbers (start of line)
                match2 = re.search(r'^\d{2}[A-Z]{4}\d{3}\b', line)
                if match2:
                    code = match2.group(0)
                    if code + ':' in line:  # Check if code is followed by ':'
                        return None, None
                    return code, 'pattern2'

                # Pattern 1: 2 numbers, 3 letters, 3 numbers (start of line)
                match1 = re.search(r'^\d{2}[A-Z]{3}\d{3}\b', line)
                if match1:
                    code = match1.group(0)
                    if code + ':' in line:  # Check if code is followed by ':'
                        return None, None
                    return code, 'pattern1'

                # Pattern 7: 3 letters, 4 numbers (start of line)
                match7 = re.search(r'^[A-Z]{3}\d{4}\b', line)
                if match7:
                    code = match7.group(0)
                    if code + ':' in line:  # Check if code is followed by ':'
                        return None, None
                    return code, 'pattern7'

                # Pattern 8: 3 letters, 3 numbers (start of line)
                match8 = re.search(r'^[A-Z]{3}\d{3}\b', line)
                if match8:
                    code = match8.group(0)
                    if code + ':' in line:  # Check if code is followed by ':'
                        return None, None
                    return code, 'pattern8'

                # Pattern 3: 1 number, 2 letters, 3 numbers (start of line)
                match3 = re.search(r'^\d[A-Z]{2}\d{3}\b', line)
                if match3:
                    code = match3.group(0)
                    if code + ':' in line:  # Check if code is followed by ':'
                        return None, None
                    return code, 'pattern3'

                # Pattern 4: 1 number, 3 letters, 3 numbers (start of line)
                match4 = re.search(r'^\d[A-Z]{3}\d{3}\b', line)
                if match4:
                    code = match4.group(0)
                    if code + ':' in line:  # Check if code is followed by ':'
                        return None, None
                    return code, 'pattern4'

                # Pattern 5: 2 letters, 4 numbers (start of line)
                match5 = re.search(r'^[A-Z]{2}\d{4}\b', line)
                if match5:
                    code = match5.group(0)
                    if code + ':' in line:  # Check if code is followed by ':'
                        return None, None
                    return code, 'pattern5'

                # Pattern 9: 1 number, 4 letters, 2 numbers (start of line)
                match9 = re.search(r'^\d[A-Z]{4}\d{2}\b', line)
                if match9:
                    code = match9.group(0)
                    if code + ':' in line:  # Check if code is followed by ':'
                        return None, None
                    return code, 'pattern9'

                # Pattern 10: 1 number, 4 letters (start of line)
                match10 = re.search(r'^\d[A-Z]{4}\b', line)
                if match10:
                    code = match10.group(0)
                    if code + ':' in line:  # Check if code is followed by ':'
                        return None, None
                    return code, 'pattern10'

                # Pattern 11: 4 letters, 2 numbers (start of line)
                match11 = re.search(r'^[A-Z]{4}\d{2}\b', line)
                if match11:
                    code = match11.group(0)
                    if code + ':' in line:  # Check if code is followed by ':'
                        return None, None
                    return code, 'pattern11'

                # Pattern 12: 3 letters, 3 numbers (start of line)
                match12 = re.search(r'^[A-Z]{3}\d{3}\b', line)
                if match12:
                    code = match12.group(0)
                    if code + ':' in line:  # Check if code is followed by ':'
                        return None, None
                    return code, 'pattern12'

                return None, None

            # Apply regex and extract matching codes
            df['CODE'], df['PATTERN'] = zip(*df['DESCRIPTION'].apply(get_matching_code))

            #ADD back extracted letters
            df['DESCRIPTION'] = df['First_Seven_Chars'] + df['DESCRIPTION']

            # Split rows based on whether a code was matched
            df_with_codes = df[df['CODE'].notnull()].copy()
            df_without_codes = df[df['CODE'].isnull()].copy()

            # Process columns for df_with_codes
            df_with_codes = pd.merge(
                df_with_codes,
                df_masterfile[['CODE1', 'DESCRIPTION']],
                left_on='CODE',
                right_on='CODE1',
                how='left'
            )

            # Access the correct 'DESCRIPTION_x' column from df_with_codes
            df_with_codes['DESCRIPTION_CODE'] = df_with_codes['DESCRIPTION_y'].fillna('') + ' ' + df_with_codes[
                'CODE'].fillna('')
            df_with_codes.drop(columns=['DESCRIPTION_x', 'DESCRIPTION_y'], inplace=True)

            # Handle rows without codes
            df_without_codes['DESCRIPTION_CODE'] = df_without_codes['DESCRIPTION'].fillna('')
            df_without_codes['CODE1'] = None

            # Ensure numeric amount
            df_with_codes['AMOUNT'] = pd.to_numeric(df_with_codes['AMOUNT'], errors='coerce').fillna(0)
            df_without_codes['AMOUNT'] = pd.to_numeric(df_without_codes['AMOUNT'], errors='coerce').fillna(0)

            # Date formatting function
            def format_date(date):
                try:
                    return pd.to_datetime(date, format='%Y%m%d').strftime('%d/%m/%Y')
                except Exception:
                    return date

            df_with_codes['DATE'] = df_with_codes['DATE'].apply(format_date)
            df_without_codes['DATE'] = df_without_codes['DATE'].apply(format_date)

            # Process amounts
            for df_part in [df_with_codes, df_without_codes]:
                df_part['CREDIT'] = np.where(df_part['AMOUNT'] > 0, df_part['AMOUNT'], 0)
                df_part['DEBIT'] = np.where(df_part['AMOUNT'] < 0, -df_part['AMOUNT'], 0)
                df_part.drop('AMOUNT', axis=1, inplace=True)

            # Final ordering
            final_order = ['DATE', 'DESCRIPTION_CODE', 'CODE1', 'DEBIT', 'CREDIT', 'original_index']
            df_with_codes = df_with_codes[final_order]
            df_without_codes = df_without_codes[final_order]

            # Concatenate and return
            df_combined = pd.concat([df_without_codes, df_with_codes]).sort_values(by='original_index').reset_index(
                drop=True)
            df_combined.drop('original_index', axis=1, inplace=True)

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

    st.write("Standard Bank files have been processed successfully.")
    file_list.clear()
# Define your file processing function for ABSA Bank
def process_absa_bank_files(file_list, df_masterfile):
    for file in file_list:
        try:
            df_absa = pd.read_csv(file, header=None)

            # Expected column indices
            expected_columns = [2, 4, 5, 6]

            # Ensure the DataFrame has enough columns
            if df_absa.shape[1] < max(expected_columns) + 1:
                raise ValueError(
                    f"File does not have enough columns. Expected at least {max(expected_columns) + 1} columns.")

            # Select only the relevant columns
            df_absa = df_absa.iloc[:, expected_columns]

            # Rename columns
            df_absa.columns = ['DATE', 'DESCRIPTION', 'CODE', 'AMOUNT']
            df_absa['original_index'] = df_absa.index

            #find codes
            def get_matching_code(line):
                line = str(line).strip()  # Ensure it's a string and remove any surrounding spaces

                # Pattern 6: 2 numbers, 3 letters, 4 numbers (anywhere in line, but not part of another word)
                match6 = re.search(r'(?<!\w)\d{2}[A-Z]{3}\d{4}(?!\w)', line)
                if match6:
                    code = match6.group(0)
                    return code

                # Pattern 2: 2 numbers, 4 letters, 3 numbers (anywhere in line, but not part of another word)
                match2 = re.search(r'(?<!\w)\d{2}[A-Z]{4}\d{3}(?!\w)', line)
                if match2:
                    code = match2.group(0)
                    return code

                # Pattern 1: 2 numbers, 3 letters, 3 numbers (anywhere in line, but not part of another word)
                match1 = re.search(r'(?<!\w)\d{2}[A-Z]{3}\d{3}(?!\w)', line)
                if match1:
                    code = match1.group(0)
                    return code

                # Pattern 7: 3 letters, 4 numbers (anywhere in line, but not part of another word)
                match7 = re.search(r'(?<!\w)[A-Z]{3}\d{4}(?!\w)', line)
                if match7:
                    code = match7.group(0)
                    return code

                # Pattern 8: 3 letters, 3 numbers (anywhere in line, but not part of another word)
                match8 = re.search(r'(?<!\w)[A-Z]{3}\d{3}(?!\w)', line)
                if match8:
                    code = match8.group(0)
                    return code

                # Pattern 3: 1 number, 2 letters, 3 numbers (anywhere in line, but not part of another word)
                match3 = re.search(r'(?<!\w)\d[A-Z]{2}\d{3}(?!\w)', line)
                if match3:
                    code = match3.group(0)
                    return code

                # Pattern 4: 1 number, 3 letters, 3 numbers (anywhere in line, but not part of another word)
                match4 = re.search(r'(?<!\w)\d[A-Z]{3}\d{3}(?!\w)', line)
                if match4:
                    code = match4.group(0)
                    return code

                # Pattern 5: 2 letters, 4 numbers (anywhere in line, but not part of another word)
                match5 = re.search(r'(?<!\w)[A-Z]{2}\d{4}(?!\w)', line)
                if match5:
                    code = match5.group(0)
                    return code

                # Pattern 9: 1 number, 4 letters, 2 numbers (anywhere in line, but not part of another word)
                match9 = re.search(r'(?<!\w)\d[A-Z]{4}\d{2}(?!\w)', line)
                if match9:
                    code = match9.group(0)
                    return code

                # Pattern 10: 1 number, 4 letters (anywhere in line, but not part of another word)
                match10 = re.search(r'(?<!\w)\d[A-Z]{4}(?!\w)', line)
                if match10:
                    code = match10.group(0)
                    return code

                # Pattern 11: 4 letters, 2 numbers (anywhere in line, but not part of another word)
                match11 = re.search(r'(?<!\w)[A-Z]{4}\d{2}(?!\w)', line)
                if match11:
                    code = match11.group(0)
                    return code

                # Pattern 12: 3 letters, 3 numbers (anywhere in line, but not part of another word)
                match12 = re.search(r'(?<!\w)[A-Z]{3}\d{3}(?!\w)', line)
                if match12:
                    code = match12.group(0)
                    return code

                return None

            # Apply regex to extract codes and add them to a new 'CODE' column
            df_absa['CODE'] = df_absa['DESCRIPTION'].apply(get_matching_code)

            # Fix df_absa
            final_order = ['DATE', 'DESCRIPTION', 'CODE', 'AMOUNT', 'original_index']
            df_absa = df_absa[final_order]

            # DEBIT and CREDIT
            df_absa['DEBIT'] = np.where(df_absa['AMOUNT'] < 0, -df_absa['AMOUNT'], 0)
            df_absa['CREDIT'] = np.where(df_absa['AMOUNT'] > 0, df_absa['AMOUNT'], 0)
            df_absa.drop('AMOUNT', axis='columns', inplace=True)
            df_absa.drop('original_index', axis='columns', inplace=True)

            # FIX DATE
            df_absa['DATE'] = df_absa['DATE'].astype(str)  # Convert the column to string
            df_absa['DATE'] = pd.to_datetime(df_absa['DATE'], format='%y%m%d', errors='coerce').dt.strftime(
                '%d/%m/%Y').fillna(df_absa['DATE'])

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
    file_list.clear()


def process_capitec_bank_files(file_list):
    for file in file_list:
        try:
            # Read CSV file and skip the first 3 lines
            df_capitec = pd.read_csv(file, header=None, engine='python', skiprows=3)
        except Exception as e:
            st.error(f"Error reading file {file}: {e}")
            continue  # Skip the current file and continue with the rest

        # Validate columns
        expected_columns = [1, 2, 3, 4, 5]
        if df_capitec.shape[1] < max(expected_columns) + 1:
            st.error(f"File does not have enough columns. Expected at least {max(expected_columns) + 1} columns.")
            continue  # Skip this file and continue with the next

        # Extract Fees, Date, and Description
        fees = df_capitec.iloc[-1, 5]
        date = df_capitec.iloc[-2, 1]
        description = df_capitec.iloc[-2, 2]

        # Select relevant columns and clean up
        df_capitec = df_capitec.iloc[:, [1, 3, 4, 5]]
        df_capitec.reset_index(drop=True, inplace=True)
        df_capitec.columns = ['DATE', 'REFERENCE', 'AMOUNT', 'FEES']
        df_capitec.drop(columns='FEES', inplace=True)

        # Remove the last two rows (summary rows)
        df_capitec = df_capitec.iloc[:-2]

        # Convert 'AMOUNT' to numeric
        df_capitec['AMOUNT'] = pd.to_numeric(df_capitec['AMOUNT'], errors='coerce').fillna(0)

        # Create 'DEBIT' and 'CREDIT' columns
        df_capitec['DEBIT'] = np.where(df_capitec['AMOUNT'] < 0, -df_capitec['AMOUNT'], 0)
        df_capitec['CREDIT'] = np.where(df_capitec['AMOUNT'] > 0, df_capitec['AMOUNT'], 0)
        df_capitec.drop(columns='AMOUNT', inplace=True)

        # Extract site information from 'REFERENCE'
        # Extract the 'D' followed by exactly three digits from 'REFERENCE'
        pattern = r'(D\d{3})'
        df_capitec['SITE'] = df_capitec['REFERENCE'].str.extract(pattern, expand=False).fillna("")

        # Extract and process activity codes
        df_capitec['activity_letter'] = df_capitec['REFERENCE'].str[5:6]
        df_capitec['ACTIVITY'] = ""
        df_capitec.loc[df_capitec['activity_letter'] == 'B', 'ACTIVITY'] = "B8200"
        df_capitec.loc[df_capitec['activity_letter'] == 'C', 'ACTIVITY'] = "C1200"
        df_capitec.drop(columns='activity_letter', inplace=True)

        # Append "EFT WAGES" to debit transactions
        df_capitec.loc[df_capitec['DEBIT'] > 0, 'REFERENCE'] = (
                "EFT WAGES " + df_capitec.loc[df_capitec['DEBIT'] > 0, 'REFERENCE']
        )

        # Reorder columns
        final_order = ['DATE', 'REFERENCE', 'SITE', 'ACTIVITY', 'DEBIT', 'CREDIT']
        df_capitec = df_capitec[final_order]

        # Add back last row
        last_row = pd.Series(
            [date, description, '', '', fees, 0],
            index=df_capitec.columns
        )
        df_capitec = pd.concat([df_capitec, last_row.to_frame().T], ignore_index=True)

        # Try saving the final output to Excel
        try:
            output_path = os.path.join("temp", "final_output_CAPITEC.xlsx")
            df_capitec.to_excel(output_path, index=False)

            # Streamlit download button
            with open(output_path, "rb") as file:
                st.download_button(
                    label="Download CAPITEC Bank Processed File",
                    data=file,
                    file_name="final_output_standard.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"Failed to save the file: {e}")

    # Clear the file list after processing all files
    file_list.clear()


# Streamlit UI code
def main():
    st.markdown("""
        <style>
        .stApp {
            background-image: url('https://images.unsplash.com/photo-1490093158370-1a6be674437b?q=80&w=1314&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
        }
        .stApp::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: inherit;
            filter: grayscale(100%);
            z-index: -1;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("""
            <style>
            .heading {
                font-size: 36px;
                font-weight: bold;
                text-align: center;
                color: #00008B;  /* Change to any color you want */
            }
            </style>

            <div class="heading">BANK STATEMENT CONVERTER</div>
        """, unsafe_allow_html=True)
    std_bank = 'STANDARD BANK'
    abs_bank = "ABSA BANK"
    cpt_bank = 'CAPITEC BANK'
    # Select Bank Type
    bank_type = st.radio("", (std_bank, abs_bank, cpt_bank))

    # Upload Text File button
    uploaded_text_file = st.file_uploader("Upload Bank Statement", type=["txt", "csv", "xlsx"])
    if uploaded_text_file is not None:
        # Save the text file in file_list
        file_path = os.path.join("temp", uploaded_text_file.name)  # Save temporarily
        with open(file_path, "wb") as f:
            f.write(uploaded_text_file.getbuffer())
        file_list.append(file_path)

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
            except Exception as e:
                st.error(f"Failed to load the master file: {e}")

    # 'Go' button to process files
    if st.button("Go"):
        if bank_type == std_bank:
            if df_masterfile is None:
                st.error("Please upload the master file for Standard Bank.")
            elif df_masterfile is not None and file_list:
                process_standard_bank_files(file_list, df_masterfile)
            else:
                st.error("Please upload the correct files before processing.")
        elif bank_type == abs_bank:
            if file_list:
                process_absa_bank_files(file_list, df_masterfile)  # No need to check master file for ABSA
            else:
                st.error("Please upload the correct files before processing.")
        elif bank_type == cpt_bank:
            if file_list:
                process_capitec_bank_files(file_list)  # No need to check master file for CAPITEC

if __name__ == "__main__":
    main()
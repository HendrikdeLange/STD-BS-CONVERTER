import pandas as pd
import streamlit as st
import logging

# Set up logging
logging.basicConfig(level=logging.ERROR)

def process_employee_data(avbob_file, new_file, terminate_file):
    try:
        # Read AVBOB data
        df_avbob = pd.read_excel(avbob_file, engine="openpyxl", dtype=str)
        df_avbob.columns = df_avbob.columns.str.strip()
        avbob_columns = df_avbob.columns

        # Read New Employee data
        df_new_employees = pd.read_excel(new_file, engine="openpyxl", dtype=str)
        df_new_employees.columns = df_new_employees.columns.str.strip()
        add_columns = df_new_employees.columns
        if len(add_columns) != 9:
            raise ValueError(f"The new employee data file only has {len(add_columns)} columns, it should have 9.")

        # Read Terminations data
        df_terminations = pd.read_excel(terminate_file, engine="openpyxl", dtype=str)
        terminations_columns = df_terminations.columns
        if len(terminations_columns) != 10:
            raise ValueError(f"The termination data file only has {len(terminations_columns)} columns, it should have 10.")

#======================================================================================================================
# CONSTRUCTION OF NEW AVBOB SCHEDULE
#======================================================================================================================

        # Initialize the new dataframe
        df_new_avbob = pd.DataFrame(columns=avbob_columns)

        # Employee Codes
        og_employees = pd.Series(df_avbob[avbob_columns[0]])
        new_employees = pd.Series(df_new_employees[add_columns[0]])
        combined_employees = pd.concat([og_employees.reset_index(drop=True), new_employees.reset_index(drop=True)], axis=0)  # Reset indices before concatenating

        # Groups
        og_group = pd.Series(df_avbob[avbob_columns[3]])
        new_group = pd.Series(df_new_employees[add_columns[6]])
        combined_group = pd.concat([og_group.reset_index(drop=True), new_group.reset_index(drop=True)], axis=0)

        # ID
        og_id = pd.Series(df_avbob[avbob_columns[9]])
        df_new_employees[add_columns[3]] = df_new_employees[add_columns[3]].fillna(df_new_employees[add_columns[5]])
        new_id = pd.Series(df_new_employees[add_columns[3]].astype(str))
        combined_id = pd.concat([og_id.reset_index(drop=True), new_id.reset_index(drop=True)], axis=0)

    #==================================
    # NEW EMPLOYEE SHEET
    #==================================
        df_new_employees[add_columns[3]] = new_id
        df_new_sheet = df_new_employees.copy()
        df_new_sheet.drop(columns=[add_columns[5], add_columns[6] ], inplace=True)

        # Commencement date
        df_new_employees[add_columns[8]] = df_new_employees[add_columns[8]].astype(str).str[:-2].astype(int)
        og_commence = pd.Series(df_avbob[avbob_columns[4]])
        new_commence = pd.Series(df_new_employees[add_columns[8]])
        combined_commence = pd.concat([og_commence.reset_index(drop=True), new_commence.reset_index(drop=True)], axis=0)

        # Surnames
        og_surnames = pd.Series(df_avbob[avbob_columns[6]])
        new_surnames = pd.Series(df_new_employees[add_columns[1]])
        combined_surnames = pd.concat([og_surnames.reset_index(drop=True), new_surnames.reset_index(drop=True)], axis=0)

        # Initials
        og_initials = pd.Series(df_avbob[avbob_columns[7]])
        new_initials = pd.Series(df_new_employees[add_columns[2]])
        combined_initials = pd.concat([og_initials.reset_index(drop=True), new_initials.reset_index(drop=True)], axis=0)

        # Date of birth
        og_birth = pd.Series(df_avbob[avbob_columns[8]])
        new_birth = pd.Series(df_new_employees[add_columns[4]])
        combined_birth = pd.concat([og_birth.reset_index(drop=True), new_birth.reset_index(drop=True)], axis=0)

        # Gender
        og_gender = pd.Series(df_avbob[avbob_columns[11]])
        new_gender = pd.Series(df_new_employees[add_columns[7]])
        combined_gender = pd.concat([og_gender.reset_index(drop=True), new_gender.reset_index(drop=True)], axis=0)

        # Reconstruct the new avbob datadrame
        df_new_avbob[avbob_columns[0]] = pd.Series(combined_employees.values)
        df_new_avbob[avbob_columns[1]] = df_new_avbob[avbob_columns[1]].fillna("A")
        df_new_avbob[avbob_columns[2]] = df_new_avbob[avbob_columns[2]].fillna(1284)
        df_new_avbob[avbob_columns[3]] = pd.Series(combined_group.values)
        df_new_avbob[avbob_columns[4]] = pd.Series(combined_commence.values)
        df_new_avbob[avbob_columns[5]] = df_new_avbob[avbob_columns[5]].fillna(1)
        df_new_avbob[avbob_columns[6]] = pd.Series(combined_surnames.values)
        df_new_avbob[avbob_columns[7]] = pd.Series(combined_initials.values)
        df_new_avbob[avbob_columns[8]] = pd.Series(combined_birth.values)
        df_new_avbob[avbob_columns[9]] = pd.Series(combined_id.values)
        df_new_avbob[avbob_columns[10]] = df_new_avbob[avbob_columns[10]].fillna("E")
        df_new_avbob[avbob_columns[11]] = pd.Series(combined_gender.values)
        df_new_avbob[avbob_columns[12]] = df_new_avbob[avbob_columns[12]].fillna(2000000)
        df_new_avbob[avbob_columns[13]] = df_new_avbob[avbob_columns[13]].fillna("PO BOX 13596")
        df_new_avbob[avbob_columns[14]] = df_new_avbob[avbob_columns[14]].fillna("NOORDSTAD")
        df_new_avbob[avbob_columns[15]] = df_new_avbob[avbob_columns[15]].fillna("BLOEMFONTEIN")
        df_new_avbob[avbob_columns[16]] = df_new_avbob[avbob_columns[16]].fillna(9302)
        df_new_avbob[avbob_columns[21]] = df_new_avbob[avbob_columns[21]].fillna(514030400)

        # Remove terminations from completed list
        valid_terminations = df_terminations[terminations_columns[0]].dropna().unique()
        df_new_avbob[avbob_columns[0]] = df_new_avbob[avbob_columns[0]].astype(str)
        valid_terminations = valid_terminations.astype(str)
        df_new_avbob[avbob_columns[0]] = df_new_avbob[avbob_columns[0]].str.strip()
        valid_terminations = [code.strip() for code in valid_terminations]
        df_new_avbob = df_new_avbob[~df_new_avbob[avbob_columns[0]].isin(valid_terminations)]

    #==================================
    # TERMINATIONS SHEET
    #==================================
        df_terminations[terminations_columns[3]] = df_terminations[terminations_columns[3]].fillna(df_terminations[terminations_columns[5]])
        new_terminations_id = pd.Series(df_terminations[terminations_columns[3]].astype(str))
        df_terminations[terminations_columns[3]] = new_terminations_id
        term_passport = terminations_columns[5]
        term_group = terminations_columns[6]
        df_terminations.drop(columns = [term_passport, term_group], inplace=True)


        return df_new_avbob, df_new_sheet, df_terminations
    except Exception as e:
            logging.error(f"Error processing employee data: {e}")
            raise
def main():
    st.markdown("""
        <style>
        .heading {
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            color: green;
        }
        </style>

        <div class="heading">AVBOB SCHEDULE</div>
    """, unsafe_allow_html=True)

    st.write("### Please ensure the new employee columns follow this pattern:")
    st.write("`CODE | SURNAME | INITIALS | ID | DOB | PASSPORT | GROUP | GENDER | DATE ENGAGED`")

    st.write("### The terminations columns must follow this pattern:")
    st.write("`CODE | SURNAME | INITIALS | ID | DOB | PASSPORT | GROUP | GENDER | DATE ENGAGED | DATE TERMINATED`")

    # File uploaders
    avbob_file = st.file_uploader("Upload the previous month's schedule", type=["xlsx", "xls"])
    new_file = st.file_uploader("Upload New Employees Data", type=["xlsx", "xls"])
    terminate_file = st.file_uploader("Upload Terminations Data", type=["xlsx", "xls"])

    if st.button("Go"):
        if avbob_file and new_file and terminate_file:
            try:
                df_new_avbob, df_new_sheet, df_terminations = process_employee_data(avbob_file, new_file, terminate_file)

                # Download processed data
                output_file_path = "temp/final_output.xlsx"
                with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:
                    df_new_avbob.to_excel(writer, sheet_name='ACTIVE', index=False)
                    df_new_sheet.to_excel(writer, sheet_name='NEW EMPLOYEES', index=False)
                    df_terminations.to_excel(writer, sheet_name='TERMINATIONS', index=False)

                with open(output_file_path, "rb") as f:
                    st.download_button(
                        label="Download Processed File",
                        data=f,
                        file_name="final_output.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            except ValueError as ve:
                st.error(f"Validation Error: {ve}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                logging.error(f"Unexpected error: {e}")
        else:
            st.error("Please upload all the required files before clicking 'Go'.")
            st.write("Please ensure all uploaded files are in .xlsx format with the newest Excel engine.")

if __name__ == "__main__":
    main()
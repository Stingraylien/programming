import pandas as pd
import os
import shutil  

# 🔹 Set the folder path where all quiz Excel files are stored
folder_path = os.path.join(os.path.expanduser("~"), "Library", "CloudStorage", "OneDrive-InventecCorp", "測驗題目自動檢查")

# 🔹 Set the output folder where the validated files will be saved
output_folder = os.path.join(folder_path, "output")

# 🔹 Set the folder for failed reports
failed_folder = os.path.join(folder_path, "failed")

# Ensure the output folders exist
for folder in [output_folder, failed_folder]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Get all Excel files
quiz_files = [f for f in os.listdir(folder_path) if f.endswith(".xlsx")]

# Required columns to check
required_columns = ["Difficulty", "Option Limit Type(for survey):0-no limit;1-max;2-min",
                    "Option Limit Count(for survey)", "Analyze(for QBank)", "NoRandom(for QBank)"]

# Store results
invalid_questions_list = []
low_weight_list = []
missing_columns_list = []
valid_files = []  # Track valid files separately
error_files = []  # Track files with issues

# Process each quiz file
for file in quiz_files:
    file_path = os.path.join(folder_path, file)
    
    # Load the Excel file
    xls = pd.ExcelFile(file_path)
    
    # Find the first occurrence of "#QTYPE" to remove unnecessary rows
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0], header=None)
    
    # Find row index where "#QTYPE" first appears
    qtype_row_index = df[df.iloc[:, 0] == "#QTYPE"].index.min()
    
    if pd.isna(qtype_row_index):
        print(f"⚠️ Skipping {file}: No '#QTYPE' found.")
        error_files.append(file)
        continue  # Skip this file if #QTYPE is missing

    # Extract only relevant data starting from "#QTYPE"
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0], skiprows=qtype_row_index)

    # Check for missing columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    
    if missing_cols:
        missing_columns_list.append({"File": file, "Missing Columns": ", ".join(missing_cols)})
        error_files.append(file)
        continue  # Skip processing this file since columns are missing

    # Ensure 'Subject' column is filled down so each option is mapped to its question
    df["Subject"] = df["Subject"].ffill()

    # Count occurrences of 'y' for each question
    answer_counts = df.groupby("Subject")["Yes/No/Answer"].apply(lambda x: (x == 'y').sum())

    # Identify questions that do not have exactly one correct answer
    invalid_questions = answer_counts[answer_counts != 1].reset_index()

    # Calculate total weight correctly
    total_weight = df.groupby("Subject")["Weight"].first().sum()

    has_invalid_questions = not invalid_questions.empty
    has_low_weight = total_weight < 100  # Report if weight is below 100

    # If no issues, mark as valid
    if not has_invalid_questions and not has_low_weight:
        valid_files.append(file)  # Track the valid file

    # Now include files with either issue, not just both
    if has_invalid_questions or has_low_weight:
        if has_invalid_questions:
            invalid_questions["File"] = file  # Add filename for reference
            invalid_questions_list.append(invalid_questions)
        if has_low_weight:
            low_weight_list.append({"File": file, "Total Weight": total_weight})
        error_files.append(file)  # Track the file with issues

# Define the full output file path for failed reports
failed_output_file = os.path.join(failed_folder, "Quiz_Validation_Report.xlsx")

# Save report if there are any issues
if invalid_questions_list or low_weight_list or missing_columns_list:
    print("❌ Some quiz files have issues.")
    print("The following files contain errors:")
    for error_file in set(error_files):
        print(f"🔸 {error_file}")  # ✅ Print error file names

    # Create Excel writer to store everything in one file
    with pd.ExcelWriter(failed_output_file, engine="xlsxwriter") as writer:
        
        # Save invalid questions
        if invalid_questions_list:
            final_invalid_questions = pd.concat(invalid_questions_list, ignore_index=True)
            final_invalid_questions.to_excel(writer, index=False, sheet_name="Invalid Questions")

        # Save low-weight files
        if low_weight_list:
            low_weight_df = pd.DataFrame(low_weight_list)
            low_weight_df.to_excel(writer, index=False, sheet_name="Low Weight Files")

        # Save missing columns files
        if missing_columns_list:
            missing_columns_df = pd.DataFrame(missing_columns_list)
            missing_columns_df.to_excel(writer, index=False, sheet_name="Missing Columns")

    print(f"📄 Combined report saved to: {failed_output_file}")

# Now copy valid files to the output folder
if valid_files:
    for file in valid_files:
        source_file = os.path.join(folder_path, file)
        destination_file = os.path.join(output_folder, file)
        shutil.copy2(source_file, destination_file)  # Preserve metadata

    print(f"✅ All valid quiz files have been copied to: {output_folder}")
else:
    print("✅ No valid files found to copy.")



import pandas as pd
import numpy as np
import os

def finalize_property_data(input_csv_path: str, output_csv_path: str):
    """
    Performs the final polishing of the cleaned property data, including imputation,
    feature engineering, and creating new metrics.
    """
    print(f"Loading cleaned data from '{input_csv_path}'...")
    try:
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: The file '{input_csv_path}' was not found. Please check the path.")
        return
        
    # --- Step 0: Drop Corrupted/Useless Rows ---
    # Rows without Price or Area are not useful for analysis or modeling.
    initial_rows = len(df)
    df.dropna(subset=['Price', 'Area_sqft'], inplace=True)
    # Some rows might have an Area_sqft of 0, which also makes them unusable.
    df = df[df['Area_sqft'] > 0]
    print(f"Step 0: Removed {initial_rows - len(df)} rows with missing Price or Area.")


    # --- Step 1: Handle Missing Values (Imputation) ---
    print("Step 1: Imputing remaining missing values...")

    numerical_cols = [
        'Washrooms', 'Floor_Number', 'Total_Floors', 'Open_Sides', 
        'Plot_Length', 'Plot_Breadth', 'Entrance_Width_ft', 'Road_Width_m'
    ]
    categorical_cols = [
        'Property_Age', 'Zoning', 'Facing', 'Overlooking', 
        'Pantry', 'Furnishing_Status', 'Possession_Date'
    ]

    for col in numerical_cols:
        if col in df.columns:
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            
    for col in categorical_cols:
        if col in df.columns:
            df[col].fillna('Not Specified', inplace=True)

    # --- Step 2: Feature Engineering - Property_Age ---
    print("Step 2: Converting 'Property_Age' to a numeric feature 'Age_in_Years'...")
    age_map = {
        'New Construction': 0,
        'Less than 5 years old': 2.5,
        '5 to 10 years old': 7.5,
        '10 to 15 years old': 12.5,
        '15 to 20 years old': 17.5,
        'Above 20 years old': 25,
        'Not Specified': -1 
    }
    df['Age_in_Years'] = df['Property_Age'].map(age_map).fillna(-1)

    # --- Step 3: Cleaning 'Water Availability' Column ---
    print("Step 3: Parsing 'Water Availability' into a clean status column...")
    df['Water_Availability_Status'] = df['Water Availability'].str.extract(r'(\d+\s*Hours?)').fillna('Not Specified')
    df['Water_Availability_Status'] = df['Water_Availability_Status'].str.replace(' ', '').str.strip()
    
    # --- Step 4: Creating New Feature 'Price_per_sqft' ---
    print("Step 4: Creating 'Price_per_sqft' feature...")
    df['Price_per_sqft'] = (df['Price'] / df['Area_sqft']).round(2)

    # --- Step 5: Final Cleanup and Column Reordering ---
    print("Step 5: Finalizing the dataframe...")
    df.drop(columns=['Property_Age', 'Water Availability'], inplace=True, errors='ignore')

    final_cols_order = [
        'Property_Type', 'Transaction_Type', 'Location', 'latitude', 'longitude', 'Price', 
        'Area_sqft', 'Price_per_sqft', 'area_type', 'Construction_Status', 
        'Age_in_Years', 'Possession_Date', 'Furnishing_Status', 'Zoning', 'Facing', 
        'Overlooking', 'Pantry', 'Water_Availability_Status', 'Washrooms', 'Floor_Number', 
        'Total_Floors', 'Covered_Parking', 'Open_Parking', 'Open_Sides', 'Plot_Length', 
        'Plot_Breadth', 'Entrance_Width_ft', 'Road_Width_m'
    ]
    
    existing_final_cols = [col for col in final_cols_order if col in df.columns]
    df_final = df[existing_final_cols]

    # --- Save the Final Data ---
    print(f"Saving analysis-ready data to '{output_csv_path}'...")
    df_final.to_csv(output_csv_path, index=False)

    print("\n--- Final Processing Complete! ---")
    print(f"File saved at: {output_csv_path}")
    print("\n--- Info of the Final DataFrame ---")
    df_final.info()
    print("\n--- Sample of the Final, Analysis-Ready Data ---")
    print(df_final.head().to_markdown(index=False))


if __name__ == "__main__":
    base_dir = r'C:\Users\Asus\OneDrive\Desktop\100 GAJ ASSIGNMENTS\Task-5\Property-Prices'
    INPUT_FILE = os.path.join(base_dir, 'fully_cleaned_property_data.csv')
    OUTPUT_FILE = os.path.join(base_dir, 'final_analysis_ready_data.csv')
    
    # Check if the input file exists before running
    if os.path.exists(INPUT_FILE):
        finalize_property_data(input_csv_path=INPUT_FILE, output_csv_path=OUTPUT_FILE)
    else:
        print(f"ERROR: The input file was not found at the path: {INPUT_FILE}")
        print("Please make sure the file from the first script exists and the path is correct.")
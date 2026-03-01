"""
Migration Script: Split erp.xlsx into separate Excel files
Run this script to migrate from single-file to multi-file storage.
"""

import pandas as pd
import os

# Source file
SOURCE_FILE = "data/erp.xlsx"

# Target files in data folder
TARGET_FILES = {
    "customer_details": "data/customer_details.xlsx",
    "store_details": "data/store_details.xlsx",
    "customer_bills": "data/customer_bills.xlsx",
    "distributor_details": "data/distributor_details.xlsx",
    "distributor_transactions": "data/distributor_transactions.xlsx",
    "credit_debit": "data/credit_debit.xlsx",
}

def migrate():
    print("Starting migration...")
    
    # Check if source file exists
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: Source file '{SOURCE_FILE}' not found!")
        return False
    
    try:
        # Read all sheets from source
        xl = pd.ExcelFile(SOURCE_FILE)
        print(f"Found sheets: {xl.sheet_names}")
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Export each sheet to a separate file
        for sheet_name, target_file in TARGET_FILES.items():
            if sheet_name in xl.sheet_names:
                df = pd.read_excel(SOURCE_FILE, sheet_name=sheet_name)
                
                # Save to separate file
                with pd.ExcelWriter(target_file, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False)
                
                print(f"✓ Created {target_file} with {len(df)} rows")
            else:
                # Create empty file with headers
                print(f"Sheet '{sheet_name}' not found, creating empty file...")
                
                # Determine columns based on sheet type
                if sheet_name == "customer_details":
                    columns = ["customer_id", "customer_name", "phone", "address"]
                elif sheet_name == "store_details":
                    columns = ["medicine", "quantity", "expiry_date", "mfg_date", "batch_number", "mrp", "distributor", "purchase_date"]
                elif sheet_name == "customer_bills":
                    columns = ["bill_no", "customer_id", "customer_name", "date", "total_amount", "paid_amount", "balance"]
                elif sheet_name == "distributor_details":
                    columns = ["distributor_id", "distributor_name", "phone_number", "address"]
                elif sheet_name == "distributor_transactions":
                    columns = ["receipt_no", "bill_no", "distributor_id", "distributor_name", "phone_number", "bill_amount", "paid_amount", "balance", "date"]
                elif sheet_name == "credit_debit":
                    columns = ["customer_id", "customer_name", "payment_type", "amount", "date", "note"]
                else:
                    columns = []
                
                df = pd.DataFrame(columns=columns)
                with pd.ExcelWriter(target_file, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False)
                
                print(f"✓ Created empty {target_file}")
        
        print("\n✓ Migration completed successfully!")
        print("\nYou can now delete the old 'data/erp.xlsx' file if you want.")
        print("The application will use separate files from now on.")
        
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

if __name__ == "__main__":
    migrate()

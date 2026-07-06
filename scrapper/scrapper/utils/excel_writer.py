"""
Enhanced Excel Writer for HPCL B2B Leads
Creates professionally formatted Excel files with proper column ordering
"""

import pandas as pd
import os


def write_excel(signals, path):
    """
    Write signals to Excel with enhanced formatting
    
    Args:
        signals: List of signal dictionaries
        path: Output file path
    """
    
    if not signals:
        print("⚠️ No signals to write")
        return
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    
    # Convert to DataFrame
    df = pd.DataFrame(signals)
    
    # Define column order (prioritize most important fields)
    priority_cols = [
        # Identification
        "Serial_Number",
        "Source",
        "Signal_Type",
        
        # Company Information
        "Company_Name",
        "Organization_Name",
        "Organization_Chain",
        
        # Tender Details
        "Title",
        "Full_Reference",
        "Summary",
        
        # HPCL Product Match
        "HPCL_Products",
        "HPCL_Keyword_Match",
        
        # Dates
        "e_Published_Date",
        "Post_Date",
        "Closing_Date",
        "Opening_Date",
        
        # Contact Information
        "Contact_Email",
        "Contact_Phone",
        
        # Location
        "Location_Clues",
        
        # Additional Info
        "Corrigendum",
        "URL",
        "Captured_At",
        
        # Metadata
        "Source_Governance",
        "Source_Trust",
        "Provenance",
    ]
    
    # Get available columns in order
    available_cols = []
    for col in priority_cols:
        if col in df.columns:
            available_cols.append(col)
    
    # Add any remaining columns not in priority list
    remaining_cols = [col for col in df.columns if col not in available_cols]
    final_cols = available_cols + remaining_cols
    
    # Reorder DataFrame
    df_final = df[final_cols]
    
    # Clean up data
    df_final = df_final.fillna("")
    
    # Truncate very long fields for better Excel display
    if "Full_Reference" in df_final.columns:
        df_final["Full_Reference"] = df_final["Full_Reference"].apply(
            lambda x: str(x)[:500] if len(str(x)) > 500 else x
        )
    
    if "Organization_Chain" in df_final.columns:
        df_final["Organization_Chain"] = df_final["Organization_Chain"].apply(
            lambda x: str(x)[:300] if len(str(x)) > 300 else x
        )
    
    # Write to Excel
    try:
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False, sheet_name='HPCL Leads')
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['HPCL Leads']
            
            # Auto-adjust column widths
            for idx, col in enumerate(df_final.columns, 1):
                # Calculate max length
                max_length = max(
                    df_final[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                
                # Set reasonable limits
                max_length = min(max_length, 50)
                max_length = max(max_length, 10)
                
                # Convert to Excel column letter
                col_letter = worksheet.cell(row=1, column=idx).column_letter
                worksheet.column_dimensions[col_letter].width = max_length
            
            # Freeze top row
            worksheet.freeze_panes = worksheet['A2']
        
        print(f"✅ Excel file created: {path}")
        print(f"   📊 Rows: {len(df_final):,}")
        print(f"   📋 Columns: {len(df_final.columns)}")
        
    except Exception as e:
        print(f"❌ Error writing Excel: {str(e)}")
        # Fallback to CSV
        csv_path = path.replace('.xlsx', '.csv')
        df_final.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"   ℹ️ Saved as CSV instead: {csv_path}")


def write_excel_multiple_sheets(signals_dict, path):
    """
    Write multiple signal groups to separate Excel sheets
    
    Args:
        signals_dict: Dictionary of {sheet_name: signals_list}
        path: Output file path
    """
    
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    
    try:
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            for sheet_name, signals in signals_dict.items():
                if not signals:
                    continue
                
                df = pd.DataFrame(signals)
                df = df.fillna("")
                
                # Limit sheet name length
                sheet_name = sheet_name[:31]  # Excel limit
                
                df.to_excel(writer, index=False, sheet_name=sheet_name)
                
                # Auto-adjust columns
                worksheet = writer.sheets[sheet_name]
                for idx, col in enumerate(df.columns, 1):
                    max_length = min(
                        max(df[col].astype(str).apply(len).max(), len(col)) + 2,
                        50
                    )
                    col_letter = worksheet.cell(row=1, column=idx).column_letter
                    worksheet.column_dimensions[col_letter].width = max_length
                
                worksheet.freeze_panes = worksheet['A2']
        
        print(f"✅ Multi-sheet Excel created: {path}")
        print(f"   📄 Sheets: {len(signals_dict)}")
        
    except Exception as e:
        print(f"❌ Error writing multi-sheet Excel: {str(e)}")


if __name__ == "__main__":
    # Test
    test_signals = [
        {
            "Source": "eProcure-CPPP",
            "Company_Name": "NTPC Limited",
            "Title": "Supply of High Speed Diesel",
            "HPCL_Products": "HSD",
            "Contact_Email": "tender@ntpc.co.in",
            "Contact_Phone": "+91-22-12345678",
            "URL": "https://example.com/tender/123"
        }
    ]
    
    print("🧪 Testing Excel Writer...")
    write_excel(test_signals, "test_output.xlsx")

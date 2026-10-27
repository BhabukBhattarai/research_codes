Input Data and File Paths

In the RUN section of the script, replace the placeholder paths (************) with the paths to your Excel data files and the directory where you want to save the output figures.

if __name__ == "__main__":
    set_style()

    cal_path = r"************.xlsx"  # Path to calibration Excel data
    val_path = r"************.xlsx"  # Path to validation Excel data
    out_dir  = r"*************"      # Directory to save output figures
    os.makedirs(out_dir, exist_ok=True)

Excel Data Requirements

Both Excel files must contain the following columns:

Date - date of observation

Runoff - observed discharge

Simulated Runoff(HBV) - discharge simulated by the HBV model

Simulated Runoff(HECHMS) - discharge simulated by the HEC-HMS model

The calibration and validation data should be provided in separate Excel files. Ensure that the column names match those expected by the script.

Example file paths:

cal_path = r"C:\Users\YourName\Documents\calibration.xlsx" 

val_path = r"C:\Users\YourName\Documents\validation.xlsx" 

out_dir  = r"C:\Users\YourName\Documents\Taylor_Diagrams"    

Replace these example paths with the actual locations of your files. The script creates the output directory if it does not already exist.

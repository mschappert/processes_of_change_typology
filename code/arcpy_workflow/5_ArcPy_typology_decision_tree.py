###=======================
##  Before running the script:
# Make sure Python extension is installed in VS Code.
# Make sure ArcGIS Pro is installed on your machine.
## Ctrl + Shift + P to open the command palette in VS Code.
# type "Python: Select Interpreter" → Enter.
# Click "Enter interpreter path" → "Find..." → 
# navigate to the C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
# 
### =======================
### Import Packages ###
import os
import arcpy
import arcpy.sa
import multiprocessing
import re
import sys
import time


################ make the code so you can run it for just one metric at a time or all at once, once all metrics present
## combine and reclassify can be available

### Parameters ###
main_workspace = r"F:\GitHub\typology\data" # main workspace for the project

######### 1.A. Time Series (TS) #########
## Remap - Time Series
## NOTE run each metric type separately to remap (set metric_type below)
metric_type = "area"  # "edge", "area", or "pn"
input_raster = os.path.join(main_workspace, "4_TS_and_TI", "TS_zscore", metric_type, f"{metric_type}_MK_tau_z.tif")
output_dir   = os.path.join(main_workspace, "5_Typology", "remap_timeseries", metric_type)

######### 1.B. Time Interval (TI) #########
## Remap - Interval
# metric_type = "pn" # "edge", "area", or "pn"

######### 2. Combine Rasters (TS or TI) #########
## Combine Rasters - Time Interval or Time Series
## NOTE all rasters should be in the same folder- it searches by file name to combine by year
combine_type = "timeseries" # "interval" or "timeseries"

#== Only run the next section once all metric types have been run ==

######### 3. Reclassify and Add Typology Names (TS or TI) #########
## Reclassify and Add Typology Names - Time Interval or Time Series
rc_input  = os.path.join(main_workspace, "5_Typology", f"combined_{combine_type}")
rc_output = os.path.join(main_workspace, "5_Typology", f"combined_rc_{combine_type}")
###################################################################################################

### Functions ###
def get_year(filename):
    # Extract year range pattern like "90-95" from filename (eg. 90-95_area) using regex
    match = re.search(r"(\d{2}-\d{2})", filename)
    return match.group(1) if match else ""

def remap_time_series(metric): #(input_dir, output_dir, metric):
    """
    Remap raster values based on the specified metric (patch, area, edge).
    """
    try:
        # Build input/output paths from main_workspace
        input_dir = os.path.join(main_workspace, "4_TS_and_TI", "TS_zscore", metric)
        output_dir = os.path.join(main_workspace, "5_Typology", "remap_timeseries", metric)
        os.makedirs(output_dir, exist_ok=True)

        print(f"Setting workspace to: {input_dir}")
        arcpy.env.workspace = input_dir
        rasters = arcpy.ListRasters()
        print(f"Found {len(rasters)} rasters: {rasters}")
        
        if not rasters:
            print("No rasters found in workspace!")
            return False
            
        for raster in rasters:
            input_raster_path = os.path.join(input_dir, raster)
            basename = os.path.basename(input_raster_path)
            year = get_year(basename)
            
            # Define remap rules based on the metric
            if metric == "pn":
                output_path = os.path.join(output_dir, f"{year}_pn_rmp.tif")
                # remap_rules = [
                #     (-70, -1.01, 100),
                #     (-1, -0.11, 200),
                #     (-0.1, 0.1, "NODATA"),
                #     (0.11, 1, 200),
                #     (1.01, 70, 300)
                # ]
                # remap_rules = [
                #     (-70, -1.01, 100),
                #     (-1, 1, 200),
                #     (1.01, 70, 300)
                # ]
                remap_rules = [
                    (-70, -0.5, 100),
                    (-0.5, 0.5, 200),
                    (0.5, 70, 300)
                ]
                remap = arcpy.sa.RemapRange(remap_rules)
                output_raster = arcpy.sa.Reclassify(input_raster_path, "Value", remap, "NODATA")
            elif metric == "area":
                output_path = os.path.join(output_dir, f"{year}_area_rmp.tif")
                # remap_rules = [
                #     (-70, -1.01, 10),
                #     (-1, -0.01, 20),
                #     (0.01, 1, 20),
                #     (1.01, 70, 30)
                # ]
                remap_rules = [
                    (-70, -0.5, 10),
                    (-0.5, 0.5, 20),
                    (0.5, 70, 30)
                ]
                remap = arcpy.sa.RemapRange(remap_rules)
                output_raster = arcpy.sa.Reclassify(input_raster_path, "Value", remap, "NODATA")
            elif metric == "edge":
                output_path = os.path.join(output_dir, f"{year}_edge_rmp.tif")
                # remap_rules = [
                #     (-70, -1.01, 1),
                #     (-1, 1, 2),
                #     (1.01, 70, 3)
                # ]
                remap_rules = [
                    (-70, -0.5, 1),
                    (-0.5, 0.5, 2),
                    (0.5, 70, 3)
                ]
                remap = arcpy.sa.RemapRange(remap_rules)
                output_raster = arcpy.sa.Reclassify(input_raster_path, "Value", remap, "NODATA")
                
            else:
                raise ValueError("Invalid metric specified: {}".format(metric))

            if not arcpy.Exists(output_path):
                output_raster.save(output_path)
                print(f"Remapped successful: {output_path}")
        return True
    except Exception as e:
        print(f"Remap error: {str(e)}")
        return None
    
def remap_time_interval(metric): #(input_dir, output_dir, metric):
    """
    Remap raster values based on the specified metric (patch, area, edge).
    """
    try:
        # Build input/output paths from main_workspace
        input_dir = os.path.join(main_workspace, "4_TS_and_TI", "img_diff", metric)
        output_dir = os.path.join(main_workspace, "5_Typology", "remap_interval", metric)
        os.makedirs(output_dir, exist_ok=True)

        rasters = [f for f in os.listdir(input_dir) if f.endswith('.tif')]
        print(f"Found {len(rasters)} rasters: {rasters}")
        
        if not rasters:
            print("No rasters found")
            return False
            
        for raster in rasters:
            input_raster_path = os.path.join(input_dir, raster)
            basename = os.path.basename(input_raster_path)
            year = get_year(basename)
            
            # Define remap rules based on the metric
            if metric == "pn":
                output_path = os.path.join(output_dir, f"{year}_pn_rmp.tif")
                remap_rules = [
                    (-3005, -0.01, 100),
                    (0, 0, 200),
                    (0.01, 3005, 300)
                ]
                remap = arcpy.sa.RemapRange(remap_rules)
                output_raster = arcpy.sa.Reclassify(input_raster_path, "Value", remap, "NODATA")
            elif metric == "area":
                output_path = os.path.join(output_dir, f"{year}_area_rmp.tif")
                remap_rules = [
                    (-3005, -0.01, 10),
                    (0, 0, 20),
                    (0.01, 3005, 30)
                ]
                remap = arcpy.sa.RemapRange(remap_rules)
                output_raster = arcpy.sa.Reclassify(input_raster_path, "Value", remap, "NODATA")
            elif metric == "edge":
                output_path = os.path.join(output_dir, f"{year}_edge_rmp.tif")
                remap_rules = [
                    (-3005, -0.01, 1),
                    (0, 0, 2),
                    (0.01, 3005, 3)
                ]
                remap = arcpy.sa.RemapRange(remap_rules)
                output_raster = arcpy.sa.Reclassify(input_raster_path, "Value", remap, "NODATA")

            else:
                raise ValueError("Invalid metric specified: {}".format(metric))

            # Preserve NoData from original input
            input_r = arcpy.sa.Raster(input_raster_path)
            output_raster = arcpy.sa.SetNull(arcpy.sa.IsNull(input_r), output_raster)

            if not arcpy.Exists(output_path):
                output_raster.save(output_path)
                print(f"Remapped successful: {output_path}")
        return True
    except Exception as e:
        print(f"Remap error: {str(e)}")
        return None


def combine_rasters(combine_type):
    """Combine edge, area, and pn rasters based on combine_type ('interval' or 'timeseries')."""
    try:
        base_dir = os.path.join(main_workspace, "5_Typology", f"remap_{combine_type}")
        output_dir = os.path.join(main_workspace, "5_Typology", f"combined_{combine_type}")
        os.makedirs(output_dir, exist_ok=True)

        edge_dir = os.path.join(base_dir, "edge")
        area_dir = os.path.join(base_dir, "area")
        pn_dir = os.path.join(base_dir, "pn")

        edge_files = [f for f in os.listdir(edge_dir) if f.endswith('.tif')]
        area_files = [f for f in os.listdir(area_dir) if f.endswith('.tif')]
        pn_files = [f for f in os.listdir(pn_dir) if f.endswith('.tif')]

        if not (edge_files and area_files and pn_files):
            print("NOT all file types found - exiting early")
            return False

        if combine_type == "interval":
            for edge_file in edge_files:
                year = get_year(edge_file)
                area_file = f"{year}_area_rmp.tif"
                patch_file = f"{year}_pn_rmp.tif"

                edge_path = os.path.join(edge_dir, edge_file)
                area_path = os.path.join(area_dir, area_file)
                patch_path = os.path.join(pn_dir, patch_file)

                if os.path.exists(area_path) and os.path.exists(patch_path):
                    output_path = os.path.join(output_dir, f"{year}_combined.tif")
                    edge_r = arcpy.sa.Raster(edge_path)
                    area_r = arcpy.sa.Raster(area_path)
                    patch_r = arcpy.sa.Raster(patch_path)

                    combined = arcpy.sa.Con(arcpy.sa.IsNull(edge_r), 0, edge_r) + \
                              arcpy.sa.Con(arcpy.sa.IsNull(area_r), 0, area_r) + \
                              arcpy.sa.Con(arcpy.sa.IsNull(patch_r), 0, patch_r)

                    combined.save(output_path)
                    arcpy.management.BuildRasterAttributeTable(output_path)
                    print(f"Combined raster created: {output_path}")

        elif combine_type == "timeseries":
            edge_r = arcpy.sa.Raster(os.path.join(edge_dir, edge_files[0]))
            area_r = arcpy.sa.Raster(os.path.join(area_dir, area_files[0]))
            pn_r = arcpy.sa.Raster(os.path.join(pn_dir, pn_files[0]))

            combined = arcpy.sa.Con(arcpy.sa.IsNull(edge_r), 0, edge_r) + \
                      arcpy.sa.Con(arcpy.sa.IsNull(area_r), 0, area_r) + \
                      arcpy.sa.Con(arcpy.sa.IsNull(pn_r), 0, pn_r)

            output_path = os.path.join(output_dir, "combined.tif")
            combined.save(output_path)
            arcpy.management.BuildRasterAttributeTable(output_path)
            print(f"Combined raster created: {output_path}")

        else:
            print(f"Error: Undefined combine_type '{combine_type}'. Must be 'interval' or 'timeseries'.")
            return False

        return True
    except Exception as e:
        print(f"Combine error: {str(e)}")
        return False


# Reclassify combined raster values to typology categories and add attribute table labels
def reclassify_typology(combine_type):
    """Reclassify all combined rasters and add typology labels."""
    try:
        input_dir = os.path.join(main_workspace, "5_Typology", f"combined_{combine_type}")
        output_dir = os.path.join(main_workspace, "5_Typology", f"combined_rc_{combine_type}")
        os.makedirs(output_dir, exist_ok=True)

        combined_files = [f for f in os.listdir(input_dir) if f.endswith('combined.tif') or f.endswith('_combined.tif')]

        if not combined_files:
            print("No combined rasters found")
            return False

        for combined_file in combined_files:
            input_raster = os.path.join(input_dir, combined_file)
            basename = os.path.basename(input_raster)
            output_name = f"{os.path.splitext(basename)[0]}_rc.tif"
            output_path = os.path.join(output_dir, output_name)

            # Define typology recoding (original_value: new_val)
            recode_map = {
                111: 1, 112: 1, 113: 1,  # attrition
                121: 2, 122: 2, 123: 2, 131: 2, 132: 2, 133: 2,  # aggregation
                211: 3,  # shrinkage333333
                213: 4,  # perforation
                221: 5, 223: 5,  # deformation
                222: 6, 220: 6,  # persistent
                231: 7, 232: 7, 233: 7, 230: 7,  # enlargement
                311: 8, 312: 8, 313: 8,  # dissection
                321: 9, 322: 9, 323: 9,  # frag per se
                331: 10, 332: 10, 333: 10  # creation
            }

            # Typology labels for new values
            typology_labels = {
                1: "Attrition",
                2: "Aggregation",
                3: "Shrinkage",
                4: "Perforation",
                5: "Deformation",
                6: "Persistent",
                7: "Enlargement",
                8: "Dissection",
                9: "Fragmentation per se",
                10: "Creation"
            }

            # Create remap - unmapped values become NODATA
            remap_rules = [[old_values, old_values, new_values] for old_values, new_values in recode_map.items()]
            remap = arcpy.sa.RemapValue(remap_rules)

            # Reclassification
            output_raster = arcpy.sa.Reclassify(input_raster, "Value", remap, "NODATA")
            output_raster.save(output_path)

            # Build raster attribute table
            arcpy.management.BuildRasterAttributeTable(output_path)

            # Add typology field
            arcpy.management.AddField(output_path, "TYPOLOGY", "TEXT", field_length=50)

            # Add km2 field
            year2 = get_year(basename)
            km2_field = f"km2_{year2}".replace("-", "_")
            arcpy.management.AddField(output_path, km2_field, "DOUBLE")

            # Update field with cursor
            with arcpy.da.UpdateCursor(output_path, ["Value", "Count", "TYPOLOGY", km2_field]) as cursor:
                for row in cursor:
                    if row[0] in typology_labels:
                        row[2] = typology_labels[row[0]]
                        row[3] = row[1] * 0.0009
                        cursor.updateRow(row)

            print(f"Typology reclassification successful: {output_path}")

        return True
    except Exception as e:
        print(f"Typology reclassification error: {str(e)}")
        return False


### Main Execution ### 
if __name__ == "__main__":
    print("Starting Processing")
    
    # # Remap Raster - v2 - USE THIS FOR BOTH TIME INTERVAL AND TIME SERIES
    # print(f"Starting ({metric_type}) remapping process...")
    # rmp_start = time.time()
    # if combine_type == "interval":
    #     rmp_results = remap_time_interval(metric_type)
    # elif combine_type == "timeseries":
    #     rmp_results = remap_time_series(metric_type)
    # rmp_duration = time.time() - rmp_start
    # print("Remap completed in {:.0f} mins. {:.2f} sec.".format(rmp_duration // 60, rmp_duration % 60))

    # # Remap Raster - Time Series- v1
    # print("Starting -- Time Series -- remapping process...")
    # rmp_start = time.time()
    # rmp_results = remap_time_series(metric_type)
    # rmp_duration = time.time() - rmp_start
    # print("Remap completed in {:.0f} mins. {:.2f} sec.".format(rmp_duration // 60, rmp_duration % 60))

     # # Remap Raster - Time Interval- v1
    # print("Starting -- Time Interval -- remapping process...")
    # rmp_start = time.time()
    # rmp_results = remap_time_interval(metric_type)
    # rmp_duration = time.time() - rmp_start
    # print("Remap completed in {:.0f} mins. {:.2f} sec.".format(rmp_duration // 60, rmp_duration % 60))

####################################

    ## Combine Rasters
    print(f"Starting -- {combine_type} -- combining process...")
    c_start = time.time()
    c_results = combine_rasters(combine_type)
    c_duration = time.time() - c_start
    print("Combine completed in {:.0f} mins. {:.2f} sec.".format(c_duration // 60, c_duration % 60))

    ## Reclassify and Add Typology Names
    print(f"Starting -- {combine_type} -- typology reclassification...")
    rc_start = time.time()
    rc_results = reclassify_typology(combine_type)
    rc_duration = time.time() - rc_start
    print("Reclassify completed in {:.0f} mins. {:.2f} sec.".format(rc_duration // 60, rc_duration % 60))








    
    
    
    
    ### NOTES ###
    
    # Debug: Check paths
    # print(f"Input raster: {input_raster}")
    # print(f"Input exists: {os.path.exists(input_raster)}")
    # print(f"Output dir: {output_dir}")
    # print(f"Output dir exists: {os.path.exists(output_dir)}")
    
    # Debug: Check ArcPy
    # try:
    #     print(f"ArcPy version: {arcpy.GetInstallInfo()['Version']}")
    #     arcpy.CheckOutExtension("Spatial")
    #     print("Spatial Analyst license checked out")
    # except Exception as e:
    #     print(f"ArcPy setup error: {e}")
    #     sys.exit(1)
    
    
# This is the original combine which only calculates values when they over lap (100 + 20 + 2 = 122, NOT 100 + 20 + 0 = 0)
# def combine_by_year(input_dir, output_dir):
#     """Automatically combine edge, area, and patch rasters by year."""
#     edge_files = [f for f in os.listdir(input_dir) if f.endswith('_edge_rmp.tif')]
    
#     for edge_file in edge_files:
#         year = get_year(edge_file)
#         area_file = f"{year}_area_rmp.tif"
#         patch_file = f"{year}_pn_rmp.tif"
        
#         edge_path = os.path.join(input_dir, edge_file)
#         area_path = os.path.join(input_dir, area_file)
#         patch_path = os.path.join(input_dir, patch_file)
        
#         if os.path.exists(area_path) and os.path.exists(patch_path):
#             output_path = os.path.join(output_dir, f"{year}_combined.tif")
#             try:
#                 combined = arcpy.sa.Raster(edge_path) + arcpy.sa.Raster(area_path) + arcpy.sa.Raster(patch_path)
#                 combined.save(output_path)
#                 arcpy.management.BuildRasterAttributeTable(output_path)
#                 print(f"Combined raster created: {output_path}")
#             except Exception as e:
#                 print(f"Combine error: {str(e)}")

# def combine_by_year(input_dir, output_dir):
#     try:
#         # Get edge files and find corresponding area/patch files
#         edge_files = [f for f in os.listdir(input_dir) if f.endswith('_edge_rmp.tif')]
        
#         for edge_file in edge_files:
#             year = get_year(edge_file)
#             area_file = f"{year}_area_rmp.tif"
#             pn_file = f"{year}_pn_rmp.tif"
            
#             # File paths
#             edge_path = os.path.join(input_dir, edge_file)
#             area_path = os.path.join(input_dir, area_file)
#             pn_path = os.path.join(input_dir, pn_file)
#             output_path = os.path.join(output_dir, f"{year}_combined.tif")
            
#             # Use Raster Calculator to combine
#             # expression = f'"{patch_path}" + "{area_path}" + "{edge_path}"'
#             # arcpy.gp.RasterCalculator_sa(expression, output_path)
#             print(f"Combined raster saved: {output_path}")
            
#         return True
#     except Exception as e:
#         print(f"Combine error: {str(e)}")
        
#         if os.path.exists(area_path) and os.path.exists(patch_path):
#             output_path = os.path.join(output_dir, f"{year}_combined.tif")
#             try:
#                 combined = arcpy.sa.Raster(edge_path) + arcpy.sa.Raster(area_path) + arcpy.sa.Raster(patch_path)
#                 combined.save(output_path)
#                 arcpy.management.BuildRasterAttributeTable(output_path)
#                 print(f"Combined raster created: {output_path}")
#             except Exception as e:
#                 print(f"Combine error: {str(e)}")













############################### old way of combining before the use of combine type ################################################ 7/19/26

# ### Parameters ###
# main_workspace = r"D:\Mikayla\site_selection" # main workspace for the project

# ######### Time Series #########
# # Remap - Time Series ### NOTE this needs to be updated ###############################
# #run each metric type separately to remap
# # input_raster = r"B:\Mikayla\DATA\Projects\AF\Typology_collection9\4_TS_and_TI\TS_zscore\edge\edge_MK_tau_z.tif"
# # output_dir = r"B:\Mikayla\DATA\Projects\AF\Typology_collection9\5_Typology\remap_timeseries"
# # metric_type = "edge" # "edge "or "area", "pn"

# # input_raster = r"D:\Typology\data\4_TS_and_TI\TS_zscore\edge\edge_MK_tau_z.tif"
# # output_dir = r"D:\typology\data\5_Typology\remap_timeseries"
# # metric_type = "edge" # "edge "or "area", "pn"

# ######### Time Interval #########
# # Remap - Interval
# #input_raster = r"D:\Mikayla\site_selection\4_TS_and_TI\img_diff\pn\*.tif" #r"D:\typology\data\4_TS_and_TI\img_diff\pn\*.tif" # change folder for each metric type
# #output_dir = r"D:\Mikayla\site_selection\5_Typology\remap_interval" #r"D:\typology\data\5_Typology\remap_interval" 
# # built in dont need input and out put now 7/19/26
# metric_type = "pn" # "edge", "area", or "pn"

# ######### Combine Rasters (TS or TI) #########
# # Combine Rasters - Time Interval or Time Series
# # all rasters should be in the same folder- it searches by file name to combine by year
# #combine_input = r"D:\Mikayla\site_selection\5_Typology\remap_interval" #r"D:\typology\data\4_TS_and_TI\1990_2020\remap_interval" #interval" #timeseries"
# #combine_output = r"D:\Mikayla\site_selection\5_Typology\combined_interval" #r"D:\typology\data\4_TS_and_TI\1990_2020\combined_interval" #interval" #timeseries"
# combine_type = "interval" # "interval" or "timeseries"

# ######### Reclassify and Add Typology Names (TS or TI) #########
# # Reclassify and Add Typology Names - Time Interval or Time Series
# #rc_input = r"D:\Mikayla\site_selection\5_Typology\combined_interval" #r"D:\typology\data\4_TS_and_TI\1990_2020\combined_interval" #interval OR timeseries
# #rc_output = r"D:\Mikayla\site_selection\5_Typology\combined_rc_interval" #r"D:\typology\data\4_TS_and_TI\1990_2020\combined_rc_interval" #interval OR timeseries

###################################################################################################


# takes all posibilties and adds them together (100 + 20 + 2 = 122, AND 100 + 20 + 0 = 0)      
# def combine_by_year(input_dir, output_dir):
#     """Automatically combine edge, area, and patch rasters by year."""
#    #edge_files = [f for f in os.listdir(input_dir) if f.endswith('_edge_rmp.tif')]
#     edge_files = [f for f in os.listdir(input_dir) if 'edge' in f and f.endswith('.tif')]

#     for edge_file in edge_files:
#         year = get_year(edge_file)
#         area_file = f"{year}_area_rmp.tif"
#         patch_file = f"{year}_pn_rmp.tif"
        
#         edge_path = os.path.join(input_dir, edge_file)
#         area_path = os.path.join(input_dir, area_file)
#         patch_path = os.path.join(input_dir, patch_file)
        
#         if os.path.exists(area_path) and os.path.exists(patch_path):
#             output_path = os.path.join(output_dir, f"{year}_combined.tif")
#             try:
#                 edge_r = arcpy.sa.Raster(edge_path)
#                 area_r = arcpy.sa.Raster(area_path)
#                 patch_r = arcpy.sa.Raster(patch_path)
                
#                 # Use Con to handle NODATA values
#                 # if no data exists, the addition off all 3 rasters will be no data so we apply no data to 0 to fix that
#                 combined = arcpy.sa.Con(arcpy.sa.IsNull(edge_r), 0, edge_r) + \
#                           arcpy.sa.Con(arcpy.sa.IsNull(area_r), 0, area_r) + \
#                           arcpy.sa.Con(arcpy.sa.IsNull(patch_r), 0, patch_r)
                
#                 combined.save(output_path)
#                 arcpy.management.BuildRasterAttributeTable(output_path)
#                 print(f"Combined raster created: {output_path}")
#             except Exception as e:
#                 print(f"Combine error: {str(e)}")
#                 return False


# combine TS output which has only one edge, area, and pn raster in the folder              
# def combine_TS(input_dir, output_dir):
#     """Combine edge, area, and pn rasters."""
#     print(f"Checking directory: {input_dir}")
#     print(f"Directory exists: {os.path.exists(input_dir)}")
    
#     all_files = os.listdir(input_dir)
#     print(f"All files: {all_files}")
    
#     edge_files = [f for f in os.listdir(input_dir) if 'edge' in f and f.endswith('.tif')]
#     area_files = [f for f in os.listdir(input_dir) if 'area' in f and f.endswith('.tif')]
#     pn_files = [f for f in os.listdir(input_dir) if 'pn' in f and f.endswith('.tif')]
    
#     print(f"Edge files: {edge_files}")
#     print(f"Area files: {area_files}")
#     print(f"PN files: {pn_files}")
    
#     if edge_files and area_files and pn_files:
#         print("All files found, processing...")
#         try:
#             print("Loading rasters...")
#             edge_r = arcpy.sa.Raster(os.path.join(input_dir, edge_files[0]))
#             print("Edge raster loaded")
#             area_r = arcpy.sa.Raster(os.path.join(input_dir, area_files[0]))
#             print("Area raster loaded")
#             pn_r = arcpy.sa.Raster(os.path.join(input_dir, pn_files[0]))
#             print("PN raster loaded")
            
#             print("Combining rasters...")
#             combined = arcpy.sa.Con(arcpy.sa.IsNull(edge_r), 0, edge_r) + \
#                       arcpy.sa.Con(arcpy.sa.IsNull(area_r), 0, area_r) + \
#                       arcpy.sa.Con(arcpy.sa.IsNull(pn_r), 0, pn_r)
#             print("Rasters combined")
            
#             output_path = os.path.join(output_dir, "combined.tif")
#             print(f"Saving to: {output_path}")
#             combined.save(output_path)
#             print("Raster saved")
            
#             arcpy.management.BuildRasterAttributeTable(output_path)
#             print(f"Combined raster created: {output_path}")
#             return True
#         except Exception as e:
#             print(f"Combine error: {str(e)}")
#             return False
#     else:
#         print("NOT all file types found - exiting early")
#         return False



# # Reclassify combined raster values to typology categories and add attribute table labels
# def reclassify_typology(input_dir, output_dir):
#     """Reclassify all combined rasters in the input directory."""
#     combined_files = [f for f in os.listdir(input_dir) if f.endswith('combined.tif') or f.endswith('_combined.tif')] #for both TS and TI outputs
    
#     for combined_file in combined_files:
#         try:
#             input_raster = os.path.join(input_dir, combined_file)
#             basename = os.path.basename(input_raster)
#             output_name = f"{os.path.splitext(basename)[0]}_rc.tif"
#             output_path = os.path.join(output_dir, output_name)
            
#             # Define typology recoding (original_value: new_val)
#             recode_map = {
#             111: 1, 112: 1, 113: 1,  # attrition
#             121: 2, 122: 2, 123: 2, 131: 2, 132: 2, 133: 2, # aggregation
#             211: 3, # shrinkage
#             213: 4, # perforation 
#             221: 5, 223: 5, # deformation
#             222: 6, 220: 6, # persistent
#             231: 7, 232: 7, 233: 7, 230: 7,  # enlargement - (added 230 = if patch becomes too large for window)
#             311: 8, 312: 8, 313: 8,  # dissection
#             321: 9, 322: 9, 323: 9,  # frag per se
#             331: 10, 332: 10, 333: 10  # creation
#             }

#             # Typology labels for new values
#             typology_labels = {
#             #0: "background", 
#             1: "Attrition", 
#             2: "Aggregation", 
#             3: "Shrinkage",
#             4: "Perforation", 
#             5: "Deformation", 
#             6: "Persistent", # originally was shift 
#             7: "Enlargement",
#             8: "Dissection", 
#             9: "Fragmentation per se", 
#             10: "Creation"
#             }
            
#             ########## need to set anything not covered by the recode map to 0 and preserve current nodata values
#             # Create remap - unmapped values become NODATA
#             remap_rules = [[old_values, old_values, new_values] for old_values, new_values in recode_map.items()]
#             remap = arcpy.sa.RemapValue(remap_rules)
            
#             # reclassification
#             output_raster = arcpy.sa.Reclassify(input_raster, "Value", remap, "NODATA")
#             output_raster.save(output_path)
            
#             # Build raster attribute table
#             arcpy.management.BuildRasterAttributeTable(output_path)
            
#             # Add typology field
#             arcpy.management.AddField(output_path, "TYPOLOGY", "TEXT", field_length=50) # adds typology name field

#             # Add km2 field
#             year2 = get_year(basename)
#             km2_field = f"km2_{year2}".replace("-", "_")  # Replace dash with underscore
#             arcpy.management.AddField(output_path, km2_field, "DOUBLE") # adds km

#             # Update field with cursor
#             with arcpy.da.UpdateCursor(output_path, ["Value", "Count", "TYPOLOGY", km2_field]) as cursor:
#                 for row in cursor:
#                     if row[0] in typology_labels:
#                         row[2] = typology_labels[row[0]] # typology field #[1]
#                         row[3] = row[1] * 0.0009 # year_km2 field = count field * 0.0009 = km2
#                         #row[3] = round(row[1] * 0.0009)  # Round to whole number
#                         cursor.updateRow(row)
            
#             print(f"Typology reclassification successful: {output_path}")
            
#         except Exception as e:
#             print(f"Typology reclassification error for {combined_file}: {str(e)}")


### Main Execution ### TIME SERIES
# if __name__ == "__main__":
#     print("Starting Processing")
    
#     # Remap Raster - Time Series
#     print("Starting remapping process...")
#     rmp_start = time.time()
#     rmp_results = remap_time_series(
#         input_dir=input_raster,
#         output_dir=output_dir,
#         metric=metric_type
#     )
#     rmp_duration = time.time() - rmp_start
#     print("Remap completed in {:.0f} mins. {:.2f} sec.".format(rmp_duration // 60, rmp_duration % 60))
    
#     # Combine Rasters- Time Series
#     print("Starting combining process...")
#     c2_start = time.time()
#     c2_results = combine_TS(
#         input_dir= combine_input,
#         output_dir= combine_output
#     )
#     c2_duration = time.time() - c2_start
#     print("Combine completed in {:.0f} mins. {:.2f} sec.".format(c2_duration // 60, c2_duration % 60))
    
#     # Reclassify Combined Raster and Add Typology Names
#     print("Starting reclassification process...")
#     rc_start = time.time()
#     reclassify_typology(
#         input_dir= rc_input,
#         output_dir= rc_output
#     )
#     rc_duration = time.time() - rc_start
#     print("Reclassification completed in {:.0f} mins. {:.2f} sec.".format(rc_duration // 60, rc_duration % 60))
    
    
    ## add an excel export of attribute tables 
    

### Main Execution ### TIME INTERVAL
# if __name__ == "__main__":
#     print("Starting Processing")

    ## Remap Raster - Time Interval
    # print("Starting remapping process...")
    # rmp_start = time.time()
    # rmp_results = remap_time_interval(
    #     input_dir=os.path.dirname(input_raster),
    #     output_dir=output_dir,
    #     metric=metric_type
    # )
    # rmp_duration = time.time() - rmp_start
    # # print(f"Remap completed in {rmp_duration:.2f} seconds") # just prints seconds
    # print("Remap completed in {:.0f} mins. {:.2f} sec.".format(rmp_duration // 60, rmp_duration % 60))
    
    ## Combine Rasters- Time Interval
    # print("Starting combining process...")
    # c_start = time.time()
    # c_results = combine_by_year(
    #     input_dir= combine_input,
    #     output_dir= combine_output
    # )
    # c_duration = time.time() - c_start
    # print("Combine completed in {:.0f} mins. {:.2f} sec.".format(c_duration // 60, c_duration % 60))
    
    ## Reclassify Combined Raster and Add Typology Names
    # print("Starting reclassification process...")
    # rc_start = time.time()
    # reclassify_typology(
    #     input_dir= rc_input,
    #     output_dir= rc_output
    # )
    # rc_duration = time.time() - rc_start
    # print("Reclassification completed in {:.0f} mins. {:.2f} sec.".format(rc_duration // 60, rc_duration % 60))
    
    
    
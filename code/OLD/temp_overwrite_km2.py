### TEMPORARY: overwrite km2 with the raster's real cell area (not 30 m) ###
import os, glob
import arcpy

main_workspace = r"F:\GitHub\typology\data"
typ = os.path.join(main_workspace, "5_Typology")

labels = {1: "Attrition", 2: "Aggregation", 3: "Shrinkage", 4: "Perforation", 5: "Deformation",
          6: "Persistent", 7: "Enlargement", 8: "Dissection", 9: "Fragmentation per se", 10: "Creation"}

rasters = sorted(glob.glob(os.path.join(typ, "TimeInterval*.tif")))
rasters.append(os.path.join(typ, "combined_rc_timeseries", "combined_rc.tif"))

for path in rasters:
    print(os.path.basename(path))
    try:
        desc = arcpy.Describe(path)
        cell_km2 = desc.meanCellWidth * desc.meanCellHeight / 1e6
        print(f"  cell size {desc.meanCellWidth:.6f} m -> {cell_km2:.8f} km2 per pixel")

        # Build the attribute table if missing ("NONE" keeps an existing table)
        arcpy.management.BuildRasterAttributeTable(path, "NONE")

        names = [f.name for f in arcpy.ListFields(path)]
        if "TYPOLOGY" not in names:
            arcpy.management.AddField(path, "TYPOLOGY", "TEXT", field_length=50)
        km2_fields = [n for n in names if n.lower().startswith("km2")]
        if not km2_fields:
            arcpy.management.AddField(path, "km2", "DOUBLE")
            km2_fields = ["km2"]

        total_px, total_km2 = 0, 0.0
        with arcpy.da.UpdateCursor(path, ["Value", "Count", "TYPOLOGY"] + km2_fields) as cursor:
            for row in cursor:
                km2 = row[1] * cell_km2
                row[2] = labels.get(row[0], row[2])
                for i in range(3, len(row)):
                    row[i] = km2
                cursor.updateRow(row)
                total_px += row[1]
                total_km2 += km2
        print(f"  updated {km2_fields} | {total_px:,} pixels | {total_km2:,.1f} km2")
    except Exception as e:
        print("  FAILED:", e)

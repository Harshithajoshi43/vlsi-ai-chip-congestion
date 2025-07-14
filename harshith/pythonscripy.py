# export_gds_features.py: Extract geometry and density from full_adder.gds using KLayout Python API.

import pya
import csv

# Open the GDS layout (change path to your full_adder.gds)
layout = pya.Layout()
layout.read("full_adder.gds")

cell = layout.top_cell()

# Define layers of interest (layer number, datatype) for N, P transistors and metals
layers = {
    "N_active": layout.layer(1, 0),  # example layer numbers; use correct ones for the PDK
    "P_active": layout.layer(2, 0),
    "metal1"  : layout.layer(3, 0),
    "metal2"  : layout.layer(4, 0)
    # (Adjust layer IDs based on the technology; 1,2 might be diff for Sky130)
}

# Prepare CSV for geometry features
with open("layout_features.csv", "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["layer", "datatype", "area", "xmin", "ymin", "xmax", "ymax"])
    for layer_name, layer_index in layers.items():
        # Get all shapes (polygons) on this layer in the top cell
        shapes = cell.each_shape(layer_index)
        for shape in shapes:
            if shape.is_box():
                box = shape.box()
                xmin, ymin = box.left, box.bottom
                xmax, ymax = box.right, box.top
                area = box.area()
            else:
                # For simplicity, use the bounding box of complex shapes
                bbox = shape.bbox()
                xmin, ymin = bbox.left, bbox.bottom
                xmax, ymax = bbox.right, bbox.top
                area = bbox.width() * bbox.height()
            writer.writerow([layer_index[0], layer_index[1], int(area), xmin, ymin, xmax, ymax])

# Compute a simple metal density grid on metal layers
grid_size = 10_000  # 10 µm grid (units depend on technology units)
density = {}
# Initialize grid cells
for x in range(0, int(layout.dbu * 1000 * 1000), grid_size):  # example extents
    for y in range(0, int(layout.dbu * 1000 * 1000), grid_size):
        density[(x//grid_size, y//grid_size)] = 0

# Accumulate metal area per cell for metal1 and metal2 layers
for layer_name in ["metal1", "metal2"]:
    layer_index = layers[layer_name]
    shapes = cell.each_shape(layer_index)
    for shape in shapes:
        pts = shape.to_itype(layout.dbu).polygon[:]  # polygon points in integer DBU
        # Rasterize the polygon into grid cells (this is simplified)
        bbox = shape.bbox()
        xmin_cell = int(bbox.left / grid_size)
        xmax_cell = int(bbox.right / grid_size)
        ymin_cell = int(bbox.bottom / grid_size)
        ymax_cell = int(bbox.top / grid_size)
        # Add full area of box to each intersecting cell (overestimate)
        box_area = (bbox.right - bbox.left) * (bbox.top - bbox.bottom)
        for i in range(xmin_cell, xmax_cell+1):
            for j in range(ymin_cell, ymax_cell+1):
                density[(i,j)] += box_area

# Write density grid to CSV
with open("density_grid.csv", "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["cell_x", "cell_y", "metal1_area", "metal2_area"])
    for (i,j), area in density.items():
        writer.writerow([i, j, area if layer_name=="metal1" else "", area if layer_name=="metal2" else ""])


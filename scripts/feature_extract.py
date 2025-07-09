#!/usr/bin/env python3
"""
feature_extract.py  –  convert DEF → grid features → CSV

USAGE EXAMPLE
-------------
python3 feature_extract.py \
        --def_file  ../data/spm.def \
        --grid      64 \
        --out       ../dataset/dataset.csv
"""
import argparse, re, csv, pathlib


# ------------------------------------------------------------
# 1. Parse the DEF file → list of (x, y, master_name)
# ------------------------------------------------------------
def parse_def(def_path):
    cells = []
    with open(def_path) as f:
        for line in f:
            # Example component line:
            # - U0 sky130_fd_sc_hd__inv_2 + PLACED (  815  780 ) N ;
            if line.startswith('-'):
                m = re.match(
                    r'-\s+\S+\s+\S+\s+\+\s+PLACED\s+\(\s*([0-9]+)\s+([0-9]+)\s*\)',
                    line
                )
                if m:
                    x, y = map(int, m.groups())
                    cells.append((x, y))
    return cells


# ------------------------------------------------------------
# 2. Bin cells into an N×N grid and count cells/pins
# ------------------------------------------------------------
def build_grid(cells, grid, die_size=(147000, 147000)):
    """Return grid[gx][gy] dicts with 'cells' and 'pins'."""
    tile_w = die_size[0] // grid
    tile_h = die_size[1] // grid

    grid_data = [[{'cells': 0, 'pins': 0} for _ in range(grid)]
                 for _ in range(grid)]

    for x, y in cells:
        gx = min(grid - 1, x // tile_w)
        gy = min(grid - 1, y // tile_h)
        grid_data[gx][gy]['cells'] += 1
        grid_data[gx][gy]['pins']  += 3   # rough avg: 3 pins/cell

    return grid_data


# ------------------------------------------------------------
# 3. Dump grid to CSV
# ------------------------------------------------------------
def dump_csv(grid_data, out_path):
    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['grid_x', 'grid_y', 'cell_density', 'pin_count'])
        g = len(grid_data)
        for gx in range(g):
            for gy in range(g):
                d = grid_data[gx][gy]
                writer.writerow([gx, gy, d['cells'], d['pins']])


# ------------------------------------------------------------
# 4. CLI entry‑point
# ------------------------------------------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('--def_file', required=True,
                    help='Path to placed DEF file (e.g. spm.def)')
    ap.add_argument('--grid', type=int, default=64,
                    help='Grid resolution (default 64 = 64×64)')
    ap.add_argument('--out', required=True,
                    help='Output CSV path')
    args = ap.parse_args()

    cells      = parse_def(args.def_file)
    grid_data  = build_grid(cells, args.grid)
    pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    dump_csv(grid_data, args.out)
    print(f"[INFO] Parsed {len(cells)} cells")
    print(f"[INFO] CSV saved to {args.out}")

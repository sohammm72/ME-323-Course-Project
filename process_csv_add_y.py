import pandas as pd
import numpy as np
import sys

csv_file = "profile_data_testv2_20251024_020244.csv"
output_ply = "mircochannel_point_cloud.ply"

print("Loading CSV file...")
df = pd.read_csv(csv_file)

print(f"Total rows: {len(df)}")
num_profiles = df['Profile_Number'].nunique()
print(f"Unique profiles: {num_profiles}")
print(f"Profile range: {df['Profile_Number'].min()} to {df['Profile_Number'].max()}")

total_y_distance = 65

y_step = total_y_distance / (num_profiles)
print(f"Calculated Y step between profiles: {y_step:.6f} mm")

df['Y'] = (df['Profile_Number'] - 1) * y_step

print(f"\nData preview with Y values:")
print(df.head(10))

print(f"\nWriting PLY file: {output_ply}")

vertices = df[['X', 'Y', 'Z']].values

with open(output_ply, 'w') as f:
    f.write("ply\n")
    f.write("format ascii 1.0\n")
    f.write(f"element vertex {len(vertices)}\n")
    f.write("property float x\n")
    f.write("property float y\n")
    f.write("property float z\n")
    f.write("end_header\n")
    
    for i, vertex in enumerate(vertices):
        f.write(f"{vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")
        if (i + 1) % 100000 == 0:
            print(f"  Written {i + 1}/{len(vertices)} points...")

print(f"\nSuccessfully created PLY file: {output_ply}")
print(f"Total points: {len(vertices)}")
print(f"Y range: {df['Y'].min():.3f} to {df['Y'].max():.3f} mm")

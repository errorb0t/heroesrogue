import os

input_folder = r"./Base.StormAssets/Assets/Textures"
output_file = "PreloadAssetDB.txt"
asset_prefix = "Assets/Textures/"

with open(output_file, "w") as f:
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(".dds"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, input_folder)
                rel_path = rel_path.replace("\\", "/")
                f.write(f"asset={asset_prefix}{rel_path}\n")

print("PreloadAssetDB.txt generated.")

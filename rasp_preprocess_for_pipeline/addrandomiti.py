import os

# Directory containing the files
directory = 'Z:\D2behavior\prj5-5\\3CSRTT-phase1\\raw_raspberypi_nb07\\new_files'  # replace with the actual path to your directory

# Loop through each file in the directory
for filename in os.listdir(directory):
    # Split the filename to insert the desired text
    parts = filename.split('_')
    if len(parts) > 2 and parts[0].startswith('results'):
        # Insert '_random-iti_' between 'TO' and 'day'
        new_filename = f"{parts[0]}_{parts[1]}_random-iti-space-50_{parts[3]}_{parts[4]}"
        # Rename the file
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))

print("Files renamed successfully.")

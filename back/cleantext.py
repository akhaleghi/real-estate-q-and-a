import os

# Specify the directory path
directory_path = "text/realized1031/"


def cleantext():
    # Iterate through each file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):  # Check if the file is a text file
            file_path = os.path.join(directory_path, filename)

            # Open the file for reading
            with open(file_path, "r") as file:
                content = file.readlines()[:-3]

            # Change content to string
            updated_content = ''.join(content)

            # Open the file for writing (this will overwrite the file)
            with open(file_path, "w") as file:
                file.write(updated_content)



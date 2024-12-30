import time_tracker
import time_tracker_v2

print("Choose a version to run:")
print("1. Version 1")
print("2. Version 2")
choice = input("Enter your choice: ")

if choice == "1":
    time_tracker.run()
elif choice == "2":
    time_tracker_v2.run()
else:
    print("Invalid choice!")

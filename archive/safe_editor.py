from backup_manager import create_backup
import yaml

def safe_write(filename, content):
    # Step 1: Validate YAML (ONLY for .yaml files)
    if filename.endswith(".yaml"):
        try:
            yaml.safe_load(content)
        except Exception as e:
            print(f"Invalid YAML. Aborting. Error: {e}")
            return False

    # Step 2: backup
    backup_path = create_backup()

    if not backup_path:
        print("Backup failed. Aborting.")
        return False

    # Step 3: preview
    print(f"\nProposed update to {filename}:\n")
    print(content[:500])

    # Step 4: confirm
    confirm = input("\nApply change? (y/n): ")

    if confirm.lower() != "y":
        print("Change cancelled")
        return False

    # Step 5: write file
    try:
        with open(filename, "w") as f:
            f.write(content)
        print("File updated successfully")
        return True
    except Exception as e:
        print(f"Write failed: {e}")
        return False

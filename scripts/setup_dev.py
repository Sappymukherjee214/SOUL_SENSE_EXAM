import subprocess
import sys
import os

def run_command(command, description):
    print(f"🚀 {description}...")
    try:
        # Use sys.executable to ensure we use the same python interpreter
        full_command = f"{sys.executable} {command}"
        subprocess.check_call(full_command, shell=True)
        print(f"✅ {description} complete.\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed! Error: {e}")
        sys.exit(1)

def main():
    print("🧠 Soul Sense EQ - Developer Setup 🧠")
    print("---------------------------------------")
    
    # 1. Alembic upgrades
    # Note: alembic is an executable, but better to run via python -m alembic
    run_command("-m alembic upgrade head", "Applying Database Migrations")
    
    # 2. Seed DB (Questions)
    run_command("-m scripts.seed_db", "Seeding Initial Data")

    # 3. Assessment Migration
    run_command("-m scripts.migrate_assessments", "Initializing Assessment Feature")

    # 4. Journal V2 Migration
    run_command("-m scripts.migrate_journal_v2", "Initializing Journal V2 Feature")

    # 5. Settings Migration (Optional, usually for upgrades)
    run_command("-m scripts.migrate_settings", "Checking User Settings Migration")

    print("🎉 Setup Complete! You can now run the app with:")
    print(f"   {sys.executable} -m app.main")

if __name__ == "__main__":
    main()

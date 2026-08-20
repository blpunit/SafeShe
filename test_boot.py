import sys
import traceback

def test_startup():
    try:
        import app.main
        print("SUCCESS: app.main imported successfully without circular dependencies or errors.")
        sys.exit(0)
    except Exception as e:
        print("FAILED: Failed to import app.main")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_startup()

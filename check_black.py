import subprocess
import sys


def run_black_check():
    result = subprocess.run(
        ["black", "--check", "--diff", "."], capture_output=True, text=True
    )

    if result.returncode != 0:
        print("❌ Black found formatting issues. Run 'black .' to fix them.")
        print("=== Подробности ===")
        print(result.stderr if result.stderr else result.stdout)  # Выводим оба потока
        sys.exit(1)
    print("✅ Код соответствует Black!")
    sys.exit(0)


if __name__ == "__main__":
    run_black_check()

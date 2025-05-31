import subprocess

def run_python_file(filename):
    try:
        result = subprocess.run(["python", filename], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error in {filename}: {result.stderr}"
    except Exception as e:
        return f"Exception occurred: {e}"

output1 = run_python_file("sqllite_adder.py")
output2 = run_python_file("newapi_price_monitor.py")

print("Output from sqlite.py:")
print(output1)
print("\nOutput from finlight_price monitor.py:")
print(output2)

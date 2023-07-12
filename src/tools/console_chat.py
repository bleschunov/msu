import sys
import signal
from chain import db_chain
from custom_memory import custom_memory
from sql_database_chain_executor import SQLDatabaseChainExecutor

"""
Консольный вариант чата с языковой моделью
"""


def signal_handler(signal, frame):
    print("\nClosing program")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

print("Creating executor...")
executor = SQLDatabaseChainExecutor(
    db_chain, custom_memory, debug=False, verbose=False, return_intermediate_steps=True
)
print("Done.")

print('How to use: enter "reset" to clear context, press Ctrl+C to exit')

while True:
    user_prompt = input("Enter prompt: ")
    print()
    if user_prompt == "reset":
        executor.reset()
        print("Memory erased\n")
        continue
    answer = executor.run(user_prompt.strip())
    intermediate_sql_pretty = executor.get_last_intermediate_steps()[1]
    print(f"Intermediate SQL Query:\n{intermediate_sql_pretty}\n")
    print(f"Answer: {answer}\n")

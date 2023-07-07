from chain import db_chain
from custom_memory import custom_memory
from sql_database_chain_executor import SQLDatabaseChainExecutor

executor = SQLDatabaseChainExecutor(db_chain, custom_memory, debug=False)

print(executor.run("Топ 5 компаний по доходу за 2023 год"))
print(executor.run("Какая из этих компаний заработала больше всего?"))
print(executor.run("Сколько она заработала?"))

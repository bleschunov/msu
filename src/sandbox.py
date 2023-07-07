from chain import db_chain
from custom_memory import custom_memory
from sql_database_chain_executor import SQLDatabaseChainExecutor

executor = SQLDatabaseChainExecutor(db_chain, custom_memory, debug=True, verbose=False)

executor.run("Топ 5 компаний по доходу за 2023 год")
executor.run("Какая из этих компаний заработала больше всего?")
executor.run("Сколько она заработала за 2023?")
executor.reset()
executor.run("Какой контрагент перевёл больше всего денег?")

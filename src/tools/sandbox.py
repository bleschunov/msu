from components.chain import db_chain
from components.custom_memory import custom_memory
from components.sql_database_chain_executor import SQLDatabaseChainExecutor


executor = SQLDatabaseChainExecutor(
    db_chain, custom_memory, debug=False, verbose=False, return_intermediate_steps=True
)

executor.run("Топ 5 компаний по доходу за 2023 год")
executor.run("Какая из этих компаний заработала больше всего?")
executor.run("Сколько она заработала за 2023?")
executor.reset()
executor.run("Какой контрагент перевёл больше всего денег?")

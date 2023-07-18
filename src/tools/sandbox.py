from chain import db_chain
from custom_memory import custom_memory
from sql_database_chain_executor import SQLDatabaseChainExecutor


executor = SQLDatabaseChainExecutor(
    db_chain, custom_memory, debug=True, verbose=False, return_intermediate_steps=True
)

executor.run("Сколько мы всего заработали?")

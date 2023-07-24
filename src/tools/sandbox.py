from components.chain import db_chain
from components.custom_memory import custom_memory
from components.sql_database_chain_executor import SQLDatabaseChainExecutor


executor = SQLDatabaseChainExecutor(
    db_chain, custom_memory, debug=True, verbose=False, return_intermediate_steps=True
)

executor.run("Сколько мы всего заработали?")

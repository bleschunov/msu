import os

from supabase import Client, create_client

from testing.models.test import Test
from testing.models.test_set import TestSet


class SupabaseRepository:
    def __int__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

    def insert_test(self, test: Test) -> None:
        self.supabase.table("test").insert(test.get_obj()).execute()

    def insert_test_set(self, test_set: TestSet) -> (dict, int):
        return self.supabase.table("test_set").insert(test_set.get_obj()).execute()


supabase_repository = SupabaseRepository()

from typing import Dict, List, Any, Optional
from .abstract_base_service import AbstractBaseService
from models.user import User  # Your user model


class UserService(AbstractBaseService[User]):
    def __init__(self, supabase_client):
        super().__init__(supabase_client, "users")

    @AbstractBaseService.log_operation
    async def create(self, data: Dict[str, Any]) -> User:
        result = await self.client.from_(self.table_name).insert(data).execute()
        return User(**result.data[0])

    @AbstractBaseService.log_operation
    async def get_by_id(self, id: str) -> Optional[User]:
        result = (
            await self.client.from_(self.table_name)
            .select("*")
            .eq("id", id)
            .single()
            .execute()
        )
        return User(**result.data) if result.data else None

    @AbstractBaseService.log_operation
    async def update(self, id: str, data: Dict[str, Any]) -> User:
        result = (
            await self.client.from_(self.table_name).update(data).eq("id", id).execute()
        )
        return User(**result.data[0])

    @AbstractBaseService.log_operation
    async def delete(self, id: str) -> bool:
        result = (
            await self.client.from_(self.table_name).delete().eq("id", id).execute()
        )
        return bool(result.data)

    @AbstractBaseService.log_operation
    async def list(self, filters: Optional[Dict[str, Any]] = None) -> List[User]:
        query = self.client.from_(self.table_name).select("*")

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        result = await query.execute()
        return [User(**item) for item in result.data]

    # Additional user-specific methods can be added here
    @AbstractBaseService.log_operation
    async def get_by_email(self, email: str) -> Optional[User]:
        result = (
            await self.client.from_(self.table_name)
            .select("*")
            .eq("email", email)
            .single()
            .execute()
        )
        return User(**result.data) if result.data else None

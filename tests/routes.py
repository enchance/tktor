from typing import Annotated, TYPE_CHECKING
from fastapi import APIRouter, Depends


if TYPE_CHECKING:
    from auth import Account, validate_token, current_user

testrouter = APIRouter()


@testrouter.get('/validate_token')
async def validate_token_dep(token_data: Annotated[dict, Depends(validate_token)]) -> dict:
    return token_data


@testrouter.get('/current_user')
async def current_user_dep(account: Annotated[Account, Depends(current_user)]) -> Account:
    return account

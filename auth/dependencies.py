from typing import Annotated, TYPE_CHECKING
from firebase_admin import auth
from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from redis_om import NotFoundError

from core import NotFoundException, AppException, InvalidToken, SessionDep, ic
from core.config import get_session_context
from auth import Auth as auth_


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
#
# def validate_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
#     try:
#         token_data = auth.verify_id_token(token)
#         return token_data
#     except Exception as _:
#         raise InvalidToken('INVALID_TOKEN')


security = HTTPBearer()


def is_valid_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """
    Just know if the token is valid or not.
    """
    token = credentials.credentials
    try:
        if _ := auth.verify_id_token(token):
            return True
        raise InvalidToken()
    except Exception:
        return False


def validate_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Get the decoded token.
    """
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception:
        raise InvalidToken('INVALID_TOKEN')


async def current_user(token_data: Annotated[dict, Depends(validate_token)]) -> auth_.Account:
    """
    Get the user associated with the token.
    """
    uid = token_data['uid']

    async with get_session_context() as session:
        try:
            account = await auth_.Account.get(uid, session=session)
            return account
        except NotFoundError as e:
            try:
                return await auth_.Account.get(uid, session=session)
            except Exception:
                raise NotFoundException('ACCOUNT_NOT_FOUND')
        except:
            raise

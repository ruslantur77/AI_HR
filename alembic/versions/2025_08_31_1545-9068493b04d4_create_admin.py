"""create admin

Revision ID: 9068493b04d4
Revises: 983f97010290
Create Date: 2025-08-31 15:45:54.613772

"""

from typing import Sequence, Union

from sqlalchemy.orm import Session

from alembic import op
from config import config
from models import UserOrm, UserRoleEnum
from security import get_hash

# revision identifiers, used by Alembic.
revision: str = "9068493b04d4"
down_revision: Union[str, Sequence[str], None] = "2342d36f9e1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Создаем сессию для работы с ORM
    bind = op.get_bind()
    session = Session(bind=bind)

    # Проверяем, что админ еще не существует
    admin_email = config.ADMIN_EMAIL
    admin_password = config.ADMIN_PASSWORD
    existing_admin = session.query(UserOrm).filter_by(role=UserRoleEnum.ADMIN).first()
    if not existing_admin:
        admin = UserOrm(email=admin_email, password_hash=get_hash(admin_password))
        admin.role = UserRoleEnum.ADMIN
        session.add(admin)
        session.commit()
        print(f"Created initial admin: {admin_email}")
    else:
        print("Admin already exists, skipping creation")

    session.close()


def downgrade():
    # Опционально удаляем админа, если нужно
    bind = op.get_bind()
    session = Session(bind=bind)
    admin = session.query(UserOrm).filter_by(role=UserRoleEnum.ADMIN).first()
    if admin:
        session.delete(admin)
        session.commit()
        print(f"Deleted initial admin: {admin.email}")
    session.close()

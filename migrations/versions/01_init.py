# Миграция, создающая таблицу wallets
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '01'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Создаём таблицу c полями id (UUID), balance (числовой), created_at, updated_at
    op.create_table('wallets',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('balance', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
    )

def downgrade():
    # Откат миграции - удаление таблицы
    op.drop_table('wallets')
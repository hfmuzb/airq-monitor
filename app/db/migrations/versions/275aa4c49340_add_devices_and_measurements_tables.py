"""add devices and measurements tables

Revision ID: 275aa4c49340
Revises: ee695e924458
Create Date: 2024-02-17 21:49:41.173594

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "275aa4c49340"
down_revision: Union[str, None] = "ee695e924458"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "devices",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("lat", sa.DECIMAL(), nullable=True),
        sa.Column("long", sa.DECIMAL(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("uid", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uid"),
    )
    op.create_table(
        "measurements",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("pm1", sa.DECIMAL(), nullable=True),
        sa.Column("pm2_5", sa.DECIMAL(), nullable=True),
        sa.Column("pm10", sa.DECIMAL(), nullable=True),
        sa.Column("device_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("measurements")
    op.drop_table("devices")
    # ### end Alembic commands ###

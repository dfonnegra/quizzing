"""quiz status

Revision ID: dfd15f65ccf6
Revises: 9b14d66a544d
Create Date: 2024-06-20 17:09:37.694962

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dfd15f65ccf6"
down_revision: Union[str, None] = "9b14d66a544d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE TYPE quiz_status AS ENUM ('draft', 'published')")
    op.add_column(
        "quiz",
        sa.Column(
            "status", sa.Enum("draft", "published", name="quiz_status"), nullable=True
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("quiz", "status")
    op.execute("DROP TYPE quiz_status")
    # ### end Alembic commands ###

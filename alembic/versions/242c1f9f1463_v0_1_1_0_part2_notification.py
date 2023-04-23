"""v0.1.1.0 Part2 Notification

Revision ID: 242c1f9f1463
Revises: 8c4e4c4f3661
Create Date: 2023-04-23 11:26:40.065546+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '242c1f9f1463'
down_revision = '8c4e4c4f3661'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('general_configs', sa.Column('warn_autoclose', sa.Interval(), nullable=True, comment='Time to warn user (via DM) after last response'), schema='tickets_plus')
    op.add_column('tickets', sa.Column('notified', sa.Boolean(), nullable=True, comment='Whether the user has been notified about this ticket'), schema='tickets_plus')
    op.execute('UPDATE tickets_plus.tickets SET notified = FALSE')
    op.alter_column('tickets', 'notified', nullable=False, schema='tickets_plus')
    # ### end Alembic commands ###
    op.add_column('general_configs', sa.Column('first_autoclose_inter', sa.Interval(), nullable=True, comment='Time since open with no response to autoclose'), schema='tickets_plus')
    op.add_column('general_configs', sa.Column('any_autoclose_inter', sa.Interval(), nullable=True, comment='Time since last response to autoclose'), schema='tickets_plus')
    op.execute('UPDATE tickets_plus.general_configs SET first_autoclose_inter = INTERVAL \'1 minute\' * first_autoclose')
    op.execute('UPDATE tickets_plus.general_configs SET any_autoclose_inter = INTERVAL \'1 minute\' * any_autoclose')
    op.drop_column('general_configs', 'first_autoclose', schema='tickets_plus')
    op.drop_column('general_configs', 'any_autoclose', schema='tickets_plus')
    op.alter_column('general_configs', 'first_autoclose_inter', new_column_name='first_autoclose', schema='tickets_plus')
    op.alter_column('general_configs', 'any_autoclose_inter', new_column_name='any_autoclose', schema='tickets_plus')
    


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tickets', 'notified', schema='tickets_plus')
    op.drop_column('general_configs', 'warn_autoclose', schema='tickets_plus')
    # ### end Alembic commands ###
    op.alter_column('general_configs', 'first_autoclose', new_column_name='first_autoclose_inter', schema='tickets_plus')
    op.alter_column('general_configs', 'any_autoclose', new_column_name='any_autoclose_inter', schema='tickets_plus')
    op.add_column('general_configs', sa.Column('first_autoclose', sa.Integer(), nullable=True, comment='Time since open with no response to autoclose'), schema='tickets_plus')
    op.add_column('general_configs', sa.Column('any_autoclose', sa.Integer(), nullable=True, comment='Time since last response to autoclose'), schema='tickets_plus')
    op.execute('UPDATE tickets_plus.general_configs SET first_autoclose = EXTRACT(MINUTE FROM first_autoclose_inter)::INTEGER')
    op.execute('UPDATE tickets_plus.general_configs SET any_autoclose = EXTRACT(MINUTE FROM any_autoclose_inter)::INTEGER')
    op.drop_column('general_configs', 'first_autoclose_inter', schema='tickets_plus')
    op.drop_column('general_configs', 'any_autoclose_inter', schema='tickets_plus')
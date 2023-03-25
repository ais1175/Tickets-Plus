"""v0.1.0.1 part 2 database

Revision ID: 8c713ab3df0b
Revises: ae5d2cc3d90b
Create Date: 2023-03-25 17:24:00.811662+00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8c713ab3df0b'
down_revision = 'ae5d2cc3d90b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags',
                    sa.Column('guild_id',
                              sa.BigInteger(),
                              nullable=False,
                              comment='Unique Guild ID of parent guild'),
                    sa.Column('tag_name',
                              sa.String(length=32),
                              nullable=False,
                              comment="The 'key' of the tag"),
                    sa.Column('title',
                              sa.String(length=256),
                              nullable=True,
                              comment='The title of the embed'),
                    sa.Column('description',
                              sa.String(length=4096),
                              nullable=False,
                              comment='The description of the embed'),
                    sa.Column('url',
                              sa.String(length=256),
                              nullable=True,
                              comment='The url of the embed'),
                    sa.Column('color',
                              sa.Integer(),
                              nullable=True,
                              comment='The color of the embed'),
                    sa.Column('footer',
                              sa.String(length=2048),
                              nullable=True,
                              comment='The footer of the embed'),
                    sa.Column('image',
                              sa.String(length=256),
                              nullable=True,
                              comment='The image of the embed'),
                    sa.Column('thumbnail',
                              sa.String(length=256),
                              nullable=True,
                              comment='The thumbnail of the embed'),
                    sa.Column('author',
                              sa.String(length=256),
                              nullable=True,
                              comment='The author of the embed'),
                    sa.ForeignKeyConstraint(
                        ['guild_id'],
                        ['tickets_plus.general_configs.guild_id'],
                    ),
                    sa.PrimaryKeyConstraint('guild_id', 'tag_name'),
                    schema='tickets_plus',
                    comment='Tags for the guilds.')
    op.create_table(
        'ticket_types',
        sa.Column('prefix',
                  sa.String(length=20),
                  nullable=False,
                  comment='The prefix of the ticket type'),
        sa.Column('guild_id',
                  sa.BigInteger(),
                  nullable=False,
                  comment='The unique discord-provided guild ID'),
        sa.Column(
            'comping',
            sa.Boolean(),
            nullable=False,
            comment='Whether to ping the community roles when template matches'
        ),
        sa.Column(
            'comaccs',
            sa.Boolean(),
            nullable=False,
            comment='Whether to add the community roles when template matches'),
        sa.Column(
            'strpbuttns',
            sa.Boolean(),
            nullable=False,
            comment='Whether to strip buttons from open when template matches'),
        sa.Column('ignore',
                  sa.Boolean(),
                  nullable=False,
                  comment='Whether to ignore this ticket type'),
        sa.ForeignKeyConstraint(
            ['guild_id'],
            ['tickets_plus.general_configs.guild_id'],
        ),
        sa.PrimaryKeyConstraint('prefix', 'guild_id'),
        schema='tickets_plus',
        comment='Ticket types are stored here. Each guild can have multiple.')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ticket_types', schema='tickets_plus')
    op.drop_table('tags', schema='tickets_plus')
    # ### end Alembic commands ###

# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai

"""
Usage:
    hammer gpg [OPTIONS] SUBCOMMAND [ARG] ...

Parameters:
    SUBCOMMAND                    subcommand
    [ARG] ...                     subcommand arguments

Subcommands:
    list                          List GPG Keys
    info                          Show a GPG key
    create                        Create a GPG Key
    update                        Update a GPG Key
    delete                        Destroy a GPG Key
"""

from robottelo.cli.base import Base


class GPGKey(Base):
    """
    Manipulates Foreman's GPG Keys.
    """

    command_base = "gpg"

    def __init__(self):
        """
        Sets the base command for class.
        """
        Base.__init__(self)

    @classmethod
    def exists(cls, organization_id, tuple_search=None):
        """
        Search for a GPG Key.
        """

        # Katello subcommands require the organization-id
        options = {}

        if tuple_search:
            search_criteria = "%s:\"%s\"" % (tuple_search[0], tuple_search[1])
            options["search"] = search_criteria
        # Katello subcommands require extra arguments such as organization-id

        result = cls.list(organization_id, options)

        if result.stdout:
            result.stdout = result.stdout[0]

        return result

    @classmethod
    def list(cls, organization_id, options=None):
        """
        Lists available GPG Keys.
        """

        cls.command_sub = "list"

        if options is None:
            options = {}
            options['per-page'] = 10000

        # Katello subcommands require the organization-id
        options['organization-id'] = organization_id

        result = cls.execute(cls._construct_command(options), expect_csv=True)

        return result
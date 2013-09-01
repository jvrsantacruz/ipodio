# -*- coding: utf-8 -*-

from expects import expect
from mamba import describe, context, before, after

from spec.ui._ipod_helpers import *
from spec.ui._fixture import update_environment


with describe('ipodio rename') as _:

    @before.all
    def setup_all():
        update_environment(_)
        bootstrap_ipod(_.mountpoint_path)

    @after.each
    def cleanup():
        empty_ipod(_.mountpoint_path)

    def should_return_an_error_when_rename_with_bad_expressions():
        execution = _.env.run(
            *_.cmd + ['rm', _.bad_expression, _.bad_expression], expect_error=True)

        expect(execution.stdout).to.have("Error: Invalid expression")

    def should_show_an_error_when_called_without_arguments():
        execution = _.env.run(*_.cmd + ['rename'], expect_error=True)

        expect(execution.stderr).to.have('Usage')

    def should_show_an_error_when_called_with_expression_but_without_replacement():
        execution = _.env.run(*_.cmd + ['rename', _.expression], expect_error=True)

        expect(execution.stderr).to.have('Usage')

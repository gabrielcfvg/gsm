# type: ignore

import pytest


assertion_count = 0

def pytest_assertion_pass(item, lineno, orig, expl):
    global assertion_count
    assertion_count += 1

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    print(f'\n{assertion_count} assertions tested.')

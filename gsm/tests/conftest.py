# type: ignore

import pytest


_assertion_count = 0

def pytest_assertion_pass(item, lineno, orig, expl):
    global _assertion_count
    _assertion_count += 1

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    print(f'\n{_assertion_count} assertions tested.')

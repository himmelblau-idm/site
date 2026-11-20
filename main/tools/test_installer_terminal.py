"""Terminal negotiation must work when a host TERM is absent in a container."""
import os
import types
import unittest
from unittest import mock

from test_install_endpoint import installer


class CursesError(Exception):
    pass


class InstallerTerminalTests(unittest.TestCase):
    def curses(self, supported):
        def setupterm(term, fd):
            if term not in supported:
                raise CursesError("setupterm: could not find terminal")
        return types.SimpleNamespace(error=CursesError, setupterm=mock.Mock(side_effect=setupterm))

    def test_preserves_recognized_terminal(self):
        curses = self.curses({"xterm-ghostty", "xterm-256color"})
        with mock.patch.dict(os.environ, {"TERM": "xterm-ghostty"}), mock.patch.object(installer, "log"):
            installer.configure_curses_terminal(curses)
            self.assertEqual(os.environ["TERM"], "xterm-ghostty")
        curses.setupterm.assert_called_once_with(term="xterm-ghostty", fd=1)

    def test_missing_ghostty_definition_falls_back_to_xterm(self):
        curses = self.curses({"xterm-256color"})
        with mock.patch.dict(os.environ, {"TERM": "xterm-ghostty"}), mock.patch.object(installer, "log") as log:
            installer.configure_curses_terminal(curses)
            self.assertEqual(os.environ["TERM"], "xterm-256color")
        self.assertTrue(any("Using TERM=xterm-256color" in call.args[0] for call in log.call_args_list))

    def test_minimal_terminfo_can_use_vt100(self):
        curses = self.curses({"vt100"})
        with mock.patch.dict(os.environ, {"TERM": "xterm-ghostty"}), mock.patch.object(installer, "log"):
            installer.configure_curses_terminal(curses)
            self.assertEqual(os.environ["TERM"], "vt100")

    def test_missing_or_dumb_term_uses_portable_definition(self):
        for term in (None, "", "dumb"):
            with self.subTest(term=term), mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(installer, "log"):
                if term is not None:
                    os.environ["TERM"] = term
                installer.configure_curses_terminal(self.curses({"xterm"}))
                self.assertEqual(os.environ["TERM"], "xterm")

    def test_no_terminfo_keeps_original_environment_and_reports_fix(self):
        with mock.patch.dict(os.environ, {"TERM": "xterm-ghostty"}), mock.patch.object(installer, "log"):
            with self.assertRaisesRegex(CursesError, "Install your distribution's terminfo package"):
                installer.configure_curses_terminal(self.curses(set()))
            self.assertEqual(os.environ["TERM"], "xterm-ghostty")

    def test_curses_wrapper_starts_after_terminal_fallback(self):
        curses = self.curses({"xterm-256color"})
        def wrapper(callback):
            self.assertEqual(os.environ["TERM"], "xterm-256color")
            return callback("screen")
        curses.wrapper = wrapper
        with mock.patch.dict(os.environ, {"TERM": "xterm-ghostty"}), \
                mock.patch.dict("sys.modules", {"curses": curses}), \
                mock.patch.object(installer, "log"), \
                mock.patch.object(installer, "WizardCursesUi") as wizard:
            wizard.return_value.run.return_value = 130
            self.assertEqual(installer.run_curses(), 130)
            wizard.assert_called_once_with("screen", curses)

    def test_missing_terminfo_stops_before_starting_wizard(self):
        curses = self.curses(set())
        curses.wrapper = mock.Mock()
        with mock.patch.dict(os.environ, {"TERM": "xterm-ghostty"}), \
                mock.patch.dict("sys.modules", {"curses": curses}), \
                mock.patch.object(installer, "log"):
            self.assertEqual(installer.run_curses(), installer.CURSES_STARTUP_EXIT)
        curses.wrapper.assert_not_called()


if __name__ == "__main__":
    unittest.main()

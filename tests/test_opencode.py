"""Regressions for the skipped npm postinstall and safe OpenCode migration."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class OpenCodeTests(unittest.TestCase):
    def run_repair(self, failure=''):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            commands = home / 'test-bin'
            commands.mkdir()
            log = home / 'mise.log'
            mise = commands / 'mise'
            mise.write_text('''#!/bin/bash
printf '%s\\n' "$*" >> "$TEST_LOG"
if [[ -n $TEST_FAILURE && "$*" == "$TEST_FAILURE" ]]; then exit 23; fi
''')
            mise.chmod(0o755)
            opencode = commands / 'opencode'
            opencode.write_text('#!/bin/bash\nprintf "%s\\n" "plain opencode $*" >> "$TEST_LOG"\n')
            opencode.chmod(0o755)
            runtime = home / '.local/share/gran'
            (runtime / 'bin').mkdir(parents=True)
            (runtime / 'version').write_text('0.3.0\n')
            (runtime / 'bin/gran-update').write_text('# old updater\n')
            (home / '.config/mise').mkdir(parents=True)
            config = home / '.config/mise/config.toml'
            config.write_text('[tools]\n"npm:opencode-ai" = "latest"\n')
            profile = home / '.config/opencode/opencode.json'
            profile.parent.mkdir()
            profile.write_text('{"personal": "keep"}\n')
            env = dict(os.environ, HOME=str(home), PATH=str(commands) + ':' + os.environ['PATH'],
                       TEST_LOG=str(log), TEST_FAILURE=failure)
            result = subprocess.run(['bash', str(ROOT / 'scripts/repair-opencode.sh')],
                                    env=env, capture_output=True, text=True)
            lines = log.read_text().splitlines()
            self.assertEqual(profile.read_text(), '{"personal": "keep"}\n')
            backups = list((home / '.local/state/gran/opencode-backups').iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual((backups[0] / '.config/mise/config.toml').read_text(), config.read_text())
            if failure:
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('unuse -g --no-prune npm:opencode-ai', lines)
                self.assertEqual((runtime / 'bin/gran-update').read_text(), '# old updater\n')
            else:
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(lines, [
                    'use -g aqua:anomalyco/opencode@latest',
                    'exec aqua:anomalyco/opencode -- opencode --version',
                    'unuse -g --no-prune npm:opencode-ai',
                    'reshim',
                    'exec -- opencode --version',
                    'plain opencode --version',
                ])
                self.assertEqual((backups[0] / '.local/share/gran/bin/gran-update').read_text(), '# old updater\n')
                self.assertIn('gran-opencode-install', (runtime / 'bin/gran-update').read_text())
                self.assertTrue((runtime / 'bin/gran-opencode-install').is_file())
                self.assertIn('check opencode --version', (runtime / 'bin/gran-doctor').read_text())

    def test_repair_switches_backend_only_after_binary_runs_and_updates_runtime(self):
        self.run_repair()

    def test_download_failure_preserves_previous_tool_request_and_runtime(self):
        self.run_repair('use -g aqua:anomalyco/opencode@latest')

    def test_broken_replacement_preserves_previous_tool_request_and_runtime(self):
        self.run_repair('exec aqua:anomalyco/opencode -- opencode --version')


class AutomaticToolInstallationTests(unittest.TestCase):
    def install_stage(self, failure=''):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            # Run the actual deployed helper, as stage 3 of install.sh does.
            subprocess.run(['python', str(ROOT / 'scripts/apply-home.py'), '--home', str(home)],
                           check=True, capture_output=True)
            commands = home / 'fake-bin'
            commands.mkdir()
            (commands / 'mise').write_text('''#!/bin/bash
printf 'mise %s\n' "$*" >> "$TEST_LOG"
case "$1" in
  use)
    [[ $3 != aqua:* ]] || touch "$HOME/native-installed" ;;
  exec)
    if [[ $2 == aqua:* ]]; then
      TEST_NATIVE=1 opencode --version
    else
      opencode --version
    fi ;;
  unuse) touch "$HOME/legacy-retired" ;;
  reshim) touch "$HOME/shims-ready" ;;
  *) exit 9 ;;
esac
''')
            (commands / 'opencode').write_text('''#!/bin/bash
printf 'opencode native=%s %s\n' "${TEST_NATIVE:-0}" "$*" >> "$TEST_LOG"
if [[ ${TEST_NATIVE:-0} == 1 ]]; then
  [[ $TEST_FAILURE != native && -e $HOME/native-installed ]] || exit 23
else
  [[ $TEST_FAILURE != plain && -e $HOME/legacy-retired && -e $HOME/shims-ready ]] || exit 24
fi
printf '2.2.5\n'
''')
            for command in commands.iterdir():
                command.chmod(0o755)
            log = home / 'calls.log'
            env = dict(os.environ, HOME=str(home), GRAN_PATH=str(home / '.local/share/gran'),
                       PATH=str(commands) + ':' + str(home / '.local/share/gran/bin') + ':' + os.environ['PATH'],
                       TEST_FAILURE=failure, TEST_LOG=str(log))
            result = subprocess.run(['bash', str(ROOT / 'scripts/install-tools.sh')],
                                    env=env, capture_output=True, text=True)
            lines = log.read_text().splitlines()
            self.assertIn('mise use -g node@lts', lines)
            self.assertIn('mise use -g npm:@openai/codex@latest', lines)
            self.assertIn('mise use -g aqua:anomalyco/opencode@latest', lines)
            self.assertNotIn('mise use -g npm:opencode-ai@latest', lines)
            if failure:
                self.assertNotEqual(result.returncode, 0)
                if failure == 'native':
                    self.assertFalse((home / 'legacy-retired').exists())
            else:
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('2.2.5', result.stdout)
                self.assertEqual(lines[-1], 'opencode native=0 --version')
                self.assertTrue((home / 'shims-ready').is_file())

    def test_install_stage_prepares_a_working_plain_opencode_command(self):
        self.install_stage()

    def test_install_stage_aborts_when_the_release_binary_does_not_run(self):
        self.install_stage('native')

    def test_install_stage_aborts_when_only_mise_exec_works(self):
        self.install_stage('plain')

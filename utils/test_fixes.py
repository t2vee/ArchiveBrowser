from download_tests import SystemCheck
from utils import Logger

tests = SystemCheck()
log = Logger()

class TestFixes:

    log.info("Starting first time system check...")

    self.trigger_tests = tests.run_all()

    def format_result(self, result):
        return "Success" if result else "Failed"


    results = [
        f"Disk Space: {format_result(tests.disk_space)}",
        f"Internet Connection: {format_result(tests.connected)}",
        f"Compatible OS: {format_result(tests.os)}",
        f"Jigdo Command: {format_result(tests.jigdo)}",
        f"Valid Json Config: {format_result(tests.json)}",
    ]
    log.info("========================= ! IMPORTANT ! =========================")
    log.info("Results of the System Check:")
    pass_or_fail = []
    for result in results:
        log.fail(result) and pass_or_fail.append(False) if "Failed" in result else log.success(result) and pass_or_fail.append(True)
    log.info("========================= ! IMPORTANT ! =========================")
    if pass_or_fail.count(True) < pass_or_fail.count(False):
        log.warn("There were one or more failures")
        log.warn("Attempting to automatically fix...")

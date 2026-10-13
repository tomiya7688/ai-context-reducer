import unittest
from src.report import Report, render_report

class ReportTests(unittest.TestCase):
    def test_render_report_adds_heading(self):
        report = Report("Daily", ["one", "two"])
        self.assertEqual("# Daily\n\none\ntwo\n", render_report(report))

if __name__ == "__main__":
    unittest.main()

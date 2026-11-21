import os
import unittest
from datetime import date
from importlib.resources import files

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QDate, QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QApplication, QLabel, QPushButton

from calendar_weeks.calendar import (
    CalendarWindow,
    bottom_right_position,
    week_number_for_date,
)


class WeekNumberTests(unittest.TestCase):
    def test_week_number_uses_iso_week_across_year_boundary(self) -> None:
        self.assertEqual(week_number_for_date(date(2021, 1, 1)), 53)

    def test_week_number_updates_for_first_iso_week(self) -> None:
        self.assertEqual(week_number_for_date(date(2021, 1, 4)), 1)


class WindowPositionTests(unittest.TestCase):
    def test_positions_window_above_taskbar_at_bottom_right(self) -> None:
        position = bottom_right_position(QRect(100, 50, 1920, 1080), QSize(360, 430))
        self.assertEqual(position, QPoint(1644, 684))


class CalendarWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])
        stylesheet = files("calendar_weeks").joinpath("style.qss").read_text(encoding="utf-8")
        cls.app.setStyleSheet(stylesheet)

    def test_custom_close_button_hides_frameless_window(self) -> None:
        window = CalendarWindow()
        window.show()
        self.app.processEvents()

        self.assertTrue(window.windowFlags() & Qt.WindowType.FramelessWindowHint)
        self.assertTrue(window.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))
        main_container = window.centralWidget()
        self.assertEqual(main_container.objectName(), "MainContainer")
        self.assertTrue(
            main_container.testAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        )
        rendered = window.grab().toImage()
        self.assertEqual(rendered.pixelColor(0, 0).alpha(), 0)
        self.assertEqual(
            rendered.pixelColor(rendered.width() // 2, rendered.height() // 2).alpha(),
            255,
        )
        self.assertFalse(window.windowIcon().isNull())
        self.assertEqual(window.week_caption_label.text(), "WEEK")
        window_icon = window.findChild(QLabel, "WindowIcon")
        self.assertIsNotNone(window_icon)
        self.assertEqual(window_icon.pixmap().size(), QSize(36, 36))
        buttons = window.findChildren(QPushButton)
        self.assertEqual(len(buttons), 2)
        close_button = window.findChild(QPushButton, "CloseButton")
        self.assertIsNotNone(close_button)
        self.assertFalse(close_button.icon().isNull())
        self.assertEqual(close_button.iconSize(), QSize(16, 16))
        today_button = window.findChild(QPushButton, "TodayButton")
        self.assertIsNotNone(today_button)
        self.assertFalse(today_button.icon().isNull())
        self.assertEqual(today_button.iconSize(), QSize(16, 16))

        window.calendar.setSelectedDate(QDate(2021, 1, 1))
        self.app.processEvents()
        self.assertEqual(window.day_value_label.text(), "1")
        self.assertEqual(window.week_value_label.text(), "53")

        close_button.click()
        self.app.processEvents()
        self.assertFalse(window.isVisible())
        self.assertEqual(window.calendar.selectedDate(), QDate.currentDate())
        self.assertEqual(window.day_value_label.text(), str(date.today().day))
        self.assertEqual(window.week_value_label.text(), str(week_number_for_date(date.today())))

        window.show_at_bottom_right()
        window.calendar.setSelectedDate(QDate(2021, 1, 1))
        self.app.processEvents()
        self.assertTrue(window.isVisible())
        screen = window.screen()
        self.assertIsNotNone(screen)
        self.assertEqual(
            window.pos(),
            bottom_right_position(screen.availableGeometry(), window.size()),
        )
        self.assertEqual(window.day_value_label.text(), "1")
        self.assertEqual(window.week_value_label.text(), "53")
        today_button.click()
        self.app.processEvents()
        self.assertEqual(window.calendar.selectedDate(), QDate.currentDate())
        self.assertEqual(window.day_value_label.text(), str(date.today().day))
        self.assertEqual(window.week_value_label.text(), str(week_number_for_date(date.today())))
        window.hide()
        window.deleteLater()


if __name__ == "__main__":
    unittest.main()

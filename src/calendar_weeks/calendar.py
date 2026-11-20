from __future__ import annotations

import sys
from datetime import date
from importlib.resources import files
from pathlib import Path

from PySide6.QtCore import QDate, QLocale, QPoint, QRect, QSize, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QMouseEvent, QTextCharFormat
from PySide6.QtWidgets import (
    QApplication,
    QCalendarWidget,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

ICON_PATH = Path(__file__).parent / "calendar_icon_tray.png"
CLOSE_ICON_PATH = Path(__file__).parent / "cerrar2.png"
BUTTON_REFRESH_PATH = Path(__file__).parent / "actualizar.png"


def week_number_for_date(selected_date: date) -> int:
    return selected_date.isocalendar().week


def bottom_right_position(
    available_geometry: QRect,
    window_size: QSize,
    margin: int = 16,
) -> QPoint:
    x = available_geometry.x() + max(
        0,
        available_geometry.width() - window_size.width() - margin,
    )
    y = available_geometry.y() + max(
        0,
        available_geometry.height() - window_size.height() - margin,
    )
    return QPoint(x, y)


class TitleBar(QWidget):
    def __init__(self, window: QMainWindow) -> None:
        super().__init__(window)
        self.setObjectName("TitleBar")
        self._drag_offset: QPoint | None = None

        icon_label = QLabel()
        icon_label.setObjectName("WindowIcon")
        icon_label.setPixmap(window.windowIcon().pixmap(36, 36))

        title_label = QLabel(window.windowTitle())
        title_label.setObjectName("WindowTitle")

        close_button = QPushButton()
        close_button.setObjectName("CloseButton")
        close_button.setIcon(QIcon(str(CLOSE_ICON_PATH)))
        close_button.setIconSize(QSize(16, 16))
        close_button.setFixedSize(32, 28)
        close_button.setToolTip("Ocultar en la bandeja")
        close_button.clicked.connect(window.hide_to_tray)

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 4, 8, 4)
        layout.setSpacing(8)
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(close_button)
        self.setLayout(layout)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = (
                event.globalPosition().toPoint()
                - self.window().frameGeometry().topLeft()
            )
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if (
            self._drag_offset is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.window().move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_offset = None
        super().mouseReleaseEvent(event)


class CalendarWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setObjectName("MainWindow")
        self.setWindowTitle("Calendar Weeks")
        self.setWindowIcon(QIcon(str(ICON_PATH)))

        self.day_caption_label = QLabel("DÍA")
        self.day_caption_label.setObjectName("DayCaption")
        self.day_value_label = QLabel()
        self.day_value_label.setObjectName("DayValue")
        self.week_caption_label = QLabel("WEEK")
        self.week_caption_label.setObjectName("WeekCaption")
        self.week_value_label = QLabel()
        self.week_value_label.setObjectName("WeekValue")
        self.today_button_icon = QIcon(str(BUTTON_REFRESH_PATH))
        self.today_button = QPushButton()
        self.today_button.setIcon(self.today_button_icon)
        self.today_button.setIconSize(QSize(16, 16))
        self.today_button.setObjectName("TodayButton")
        self.today_button.setToolTip("Return to today's date")
        self.today_button.clicked.connect(self.reset_to_today)

        self.calendar = QCalendarWidget()
        self.calendar.setLocale(
            QLocale(QLocale.Language.Spanish, QLocale.Country.Spain)
        )
        self.calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        self.calendar.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.ISOWeekNumbers
        )
        self.calendar.setGridVisible(False)
        self.calendar.setWeekdayTextFormat(
            Qt.DayOfWeek.Saturday,
            self.weekday_format("#E06C75"),
        )
        self.calendar.setWeekdayTextFormat(
            Qt.DayOfWeek.Sunday,
            self.weekday_format("#E06C75"),
        )
        for day in (
            Qt.DayOfWeek.Monday,
            Qt.DayOfWeek.Tuesday,
            Qt.DayOfWeek.Wednesday,
            Qt.DayOfWeek.Thursday,
            Qt.DayOfWeek.Friday,
        ):
            self.calendar.setWeekdayTextFormat(day, self.weekday_format("#6B7280"))
        self.calendar.selectionChanged.connect(self.update_date_display)
        self.calendar.setSelectedDate(QDate.currentDate())

        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(14, 8, 14, 8)
        status_layout.setSpacing(8)
        status_layout.addWidget(self.day_caption_label)
        status_layout.addWidget(self.day_value_label)
        status_layout.addStretch()
        status_layout.addWidget(self.week_caption_label)
        status_layout.addWidget(self.week_value_label)
        status_layout.addSpacing(12)
        status_layout.addWidget(self.today_button)

        self.status_card = QFrame()
        self.status_card.setObjectName("StatusCard")
        self.status_card.setLayout(status_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(10)
        layout.addWidget(TitleBar(self))
        layout.addWidget(self.status_card)
        layout.addWidget(self.calendar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.update_date_display()
        self.setMinimumSize(320, 400)
        self.resize(360, 430)

    @staticmethod
    def weekday_format(color: str) -> QTextCharFormat:
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color))
        return text_format

    def update_date_display(self) -> None:
        selected_date = self.calendar.selectedDate().toPython()
        self.day_value_label.setText(str(selected_date.day))
        self.week_value_label.setText(str(week_number_for_date(selected_date)))

    def reset_to_today(self) -> None:
        today = QDate.currentDate()
        self.calendar.setCurrentPage(today.year(), today.month())
        self.calendar.setSelectedDate(today)
        self.update_date_display()

    def hide_to_tray(self) -> None:
        self.reset_to_today()
        self.hide()

    def show_at_bottom_right(self) -> None:
        screen = self.screen() or QApplication.primaryScreen()
        if screen is None:
            raise RuntimeError(
                "No se encontró una pantalla para mostrar el calendario."
            )
        self.showNormal()
        self.move(bottom_right_position(screen.availableGeometry(), self.size()))
        self.raise_()
        self.activateWindow()


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Calendar Weeks")
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet(
        files("calendar_weeks").joinpath("style.qss").read_text(encoding="utf-8")
    )

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(
            None, "Calendar Weeks", "No se encontró el área de notificación de Windows."
        )
        return 1

    window = CalendarWindow()
    app_icon = QIcon(str(ICON_PATH))
    tray_icon = QSystemTrayIcon(app_icon, app)
    tray_icon.setToolTip("Calendar Weeks")

    menu = QMenu()
    open_action = QAction("Open", menu)
    open_action.triggered.connect(window.show_at_bottom_right)
    menu.addAction(open_action)
    menu.addSeparator()
    exit_action = QAction("Exit", menu)
    exit_action.triggered.connect(app.quit)
    menu.addAction(exit_action)

    tray_icon.setContextMenu(menu)
    tray_icon.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

from pathlib import Path

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QApplication, QFileDialog
from loguru import logger

from .converter import convert, read, write


class ScheduleIO(QObject):
    def __init__(self, parent):
        super().__init__()
        self.manager = parent

    @Slot(str, result=bool)
    def exportToCSES(self, filename: str) -> bool:
        """Export current CW2 schedule to CSES YAML file."""
        try:
            path = self.manager.schedules_dir / f"{filename}.json"
            default_name = path.stem + ".yaml"
            output_path, _ = QFileDialog.getSaveFileName(
                None,
                QApplication.translate("ExportScheduleDialog", "Export Schedule"),
                default_name,
                QApplication.translate(
                    "ExportScheduleDialog", "CSES Format (*.yaml *.yml)"
                ),
            )
            if not output_path:
                return False
            convert(path, "cw2", Path(output_path), "cses")
            logger.success(f"Exported schedule to {output_path}")
            return True
        except Exception as e:
            logger.exception(f"Export failed: {e}")
            return False

    def _import_as_cw2(
        self,
        format_id: str,
        dialog_title: str,
        file_filter: str,
        output_suffix: str,
    ) -> bool:
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            dialog_title,
            str(self.manager.schedules_dir),
            file_filter,
        )
        if not file_path:
            logger.info("User cancelled import.")
            return False

        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"Selected file does not exist: {file_path}")
                return False

            schedule = read(path, format_id)
            dest_path = self.manager.schedules_dir / f"{path.stem} - {output_suffix}.json"
            write(schedule, dest_path, "cw2")

            self.manager.schedule = schedule
            self.manager.current_schedule_name = dest_path.stem
            self.manager.schedule_path = dest_path

            self.manager.save()
            self.manager.scheduleSwitched.emit(self.manager.schedule)
            self.manager.scheduleModified.emit(self.manager.schedule)

            logger.success(f"Imported {format_id.upper()} schedule from {file_path}")
            return True
        except Exception as e:
            logger.exception(f"Import failed: {e}")
            return False

    @Slot(result=bool)
    def importCSES(self) -> bool:
        """Import a CSES schedule and convert it to CW2."""
        return self._import_as_cw2(
            format_id="cses",
            dialog_title=QApplication.translate(
                "ImportScheduleDialog", "Import CSES Schedule"
            ),
            file_filter=QApplication.translate(
                "ImportScheduleDialog", "CSES YAML Files (*.yaml *.yml)"
            ),
            output_suffix="CSES",
        )

    @Slot(result=bool)
    def importCW1(self) -> bool:
        """Import a Class Widgets 1 schedule and convert it to CW2."""
        return self._import_as_cw2(
            format_id="cw1",
            dialog_title=QApplication.translate(
                "ImportScheduleDialog", "Import Class Widgets 1 Schedule"
            ),
            file_filter=QApplication.translate(
                "ImportScheduleDialog", "Class Widgets 1 JSON Files (*.json)"
            ),
            output_suffix="CW1",
        )

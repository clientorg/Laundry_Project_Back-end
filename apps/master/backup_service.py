import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
import zipfile

from django.conf import settings


class DatabaseBackupService:

    @classmethod
    def get_app_dir(cls):
        """
        Directory containing launcher.exe in packaged application.

        Example:
            C:/Laundry/db
        """
        import sys

        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent

        # Development fallback.
        # Adjust this if your Django project has a different structure.
        return Path(settings.BASE_DIR).resolve()

    @classmethod
    def get_db_bin(cls):
        return cls.get_app_dir() / "windows" / "bin"

    @classmethod
    def get_backup_dir(cls):
        """
        Backup directory is ../backup relative to db/.
        """
        return cls.get_app_dir().parent / "backup"

    @classmethod
    def get_mysql(cls):
        return cls.get_db_bin() / "mariadb.exe"

    @classmethod
    def get_mysql_dump(cls):
        return cls.get_db_bin() / "mariadb-dump.exe"

    @classmethod
    def get_database_config(cls):
        return {
            "host": getattr(settings, "DB_BACKUP_HOST", "127.0.0.1"),
            "port": str(getattr(settings, "DB_BACKUP_PORT", 3307)),
            "name": getattr(settings, "DB_BACKUP_NAME", "laundry"),
            "user": getattr(settings, "DB_BACKUP_USER", "root"),
            "password": getattr(settings, "DB_BACKUP_PASSWORD", ""),
        }

    @classmethod
    def ensure_backup_directory(cls):
        backup_dir = cls.get_backup_dir()
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir

    @classmethod
    def check_database(cls):
        config = cls.get_database_config()
        mysql = cls.get_mysql()

        if not mysql.exists():
            raise RuntimeError(f"MariaDB executable not found: {mysql}")

        command = [
            str(mysql),
            "-h",
            config["host"],
            "-P",
            config["port"],
            "-u",
            config["user"],
        ]

        if config["password"]:
            command.append(f"-p{config['password']}")

        command.extend(
            [
                config["name"],
                "-e",
                "SELECT 1;",
            ]
        )

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Database connection failed.")

        return True

    @classmethod
    def create_backup(cls):
        config = cls.get_database_config()

        cls.check_database()

        backup_dir = cls.ensure_backup_directory()
        mysql_dump = cls.get_mysql_dump()

        if not mysql_dump.exists():
            raise RuntimeError(f"MariaDB dump executable not found: {mysql_dump}")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        base_name = f"{config['name']}_{timestamp}"

        sql_file = backup_dir / f"{base_name}.sql"
        zip_file = backup_dir / f"{base_name}.zip"

        command = [
            str(mysql_dump),
            "-h",
            config["host"],
            "-P",
            config["port"],
            "-u",
            config["user"],
            "--routines",
            "--events",
            "--triggers",
            config["name"],
        ]

        if config["password"]:
            command.insert(4, f"-p{config['password']}")

        try:
            with open(sql_file, "w", encoding="utf-8") as output:
                result = subprocess.run(
                    command,
                    stdout=output,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=getattr(
                        subprocess,
                        "CREATE_NO_WINDOW",
                        0,
                    ),
                )

            if result.returncode != 0:
                if sql_file.exists():
                    sql_file.unlink()

                raise RuntimeError(result.stderr.strip() or "Database backup failed.")

            # Compress SQL backup
            with zipfile.ZipFile(
                zip_file,
                "w",
                compression=zipfile.ZIP_DEFLATED,
            ) as archive:
                archive.write(
                    sql_file,
                    arcname=sql_file.name,
                )

            # Remove temporary SQL
            sql_file.unlink(missing_ok=True)

            return cls.get_backup_details(zip_file)

        except Exception:
            sql_file.unlink(missing_ok=True)
            zip_file.unlink(missing_ok=True)
            raise

    @classmethod
    def list_backups(cls):
        backup_dir = cls.ensure_backup_directory()

        backups = []

        for file in backup_dir.iterdir():

            if not file.is_file():
                continue

            if file.suffix.lower() not in {".zip", ".sql"}:
                continue

            stat = file.stat()

            backups.append(
                {
                    "name": file.name,
                    "size": stat.st_size,
                    "size_mb": round(
                        stat.st_size / (1024 * 1024),
                        2,
                    ),
                    "created_at": datetime.fromtimestamp(stat.st_mtime).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            )

        backups.sort(
            key=lambda item: item["created_at"],
            reverse=True,
        )

        return backups

    @classmethod
    def get_backup_file(cls, filename):
        backup_dir = cls.ensure_backup_directory()

        # Security: only allow filenames, never paths.
        safe_name = Path(filename).name

        if safe_name != filename:
            raise ValueError("Invalid backup filename.")

        backup_file = backup_dir / safe_name

        if not backup_file.exists():
            raise FileNotFoundError(f"Backup not found: {filename}")

        if not backup_file.is_file():
            raise ValueError("Invalid backup file.")

        if backup_file.suffix.lower() not in {".zip", ".sql"}:
            raise ValueError("Invalid backup file type.")

        return backup_file

    @classmethod
    def restore_backup(cls, filename):
        config = cls.get_database_config()

        cls.check_database()

        backup_file = cls.get_backup_file(filename)
        mysql = cls.get_mysql()

        temp_dir = None
        sql_file = backup_file

        try:

            if backup_file.suffix.lower() == ".zip":

                temp_dir = Path(tempfile.mkdtemp(prefix="laundry_restore_"))

                with zipfile.ZipFile(
                    backup_file,
                    "r",
                ) as archive:

                    members = archive.namelist()

                    sql_members = [
                        member for member in members if member.lower().endswith(".sql")
                    ]

                    if not sql_members:
                        raise RuntimeError("No SQL file found inside backup.")

                    # Prevent ZIP path traversal
                    for member in members:
                        target = (temp_dir / member).resolve()

                        if not str(target).startswith(str(temp_dir.resolve())):
                            raise RuntimeError("Invalid backup archive.")

                    archive.extractall(temp_dir)

                    sql_file = temp_dir / sql_members[0]

            command = [
                str(mysql),
                "-h",
                config["host"],
                "-P",
                config["port"],
                "-u",
                config["user"],
            ]

            if config["password"]:
                command.append(f"-p{config['password']}")

            command.extend(
                [
                    config["name"],
                ]
            )

            with open(
                sql_file,
                "r",
                encoding="utf-8",
                errors="replace",
            ) as sql:

                result = subprocess.run(
                    command,
                    stdin=sql,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=getattr(
                        subprocess,
                        "CREATE_NO_WINDOW",
                        0,
                    ),
                )

            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or "Database restore failed.")

            return True

        finally:

            if temp_dir and temp_dir.exists():
                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True,
                )

    @classmethod
    def delete_backup(cls, filename):
        backup_file = cls.get_backup_file(filename)

        backup_file.unlink()

        return True

    @classmethod
    def get_backup_details(cls, file):
        stat = file.stat()

        return {
            "name": file.name,
            "size": stat.st_size,
            "size_mb": round(
                stat.st_size / (1024 * 1024),
                2,
            ),
            "created_at": datetime.fromtimestamp(stat.st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

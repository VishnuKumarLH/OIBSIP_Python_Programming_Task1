import sqlite3
import logging
import re
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.interval import IntervalTrigger
import os

logger = logging.getLogger(__name__)

class ReminderSkill:
   
    def __init__(self):
        """Initialize the reminder skill."""
        self.db_path = 'reminders.db'
        self.scheduler = None
        self._init_db()
        self._init_scheduler()

    def _init_db(self):
       
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create reminders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    scheduled_time TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'scheduled'
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("Reminder database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize reminder database: {e}")

    def _init_scheduler(self):
       
        try:
            # Configure job stores
            jobstores = {
                'default': MemoryJobStore()
            }

            # Configure executors
            executors = {
                'default': AsyncIOExecutor()
            }

            # Configure job defaults
            job_defaults = {
                'coalesce': True,
                'max_instances': 1
            }

            self.scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults
            )

            # Note: APScheduler 3.10.4 starts automatically when instantiated
            logger.info("Reminder scheduler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {e}")

    def set_reminder(self, text, minutes=None, hours=None):
      
        if not text or not text.strip():
            return False, "Reminder text cannot be empty", None

        try:
            # Calculate reminder time
            now = datetime.now()
            if minutes:
                reminder_time = now + timedelta(minutes=minutes)
            elif hours:
                reminder_time = now + timedelta(hours=hours)
            else:
                return False, "Please specify either minutes or hours for the reminder", None

            # Store reminder in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO reminders (text, scheduled_time, status)
                VALUES (?, ?, ?)
            ''', (text, reminder_time.isoformat(), 'scheduled'))

            reminder_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Schedule the reminder
            self.scheduler.add_job(
                func=self._trigger_reminder,
                trigger='date',
                run_date=reminder_time,
                args=[reminder_id, text],
                id=str(reminder_id),
                replace_existing=True
            )

            logger.info(f"Reminder set for {reminder_time}: {text}")
            return True, f"Reminder set for {reminder_time.strftime('%I:%M %p')}: {text}", reminder_id

        except Exception as e:
            logger.error(f"Failed to set reminder: {e}")
            return False, f"Failed to set reminder: {str(e)}", None

    def _trigger_reminder(self, reminder_id, text):
       
        try:
            logger.info(f"Reminder triggered: {text}")

            # Update reminder status in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE reminders SET status = ? WHERE id = ?', ('triggered', reminder_id))
            conn.commit()
            conn.close()

            # Here you would typically integrate with TTS to speak the reminder
            # For now, we'll just log it
            print(f"\n🔔 REMINDER: {text}\n")

        except Exception as e:
            logger.error(f"Failed to trigger reminder {reminder_id}: {e}")

    def list_reminders(self):
      
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, text, scheduled_time, status, created_at
                FROM reminders
                ORDER BY scheduled_time DESC
            ''')

            reminders = []
            for row in cursor.fetchall():
                reminder = {
                    'id': row[0],
                    'text': row[1],
                    'scheduled_time': row[2],
                    'status': row[3],
                    'created_at': row[4]
                }
                reminders.append(reminder)

            conn.close()
            return reminders

        except Exception as e:
            logger.error(f"Failed to list reminders: {e}")
            return []

    def cancel_reminder(self, reminder_id):
      
        try:
            # Remove from scheduler
            if self.scheduler.get_job(str(reminder_id)):
                self.scheduler.remove_job(str(reminder_id))

            # Update status in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE reminders SET status = ? WHERE id = ?', ('cancelled', reminder_id))
            conn.commit()
            conn.close()

            logger.info(f"Reminder {reminder_id} cancelled")
            return True, f"Reminder {reminder_id} cancelled successfully"

        except Exception as e:
            logger.error(f"Failed to cancel reminder {reminder_id}: {e}")
            return False, f"Failed to cancel reminder: {str(e)}"

    def cleanup_old_reminders(self, days=7):
       
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM reminders WHERE status != ? AND scheduled_time < ?',
                         ('scheduled', cutoff_date.isoformat()))

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old reminders")

        except Exception as e:
            logger.error(f"Failed to cleanup old reminders: {e}")

    def shutdown(self):
       
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Reminder scheduler shutdown")

    def parse_time_expression(self, time_expr):
        
        try:
            now = datetime.now()

            # Handle "in X minutes/hours/days"
            in_match = re.search(r'in\s+(\d+)\s+(minute|hour|day)s?', time_expr.lower())
            if in_match:
                amount = int(in_match.group(1))
                unit = in_match.group(2)

                if unit.startswith('minute'):
                    return now + timedelta(minutes=amount)
                elif unit.startswith('hour'):
                    return now + timedelta(hours=amount)
                elif unit.startswith('day'):
                    return now + timedelta(days=amount)

            # Handle "tomorrow at TIME"
            tomorrow_match = re.search(r'tomorrow\s+at\s+(\d+)(?::(\d+))?\s*(am|pm)?', time_expr.lower())
            if tomorrow_match:
                hour = int(tomorrow_match.group(1))
                minute = int(tomorrow_match.group(2)) if tomorrow_match.group(2) else 0
                am_pm = tomorrow_match.group(3)

                if am_pm:
                    if am_pm.lower() == 'pm' and hour != 12:
                        hour += 12
                    elif am_pm.lower() == 'am' and hour == 12:
                        hour = 0

                tomorrow = now + timedelta(days=1)
                return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Handle "today at TIME"
            today_match = re.search(r'today\s+at\s+(\d+)(?::(\d+))?\s*(am|pm)?', time_expr.lower())
            if today_match:
                hour = int(today_match.group(1))
                minute = int(today_match.group(2)) if today_match.group(2) else 0
                am_pm = today_match.group(3)

                if am_pm:
                    if am_pm.lower() == 'pm' and hour != 12:
                        hour += 12
                    elif am_pm.lower() == 'am' and hour == 12:
                        hour = 0

                return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Handle "next week"
            if 'next week' in time_expr.lower():
                return now + timedelta(weeks=1)

            # Handle "next month"
            if 'next month' in time_expr.lower():
                return now + timedelta(days=30)  # Approximate

            return None

        except Exception as e:
            logger.error(f"Failed to parse time expression '{time_expr}': {e}")
            return None

    def set_reminder_advanced(self, text, time_expr=None, minutes=None, hours=None, days=None, recurring=None):
       
        if not text or not text.strip():
            return False, "Reminder text cannot be empty", None

        try:
            # Calculate reminder time
            now = datetime.now()
            reminder_time = None

            if time_expr:
                reminder_time = self.parse_time_expression(time_expr)
                if not reminder_time:
                    return False, f"I couldn't understand the time expression '{time_expr}'", None
            elif minutes:
                reminder_time = now + timedelta(minutes=minutes)
            elif hours:
                reminder_time = now + timedelta(hours=hours)
            elif days:
                reminder_time = now + timedelta(days=days)
            else:
                return False, "Please specify when you want to be reminded", None

            # Store reminder in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO reminders (text, scheduled_time, status)
                VALUES (?, ?, ?)
            ''', (text, reminder_time.isoformat(), 'scheduled'))

            reminder_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Schedule the reminder
            if recurring:
                trigger = IntervalTrigger(**self._parse_recurring_interval(recurring))
                self.scheduler.add_job(
                    func=self._trigger_reminder,
                    trigger=trigger,
                    args=[reminder_id, text],
                    id=str(reminder_id),
                    replace_existing=True
                )
            else:
                self.scheduler.add_job(
                    func=self._trigger_reminder,
                    trigger='date',
                    run_date=reminder_time,
                    args=[reminder_id, text],
                    id=str(reminder_id),
                    replace_existing=True
                )

            logger.info(f"Reminder set for {reminder_time}: {text}")
            return True, f"Reminder set for {reminder_time.strftime('%I:%M %p')}: {text}", reminder_id

        except Exception as e:
            logger.error(f"Failed to set reminder: {e}")
            return False, f"Failed to set reminder: {str(e)}", None

    def _parse_recurring_interval(self, recurring):
       
        recurring = recurring.lower()

        if recurring == 'daily':
            return {'days': 1}
        elif recurring == 'weekly':
            return {'weeks': 1}
        elif recurring == 'monthly':
            return {'days': 30}

        # Handle "every X hours/days/minutes"
        match = re.search(r'every\s+(\d+)\s+(hour|day|minute)s?', recurring)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)

            if unit.startswith('hour'):
                return {'hours': amount}
            elif unit.startswith('day'):
                return {'days': amount}
            elif unit.startswith('minute'):
                return {'minutes': amount}

        return {'days': 1}  # Default to daily

    def cancel_reminder_by_text(self, text):
      
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Find matching reminders
            cursor.execute('SELECT id FROM reminders WHERE text LIKE ? AND status = ?',
                         (f'%{text}%', 'scheduled'))

            matching_reminders = cursor.fetchall()
            cancelled_count = 0

            for row in matching_reminders:
                reminder_id = row[0]
                # Remove from scheduler
                if self.scheduler.get_job(str(reminder_id)):
                    self.scheduler.remove_job(str(reminder_id))

                # Update status in database
                cursor.execute('UPDATE reminders SET status = ? WHERE id = ?', ('cancelled', reminder_id))
                cancelled_count += 1

            conn.commit()
            conn.close()

            if cancelled_count > 0:
                logger.info(f"Cancelled {cancelled_count} reminders matching '{text}'")
                return True, f"Cancelled {cancelled_count} reminders matching '{text}'", cancelled_count
            else:
                return False, f"No active reminders found matching '{text}'", 0

        except Exception as e:
            logger.error(f"Failed to cancel reminders by text: {e}")
            return False, f"Failed to cancel reminders: {str(e)}", 0

    def snooze_reminder(self, reminder_id, minutes=10):
      
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get current reminder
            cursor.execute('SELECT text, scheduled_time FROM reminders WHERE id = ?', (reminder_id,))
            row = cursor.fetchone()

            if not row:
                conn.close()
                return False, f"Reminder {reminder_id} not found"

            text, current_time_str = row
            current_time = datetime.fromisoformat(current_time_str)

            # Calculate new time
            new_time = datetime.now() + timedelta(minutes=minutes)

            # Update database
            cursor.execute('UPDATE reminders SET scheduled_time = ?, status = ? WHERE id = ?',
                         (new_time.isoformat(), 'scheduled', reminder_id))

            # Remove old job and add new one
            if self.scheduler.get_job(str(reminder_id)):
                self.scheduler.remove_job(str(reminder_id))

            self.scheduler.add_job(
                func=self._trigger_reminder,
                trigger='date',
                run_date=new_time,
                args=[reminder_id, text],
                id=str(reminder_id),
                replace_existing=True
            )

            conn.commit()
            conn.close()

            logger.info(f"Reminder {reminder_id} snoozed until {new_time}")
            return True, f"Reminder snoozed for {minutes} minutes until {new_time.strftime('%I:%M %p')}"

        except Exception as e:
            logger.error(f"Failed to snooze reminder {reminder_id}: {e}")
            return False, f"Failed to snooze reminder: {str(e)}"

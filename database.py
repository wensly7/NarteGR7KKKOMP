__all__ = [
    'verify_user',
    'get_all_professors',
    'get_professor_by_name',
    'get_professor_schedule',
    'update_professor_schedule',
    'update_professor',
    'update_professor_picture',
    'get_all_users',
    'add_user',
    'delete_user',
    'delete_professor',
    'close_db',
    'add_schedule',
    'delete_schedule',
    'get_schedules_by_day',
    'add_professor',
    'update_single_schedule'
]

import sqlite3
import os
import hashlib
import atexit

_db_connection = None
_SCHEMA_VERSION = 2  # Increment this when schema changes

def init_db():
    """Initialize the database with required tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Drop existing tables if they exist
        cursor.execute('DROP TABLE IF EXISTS schedules')
        cursor.execute('DROP TABLE IF EXISTS professors')
        cursor.execute('DROP TABLE IF EXISTS users')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        
        # Create professors table
        cursor.execute('''
            CREATE TABLE professors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                contact TEXT NOT NULL,
                email TEXT NOT NULL,
                picture TEXT
            )
        ''')
        
        # Create schedules table
        cursor.execute('''
            CREATE TABLE schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professor_id INTEGER NOT NULL,
                day TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                subject TEXT NOT NULL,
                FOREIGN KEY (professor_id) REFERENCES professors (id)
            )
        ''')
        
        # Add default admin user
        cursor.execute(
            'INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
            ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'admin@example.com', 'admin')
        )
        
        conn.commit()
        print("[DEBUG] Database initialized successfully")
        
    except Exception as e:
        print(f"[DEBUG] Error initializing database: {str(e)}")
        if conn:
            conn.rollback()

def get_db_connection():
    """Get a connection to the SQLite database
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    try:
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Set database path
        db_path = os.path.join('data', 'professor_checker.db')
        print(f"[DEBUG] Using database at: {db_path}")
        
        # Check if database exists
        db_exists = os.path.exists(db_path)
        if not db_exists:
            print("[DEBUG] Database does not exist, will initialize")
        
        # Create connection
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Enable foreign keys
        conn.execute('PRAGMA foreign_keys = ON')
        
        # Initialize database if it doesn't exist
        if not db_exists:
            init_db()
            
        return conn
        
    except Exception as e:
        print(f"[DEBUG] Error connecting to database: {str(e)}")
        return None

def _upgrade_database(conn, from_version):
    """Upgrade database schema"""
    cursor = conn.cursor()
    
    try:
        if from_version < 2:
            # Add contact and email columns
            cursor.execute('ALTER TABLE professors ADD COLUMN contact TEXT')
            cursor.execute('ALTER TABLE professors ADD COLUMN email TEXT')
            
            # Update existing professors with sample data
            sample_data = {
                'Dr. Charles Tabares': ('+63 912 345 6789', 'charles.tabares@university.edu'),
                'Dr. Wensley Naarte': ('+63 923 456 7890', 'wensley.naarte@university.edu'),
                'Mr. Brian Sarmiento': ('+63 934 567 8901', 'brian.sarmiento@university.edu'),
                'Dr. Maria Santos': ('+63 945 678 9012', 'maria.santos@university.edu'),
            }
            
            for name, (contact, email) in sample_data.items():
                cursor.execute('''
                    UPDATE professors 
                    SET contact = ?, email = ?
                    WHERE name = ?
                ''', (contact, email, name))
        
        # Update schema version
        cursor.execute('UPDATE schema_version SET version = ?', (_SCHEMA_VERSION,))
        conn.commit()
        print("[DEBUG] Database upgrade completed successfully")
        
    except Exception as e:
        print(f"[DEBUG] Error upgrading database: {str(e)}")
        conn.rollback()
        raise

def get_all_professors():
    """Get all professors from database"""
    try:
        print("[DEBUG] Attempting to get database connection")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("[DEBUG] Executing SELECT query on professors table")
        try:
            cursor.execute('SELECT * FROM professors ORDER BY name')
            professors = cursor.fetchall()
            
            if not professors:
                print("[DEBUG] No professors found in database")
                # Initialize database if empty
                init_db()
                cursor.execute('SELECT * FROM professors ORDER BY name')
                professors = cursor.fetchall()
            
            result = []
            for row in professors:  # Use professors instead of cursor.fetchall()
                prof_data = {
                    'id': row['id'] if 'id' in row.keys() else None,
                    'name': row['name'] if 'name' in row.keys() else 'N/A',
                    'department': row['department'] if 'department' in row.keys() else 'N/A',
                    'contact': row['contact'] if 'contact' in row.keys() else 'N/A',
                    'email': row['email'] if 'email' in row.keys() else 'N/A',
                    'picture': row['picture'] if 'picture' in row.keys() else None
                }
                result.append(prof_data)
                
            print(f"[DEBUG] Found {len(result)} professors")
            return result
            
        except sqlite3.OperationalError as e:
            if "no such table" in str(e).lower():
                print("[DEBUG] Professors table not found, initializing database")
                init_db()
                # Try again after initialization
                cursor.execute('SELECT * FROM professors ORDER BY name')
                professors = cursor.fetchall()
                return [dict(prof) for prof in professors]
            raise
            
    except Exception as e:
        print(f"[DEBUG] Error getting professors: {str(e)}")
        return []

def get_professor_by_name(name):
    """Get professor details by name"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM professors WHERE name = ?', (name,))
        row = cursor.fetchone()
        
        if row:
            # Convert sqlite3.Row to dictionary
            return {
                'id': row['id'],
                'name': row['name'],
                'department': row['department'] if 'department' in row.keys() else 'N/A',
                'contact': row['contact'] if 'contact' in row.keys() else 'N/A',
                'email': row['email'] if 'email' in row.keys() else 'N/A',
                'picture': row['picture'] if 'picture' in row.keys() else None
            }
        return None
        
    except Exception as e:
        print(f"[DEBUG] Error getting professor: {str(e)}")
        return None

def update_professor(professor_id, name, department, contact=None, email=None):
    """Update professor details
    
    Args:
        professor_id (int): ID of professor to update
        name (str): New name
        department (str): New department
        contact (str, optional): New contact number
        email (str, optional): New email
        
    Returns:
        bool: True if professor was updated successfully, False otherwise
    """
    try:
        if not professor_id or not name or not department:
            print("[DEBUG] Missing required fields")
            return False
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE professors 
            SET name = ?, department = ?, contact = ?, email = ?
            WHERE id = ?
        ''', (name, department, contact, email, professor_id))
        
        conn.commit()
        print(f"[DEBUG] Updated professor {name}")
        return True
        
    except Exception as e:
        print(f"[DEBUG] Error updating professor: {str(e)}")
        if conn:
            conn.rollback()
        return False

def get_professor_schedule(professor_id):
    """Get schedule for a specific professor
    
    Args:
        professor_id (int): ID of the professor
        
    Returns:
        list: List of schedule dictionaries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, p.name as professor_name 
            FROM schedules s
            JOIN professors p ON s.professor_id = p.id
            WHERE s.professor_id = ?
            ORDER BY s.day, s.start_time
        ''', (professor_id,))
        
        schedules = []
        for row in cursor.fetchall():
            schedule = {
                'id': row['id'],
                'professor_id': row['professor_id'],
                'professor_name': row['professor_name'],
                'day': row['day'],
                'start_time': row['start_time'],
                'end_time': row['end_time'],
                'subject': row['subject']
            }
            schedules.append(schedule)
            
        print(f"[DEBUG] Found {len(schedules)} schedules for professor {professor_id}")
        return schedules
        
    except Exception as e:
        print(f"[DEBUG] Error getting professor schedule: {str(e)}")
        return []

def close_db():
    """Close the database connection"""
    try:
        if _db_connection:
            _db_connection.close()
            print("[DEBUG] Database connection closed")
            
    except Exception as e:
        print(f"[DEBUG] Error closing database: {str(e)}")

def update_professor_schedule(professor_name, schedules):
    """Update professor's schedule"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get professor ID
        cursor.execute('SELECT id FROM professors WHERE name = ?', (professor_name,))
        prof_row = cursor.fetchone()
        
        if not prof_row:
            print(f"[DEBUG] Professor {professor_name} not found")
            return False
            
        # Begin transaction
        cursor.execute('BEGIN TRANSACTION')
        
        # Delete existing schedules
        cursor.execute('DELETE FROM schedules WHERE professor_id = ?', (prof_row['id'],))
        
        # Insert new schedules
        for schedule in schedules:
            cursor.execute('''
                INSERT INTO schedules (professor_id, day, start_time, end_time, subject)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                prof_row['id'],
                schedule['day'],
                schedule['start_time'],
                schedule['end_time'],
                schedule.get('subject', 'N/A')
            ))
        
        # Commit transaction
        conn.commit()
        return True
        
    except Exception as e:
        print(f"[DEBUG] Error updating schedule: {str(e)}")
        conn.rollback()
        return False

def verify_user(username, password):
    """Verify user credentials"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Hash the provided password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Check credentials
        cursor.execute(
            'SELECT role FROM users WHERE username = ? AND password = ?',
            (username, hashed_password)
        )
        
        row = cursor.fetchone()
        if row:
            return True, row['role']
        return False, None
        
    except Exception as e:
        print(f"[DEBUG] Error verifying user: {str(e)}")
        return False, None

def get_all_users():
    """Get all users from database
    
    Returns:
        list: List of user dictionaries containing id, username, email, and role
    """
    try:
        conn = get_db_connection()
        if not conn:
            print("[DEBUG] Failed to get database connection")
            return []
            
        cursor = conn.cursor()
        print("[DEBUG] Getting all users from database")
        
        try:
            cursor.execute('''
                SELECT id, username, email, role 
                FROM users 
                ORDER BY username
            ''')
            
            users = []
            for row in cursor.fetchall():
                user = {
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'role': row['role']
                }
                users.append(user)
                print(f"[DEBUG] Found user: {user['username']} ({user['email']})")
                
            print(f"[DEBUG] Total users found: {len(users)}")
            return users
            
        except sqlite3.OperationalError as e:
            if "no such table" in str(e).lower() or "no such column" in str(e).lower():
                print("[DEBUG] Users table needs initialization")
                init_db()
                # Try again after initialization
                cursor.execute('''
                    SELECT id, username, email, role 
                    FROM users 
                    ORDER BY username
                ''')
                
                users = []
                for row in cursor.fetchall():
                    user = {
                        'id': row['id'],
                        'username': row['username'],
                        'email': row['email'],
                        'role': row['role']
                    }
                    users.append(user)
                    print(f"[DEBUG] Found user: {user['username']} ({user['email']})")
                    
                print(f"[DEBUG] Total users found after init: {len(users)}")
                return users
            else:
                raise
            
    except Exception as e:
        print(f"[DEBUG] Error getting users: {str(e)}")
        return []

def add_user(username, password, email, role):
    """Add a new user
    
    Args:
        username (str): Username
        password (str): Password to hash and store
        email (str): User's email address
        role (str): User's role (admin/student)
        
    Returns:
        bool: True if user was added successfully, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            print(f"[DEBUG] Username {username} already exists")
            return False
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO users (username, password, email, role)
            VALUES (?, ?, ?, ?)
        ''', (username, hashed_password, email, role))
        
        conn.commit()
        print(f"[DEBUG] Added new user: {username}")
        return True
        
    except Exception as e:
        print(f"[DEBUG] Error adding user: {str(e)}")
        if conn:
            conn.rollback()
        return False

def delete_user(username):
    """Delete a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        
        conn.commit()
        print(f"[DEBUG] Deleted user: {username}")
        return True
        
    except Exception as e:
        print(f"[DEBUG] Error deleting user: {str(e)}")
        return False

def update_professor_picture(professor_name, picture_path):
    """Update professor's picture"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE professors 
            SET picture = ?
            WHERE name = ?
        ''', (picture_path, professor_name))
        
        conn.commit()
        print(f"[DEBUG] Updated picture for professor: {professor_name}")
        return True
        
    except Exception as e:
        print(f"[DEBUG] Error updating professor picture: {str(e)}")
        return False

def update_professor(old_name, new_name, department, contact, email, picture=None):
    """Update professor information
    
    Args:
        old_name (str): Current name of the professor
        new_name (str): New name for the professor
        department (str): Department
        contact (str): Contact information
        email (str): Email address
        picture (str, optional): Path to profile picture
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First check if the professor exists
        cursor.execute('SELECT picture FROM professors WHERE name = ?', (old_name,))
        result = cursor.fetchone()
        if not result:
            print(f"Professor {old_name} not found")
            return False
                
        # If we're changing the name, check if the new name already exists
        if old_name != new_name:
            cursor.execute('SELECT 1 FROM professors WHERE name = ?', (new_name,))
            if cursor.fetchone():
                print(f"Professor {new_name} already exists")
                return False
            
        # Get current picture path
        current_picture = result[0] if result[0] != "N/A" else None
        
        # If no new picture provided, keep the current one
        picture_path = picture if picture is not None else current_picture
        
        # Update professor information
        if old_name == new_name:
            # If name isn't changing, simple update
            cursor.execute('''
                UPDATE professors 
                SET department = ?, contact = ?, email = ?, picture = ?
                WHERE name = ?
            ''', (department, contact, email, picture_path, old_name))
        else:
            # If name is changing, we need to update schedules as well
            cursor.execute('''
                UPDATE professors 
                SET name = ?, department = ?, contact = ?, email = ?, picture = ?
                WHERE name = ?
            ''', (new_name, department, contact, email, picture_path, old_name))
            
            # Update related schedules
            cursor.execute('UPDATE schedules SET professor_id = (SELECT id FROM professors WHERE name = ?) WHERE professor_id = (SELECT id FROM professors WHERE name = ?)',
                         (new_name, old_name))
        
        conn.commit()
        if conn.total_changes > 0:
            return True
        else:
            print("No changes made to professor record")
            return False
                
    except Exception as e:
        print(f"Error updating professor: {e}")
        return False

def delete_professor(name):
    """Delete a professor and all associated schedules
    
    Args:
        name (str): Name of the professor to delete
        
    Returns:
        bool: True if professor was deleted successfully, False otherwise
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Start transaction
        conn.execute('BEGIN TRANSACTION')
        
        # Get professor ID first
        cursor.execute('SELECT id FROM professors WHERE name = ?', (name,))
        prof = cursor.fetchone()
        if not prof:
            print(f"[DEBUG] Professor {name} not found")
            return False
            
        prof_id = prof['id']
        
        # Delete associated schedules first
        cursor.execute('DELETE FROM schedules WHERE professor_id = ?', (prof_id,))
        
        # Then delete the professor
        cursor.execute('DELETE FROM professors WHERE id = ?', (prof_id,))
        
        # Commit transaction
        conn.commit()
        print(f"[DEBUG] Successfully deleted professor {name} and their schedules")
        return True
        
    except Exception as e:
        print(f"[DEBUG] Error deleting professor: {str(e)}")
        if conn:
            conn.rollback()
        return False

def add_professor(name, department, contact=None, email=None, picture=None):
    """Add a new professor
    
    Args:
        name (str): Professor's name
        department (str): Professor's department
        contact (str, optional): Professor's contact number
        email (str, optional): Professor's email
        picture (str, optional): Path to professor's picture
        
    Returns:
        bool: True if professor was added successfully, False otherwise
    """
    try:
        if not name or not department:
            print("[DEBUG] Missing required fields")
            return False
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if professor already exists
        cursor.execute('SELECT name FROM professors WHERE name = ?', (name,))
        if cursor.fetchone():
            print(f"[DEBUG] Professor {name} already exists")
            return False
            
        # Insert professor
        cursor.execute('''
            INSERT INTO professors (name, department, contact, email, picture)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, department, contact, email, picture))
        
        conn.commit()
        print(f"[DEBUG] Added new professor: {name} from {department}")
        return True
        
    except Exception as e:
        print(f"[DEBUG] Error adding professor: {str(e)}")
        if conn:
            conn.rollback()
        return False

def add_schedule(professor_id, day, start_time, end_time, subject):
    """Add a new schedule for a professor
    
    Args:
        professor_id (int): ID of the professor
        day (str): Day of the week
        start_time (str): Start time in HH:MM format
        end_time (str): End time in HH:MM format
        subject (str): Subject name
        
    Returns:
        bool: True if schedule was added successfully, False otherwise
    """
    try:
        if not all([professor_id, day, start_time, end_time, subject]):
            print("[DEBUG] Missing required fields")
            return False
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Add the schedule
        cursor.execute('''
            INSERT INTO schedules (professor_id, day, start_time, end_time, subject)
            VALUES (?, ?, ?, ?, ?)
        ''', (professor_id, day, start_time, end_time, subject))
        
        conn.commit()
        print(f"[DEBUG] Added schedule for professor {professor_id} on {day}")
        return True
        
    except Exception as e:
        print(f"[DEBUG] Error adding schedule: {str(e)}")
        if conn:
            conn.rollback()
        return False

def delete_schedule(schedule_id):
    """Delete a schedule
    
    Args:
        schedule_id (int): ID of the schedule to delete
        
    Returns:
        bool: True if schedule was deleted successfully, False otherwise
    """
    try:
        if not schedule_id:
            print("[DEBUG] Missing schedule ID")
            return False
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM schedules WHERE id = ?', (schedule_id,))
        conn.commit()
        
        print(f"[DEBUG] Deleted schedule {schedule_id}")
        return True
        
    except Exception as e:
        print(f"[DEBUG] Error deleting schedule: {str(e)}")
        if conn:
            conn.rollback()
        return False

def get_schedules_by_day(day=None):
    """Get all schedules for a specific day or all days
    
    Args:
        day (str, optional): Day of the week. If None, returns all schedules
        
    Returns:
        list: List of schedule dictionaries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if day:
            cursor.execute('''
                SELECT s.*, p.name as professor_name 
                FROM schedules s
                JOIN professors p ON s.professor_id = p.id
                WHERE s.day = ?
                ORDER BY s.start_time
            ''', (day,))
        else:
            cursor.execute('''
                SELECT s.*, p.name as professor_name 
                FROM schedules s
                JOIN professors p ON s.professor_id = p.id
                ORDER BY s.day, s.start_time
            ''')
            
        schedules = []
        for row in cursor.fetchall():
            schedule = {
                'id': row['id'],
                'professor_id': row['professor_id'],
                'professor_name': row['professor_name'],
                'day': row['day'],
                'start_time': row['start_time'],
                'end_time': row['end_time'],
                'subject': row['subject']
            }
            schedules.append(schedule)
            
        print(f"[DEBUG] Found {len(schedules)} schedules for day: {day if day else 'all'}")
        return schedules
        
    except Exception as e:
        print(f"[DEBUG] Error getting schedules: {str(e)}")
        return []

def update_single_schedule(schedule_id, day, start_time, end_time, subject):
    """Update a professor's schedule
    
    Args:
        schedule_id (int): ID of the schedule to update
        day (str): New day of the week
        start_time (str): New start time
        end_time (str): New end time
        subject (str): New subject
        
    Returns:
        bool: True if schedule was updated successfully, False otherwise
    """
    try:
        if not all([schedule_id, day, start_time, end_time, subject]):
            print("[DEBUG] Missing required fields")
            return False
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE schedules 
            SET day = ?, start_time = ?, end_time = ?, subject = ?
            WHERE id = ?
        ''', (day, start_time, end_time, subject, schedule_id))
        
        conn.commit()
        print(f"[DEBUG] Updated schedule {schedule_id}")
        return True
        
    except Exception as e:
        print(f"[DEBUG] Error updating schedule: {str(e)}")
        if conn:
            conn.rollback()
        return False

# Ensure database exists and is initialized
if not os.path.exists('data'):
    os.makedirs('data')
    
db_path = os.path.join('data', 'professor_checker.db')
if not os.path.exists(db_path):
    conn = get_db_connection()
    init_db()

# Register database cleanup
atexit.register(close_db)

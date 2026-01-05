import mysql.connector
from mysql.connector import pooling, Error
import hashlib
import streamlit as st
import os
from datetime import datetime, timedelta

# ==========================================
# 1. CONNECTION POOL (The Professional Fix)
# ==========================================
# We cache the POOL, not the individual connection.
@st.cache_resource
def get_db_pool():
    """Creates a pool of connections that stay alive."""
    try:
        db_config = st.secrets["mysql"].to_dict()
        
        # SSL Logic
        local_cert_path = "C:/Users/CHETANA GARUD/OneDrive/Chetana/isrgrootx1.pem"
        
        if os.path.exists(local_cert_path):
            db_config["ssl_ca"] = local_cert_path
            db_config["ssl_verify_identity"] = True
        else:
            db_config["ssl_ca"] = "/etc/ssl/certs/ca-certificates.crt"
            db_config["ssl_verify_identity"] = True

        # Create a Pool named 'mypool' with 3 connections
        # This keeps connections ready so there is NO LAG.
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=3,
            pool_reset_session=True,
            **db_config
        )
        print("✅ Database Pool Created!")
        return pool

    except Error as e:
        st.error(f"❌ Pool Creation Error: {e}")
        return None

def get_connection():
    """Gets a fresh connection from the pool."""
    try:
        pool = get_db_pool()
        if pool:
            # Get a connection from the pool
            conn = pool.get_connection()
            # Ensure it's actually alive
            if not conn.is_connected():
                conn.reconnect(attempts=3, delay=0)
            return conn
    except Error as e:
        st.error(f"⚠️ Connection Error: {e}")
        # Force clear cache if pool is broken
        st.cache_resource.clear()
        return None
    return None

# ==========================================
# 2. DATABASE OPERATIONS (Updated to use Pool)
# ==========================================
# NOTICE: We use 'with' blocks or explicit close() to return connections to the pool.

def create_table():
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            # Users
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'user',
                is_verified TINYINT(1) DEFAULT 0,
                otp VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP DEFAULT NULL
            )''')
            # Predictions
            cursor.execute('''CREATE TABLE IF NOT EXISTS predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                prediction_value VARCHAR(255),
                role_predicted VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            # Activity Logs
            cursor.execute('''CREATE TABLE IF NOT EXISTS activity_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255),
                action VARCHAR(255),
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            # Feedback
            cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255),
                job_role VARCHAR(255),
                predicted_salary VARCHAR(255),
                actual_salary VARCHAR(255),
                accuracy_rating VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            conn.commit()
            cursor.close()
            conn.close() # Important: Returns connection to pool
    except Exception as e:
        print(f"Setup Error: {e}")

def ensure_admin():
    admin_email = "chetanagarud2@gmail.com" 
    user = get_user_by_email(admin_email)
    if not user:
        create_user("Chetana Garud", admin_email, "Chetana2005@", "super_admin", 1)

# ==========================================
# 3. USER FUNCTIONS
# ==========================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_email(email):
    conn = get_connection()
    user = None
    if conn:
        try:
            cursor = conn.cursor(dictionary=True, buffered=True) 
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
        except Error:
            pass
        finally:
            conn.close() # Return to pool
    return user

def create_user(username, email, password, role="user", is_verified=0):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            hashed_pw = hash_password(password)
            cursor.execute("INSERT INTO users (username, email, password, role, is_verified) VALUES (%s, %s, %s, %s, %s)", 
                           (username, email, hashed_pw, role, is_verified))
            conn.commit()
            cursor.close()
            log_activity(username, "Account Created", f"Role: {role}")
            return True
        except Error as e:
            print(f"Error: {e}")
            return False
        finally:
            conn.close()
    return False

def create_user_pending_verification(username, email, password, otp):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            hashed_pw = hash_password(password)
            cursor.execute("INSERT INTO users (username, email, password, role, is_verified, otp) VALUES (%s, %s, %s, 'user', 0, %s)", 
                           (username, email, hashed_pw, otp))
            conn.commit()
            cursor.close()
            return True
        except Error:
            return False
        finally:
            conn.close()
    return False

def verify_user(email, otp_input):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute("SELECT otp FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            if result and str(result['otp']) == str(otp_input):
                cursor.execute("UPDATE users SET is_verified = 1, otp = NULL WHERE email = %s", (email,))
                conn.commit()
                cursor.close()
                log_activity(email, "Account Verified", "Success")
                return True
            cursor.close()
        except Error:
            pass
        finally:
            conn.close()
    return False

def set_otp_for_reset(email, otp):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET otp = %s WHERE email = %s", (otp, email))
            conn.commit()
            cursor.close()
            return True
        finally:
            conn.close()
    return False

def update_user_password(email, new_password):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            hashed_pw = hash_password(new_password)
            cursor.execute("UPDATE users SET password = %s, otp = NULL WHERE email = %s", (hashed_pw, email))
            conn.commit()
            cursor.close()
            log_activity(email, "Password Reset", "Success")
            return True
        finally:
            conn.close()
    return False

def delete_user(username):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            cursor.close()
            return True
        finally:
            conn.close()
    return False

# ==========================================
# 4. DATA FETCHING
# ==========================================
def get_user_history(username):
    conn = get_connection()
    data = []
    if conn:
        try:
            cursor = conn.cursor(buffered=True)
            query = "SELECT created_at, role_predicted, prediction_value FROM predictions WHERE username = %s ORDER BY created_at DESC LIMIT 5"
            cursor.execute(query, (username,))
            rows = cursor.fetchall()
            for row in rows:
                date_str = row[0].strftime("%b %d") if isinstance(row[0], datetime) else str(row[0])
                data.append((date_str, row[1], row[2]))
            cursor.close()
        except Error:
            pass
        finally:
            conn.close()
    return data

def get_dashboard_kpis():
    conn = get_connection()
    stats = {'users': 0, 'admins': 0, 'predictions': 0}
    if conn:
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
            stats['users'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE role IN ('admin', 'super_admin')")
            stats['admins'] = cursor.fetchone()[0]
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("SELECT COUNT(*) FROM predictions WHERE created_at > %s", (yesterday,))
            stats['predictions'] = cursor.fetchone()[0]
            cursor.close()
        except Error:
            pass
        finally:
            conn.close()
    return stats

def get_all_users():
    conn = get_connection()
    users = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute("SELECT id, username, email, role, created_at, last_login FROM users")
            rows = cursor.fetchall()
            for row in rows:
                joined_date = row['created_at'].strftime("%Y-%m-%d") if row['created_at'] else "-"
                last_log = row['last_login'].strftime("%Y-%m-%d %H:%M") if row.get('last_login') else "Never"
                users.append({
                    'id': row['id'], 'username': row['username'], 'email': row['email'], 
                    'role': row['role'], 'Joined': joined_date, 'Last Login': last_log
                })
            cursor.close()
        except Error:
            pass
        finally:
            conn.close()
    return users

def get_recent_logs(limit=50):
    conn = get_connection()
    logs = []
    if conn:
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute("SELECT username, action, details, timestamp FROM activity_logs ORDER BY timestamp DESC LIMIT %s", (limit,))
            rows = cursor.fetchall()
            for row in rows:
                logs.append({"User": row[0], "Action": row[1], "Details": row[2], "Time": row[3]})
            cursor.close()
        except Error:
            pass
        finally:
            conn.close()
    return logs

# ==========================================
# 5. LOGGING
# ==========================================
def log_activity(username, action, details=""):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO activity_logs (username, action, details) VALUES (%s, %s, %s)", (username, action, details))
            conn.commit()
            cursor.close()
        finally:
            conn.close()

def log_prediction(username, prediction_val, role):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO predictions (username, prediction_value, role_predicted) VALUES (%s, %s, %s)", (username, prediction_val, role))
            conn.commit()
            cursor.close()
            log_activity(username, "Prediction Generated", f"Role: {role}")
        finally:
            conn.close()

def log_feedback(username, job_role, predicted, actual, accuracy):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO feedback (username, job_role, predicted_salary, actual_salary, accuracy_rating) VALUES (%s, %s, %s, %s, %s)", (username, job_role, predicted, actual, accuracy))
            conn.commit()
            cursor.close()
        finally:
            conn.close()

def log_job_application(username, role, source, status):
    log_activity(username, "Job Click", f"{role} via {source} ({status})")

def log_login(username, email):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO activity_logs (username, action, details) VALUES (%s, %s, %s)", (username, "Login", f"Email: {email}"))
            cursor.execute("UPDATE users SET last_login = NOW() WHERE email = %s", (email,))
            conn.commit()
            cursor.close()
        finally:
            conn.close()
import bcrypt
import streamlit as st
from data.etf_data import get_connection


def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Vérifie un mot de passe contre son hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def get_user_by_email(email: str) -> dict:
    """Récupère un utilisateur depuis la DB."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, email, password_hash, role, is_active
            FROM users WHERE email = %s
        """, (email,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "email": row[1],
                "password_hash": row[2],
                "role": row[3],
                "is_active": row[4]
            }
        return None
    finally:
        conn.close()


def login(email: str, password: str) -> dict:
    """Tente une connexion. Retourne l'user ou None."""
    user = get_user_by_email(email)
    if not user:
        return None
    if not user["is_active"]:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


def create_user(email: str, password: str, role: str = "user") -> bool:
    """Crée un nouvel utilisateur."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (email, password_hash, role)
            VALUES (%s, %s, %s)
        """, (email, hash_password(password), role))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def delete_user(user_id: int) -> bool:
    """Supprime un utilisateur."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def get_all_users() -> list:
    """Retourne tous les utilisateurs (admin seulement)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, email, role, is_active, created_at
            FROM users ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        return [{"id": r[0], "email": r[1], "role": r[2],
                 "is_active": r[3], "created_at": r[4]} for r in rows]
    finally:
        conn.close()


def is_logged_in() -> bool:
    return "user" in st.session_state and st.session_state.user is not None


def is_admin() -> bool:
    return is_logged_in() and st.session_state.user["role"] == "admin"


def logout():
    st.session_state.user = None
    st.rerun()
"""
Database utilities for the escrow bot
"""

import sqlite3
import aiosqlite
from datetime import datetime
from typing import List, Dict, Optional
from config import DATABASE_FILE

async def init_db():
    """Initialize the database with required tables"""
    
    async with aiosqlite.connect(DATABASE_FILE) as db:
        # Users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Deals table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deal_id TEXT UNIQUE NOT NULL,
                creator_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                terms TEXT NOT NULL,
                status TEXT DEFAULT 'created',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (creator_id) REFERENCES users (user_id)
            )
        """)
        
        # Payments table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deal_id TEXT NOT NULL,
                payer_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                reference_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deal_id) REFERENCES deals (deal_id),
                FOREIGN KEY (payer_id) REFERENCES users (user_id)
            )
        """)
        
        # Rate limiting table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                user_id INTEGER PRIMARY KEY,
                last_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action_count INTEGER DEFAULT 1
            )
        """)
        
        await db.commit()

async def create_user(user_id: int, username: str, first_name: str) -> bool:
    """Create a new user"""
    
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            await db.execute(
                "INSERT OR REPLACE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
                (user_id, username, first_name)
            )
            await db.commit()
            return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

async def get_user(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

async def create_deal(deal_id: str, creator_id: int, description: str, amount: float, terms: str) -> bool:
    """Create a new deal"""
    
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            await db.execute(
                """INSERT INTO deals (deal_id, creator_id, description, amount, terms) 
                   VALUES (?, ?, ?, ?, ?)""",
                (deal_id, creator_id, description, amount, terms)
            )
            await db.commit()
            return True
    except Exception as e:
        print(f"Error creating deal: {e}")
        return False

async def get_deal(deal_id: str) -> Optional[Dict]:
    """Get deal by ID"""
    
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM deals WHERE deal_id = ?", (deal_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    except Exception as e:
        print(f"Error getting deal: {e}")
        return None

async def get_user_deals(user_id: int) -> List[Dict]:
    """Get all deals for a user"""
    
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM deals WHERE creator_id = ? ORDER BY created_at DESC", 
                (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting user deals: {e}")
        return []

async def get_all_deals(status: str = None) -> List[Dict]:
    """Get all deals, optionally filtered by status"""
    
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            db.row_factory = aiosqlite.Row
            if status:
                query = "SELECT * FROM deals WHERE status = ? ORDER BY created_at DESC"
                params = (status,)
            else:
                query = "SELECT * FROM deals ORDER BY created_at DESC"
                params = ()
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting all deals: {e}")
        return []

async def update_deal_status(deal_id: str, status: str) -> bool:
    """Update deal status"""
    
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            await db.execute(
                "UPDATE deals SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE deal_id = ?",
                (status, deal_id)
            )
            await db.commit()
            return True
    except Exception as e:
        print(f"Error updating deal status: {e}")
        return False

async def create_payment_record(deal_id: str, payer_id: int, amount: float, 
                              payment_method: str, reference_id: str, status: str) -> bool:
    """Create a payment record"""
    
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            await db.execute(
                """INSERT INTO payments (deal_id, payer_id, amount, payment_method, reference_id, status) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (deal_id, payer_id, amount, payment_method, reference_id, status)
            )
            await db.commit()
            return True
    except Exception as e:
        print(f"Error creating payment record: {e}")
        return False

async def get_deal_stats() -> Dict:
    """Get dashboard statistics"""
    
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            stats = {}
            
            # Total deals
            async with db.execute("SELECT COUNT(*) FROM deals") as cursor:
                result = await cursor.fetchone()
                stats['total_deals'] = result[0] if result else 0
            
            # Active deals (created or funded)
            async with db.execute(
                "SELECT COUNT(*) FROM deals WHERE status IN ('created', 'funded')"
            ) as cursor:
                result = await cursor.fetchone()
                stats['active_deals'] = result[0] if result else 0
            
            # Completed deals
            async with db.execute(
                "SELECT COUNT(*) FROM deals WHERE status = 'completed'"
            ) as cursor:
                result = await cursor.fetchone()
                stats['completed_deals'] = result[0] if result else 0
            
            # Disputed deals
            async with db.execute(
                "SELECT COUNT(*) FROM deals WHERE status = 'disputed'"
            ) as cursor:
                result = await cursor.fetchone()
                stats['disputed_deals'] = result[0] if result else 0
            
            # Total escrow value (active deals)
            async with db.execute(
                "SELECT SUM(amount) FROM deals WHERE status IN ('created', 'funded')"
            ) as cursor:
                result = await cursor.fetchone()
                stats['total_value'] = result[0] if result and result[0] else 0
            
            return stats
            
    except Exception as e:
        print(f"Error getting deal stats: {e}")
        return {}

async def check_rate_limit(user_id: int, limit_seconds: int = 5) -> bool:
    """Check if user is within rate limit"""
    
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            now = datetime.now()
            
            # Get last action
            async with db.execute(
                "SELECT last_action FROM rate_limits WHERE user_id = ?", (user_id,)
            ) as cursor:
                result = await cursor.fetchone()
            
            if result:
                last_action = datetime.fromisoformat(result[0])
                time_diff = (now - last_action).total_seconds()
                
                if time_diff < limit_seconds:
                    return False  # Rate limited
            
            # Update rate limit record
            await db.execute(
                "INSERT OR REPLACE INTO rate_limits (user_id, last_action) VALUES (?, ?)",
                (user_id, now.isoformat())
            )
            await db.commit()
            
            return True  # Within rate limit
            
    except Exception as e:
        print(f"Error checking rate limit: {e}")
        return True  # Allow on error

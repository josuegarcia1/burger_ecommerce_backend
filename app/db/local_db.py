import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class LocalDB:
    def __init__(self, db_path: str = "local_burger.db"):
        # Asegurar que el directorio exista
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        """Inicializa la base de datos local con las tablas necesarias"""
        cursor = self.conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT,
            full_name TEXT,
            is_google_auth INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Tabla de productos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            image_url TEXT,
            category TEXT,
            ingredients TEXT,
            is_available INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Tabla del carrito
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart_items (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            options TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        # Tabla de operaciones pendientes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_operations (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            data TEXT,
            item_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.conn.commit()

    def get_pending_operations(self) -> List[Dict]:
        """Obtiene todas las operaciones pendientes de sincronización"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('SELECT * FROM pending_operations ORDER BY created_at ASC')
            rows = cursor.fetchall()
            
            operations = []
            for row in rows:
                try:
                    operation = {
                        'id': row[0],
                        'type': row[1],
                        'data': json.loads(row[2]) if row[2] else None,
                        'item_id': row[3],
                        'created_at': row[4]
                    }
                    operations.append(operation)
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding JSON for operation {row[0]}: {e}")
                    continue
            
            return operations
        except sqlite3.Error as e:
            logger.error(f"Error getting pending operations: {e}")
            return []

    def remove_pending_operation(self, operation_id: str) -> bool:
        """Elimina una operación pendiente después de sincronizarla"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('DELETE FROM pending_operations WHERE id = ?', (operation_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error removing pending operation {operation_id}: {e}")
            return False

    def add_pending_operation(self, operation: Dict) -> bool:
        """Añade una nueva operación pendiente de sincronización"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                '''
                INSERT INTO pending_operations 
                (id, type, data, item_id, created_at)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (
                    operation.get('id', str(datetime.now().timestamp())),
                    operation['type'],
                    json.dumps(operation.get('data')) if operation.get('data') else None,
                    operation.get('item_id'),
                    datetime.now()
                )
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error adding pending operation: {e}")
            return False

    def get_cart_items(self, user_id: str) -> List[Dict]:
        """Obtiene los items del carrito para un usuario específico"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                SELECT 
                    c.id, c.user_id, c.product_id, c.quantity, c.options, c.created_at,
                    p.name, p.price, p.image_url
                FROM cart_items c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = ?
            ''', (user_id,))
            
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'user_id': row[1],
                    'product_id': row[2],
                    'quantity': row[3],
                    'options': row[4],
                    'created_at': row[5],
                    'product_name': row[6],
                    'product_price': row[7],
                    'product_image': row[8]
                }
                for row in rows
            ]
        except sqlite3.Error as e:
            logger.error(f"Error getting cart items for user {user_id}: {e}")
            return []

    def add_cart_item(self, user_id: str, product_id: str, quantity: int, options: str = None) -> bool:
        """Añade un item al carrito local"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                '''
                INSERT INTO cart_items 
                (id, user_id, product_id, quantity, options)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (
                    f"{user_id}_{product_id}",
                    user_id,
                    product_id,
                    quantity,
                    options
                )
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error adding cart item: {e}")
            return False

    def remove_cart_item(self, item_id: str) -> bool:
        """Elimina un item del carrito local"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('DELETE FROM cart_items WHERE id = ?', (item_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error removing cart item {item_id}: {e}")
            return False

    def update_cart_item(self, item_id: str, quantity: int, options: str = None) -> bool:
        """Actualiza un item del carrito local"""
        cursor = self.conn.cursor()
        try:
            if options is not None:
                cursor.execute(
                    'UPDATE cart_items SET quantity = ?, options = ? WHERE id = ?',
                    (quantity, options, item_id)
                )
            else:
                cursor.execute(
                    'UPDATE cart_items SET quantity = ? WHERE id = ?',
                    (quantity, item_id)
                )
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error updating cart item {item_id}: {e}")
            return False

    def get_product(self, product_id: str) -> Optional[Dict]:
        """Obtiene un producto por su ID"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'price': row[3],
                    'image_url': row[4],
                    'category': row[5],
                    'ingredients': row[6],
                    'is_available': bool(row[7]),
                    'created_at': row[8]
                }
            return None
        except sqlite3.Error as e:
            logger.error(f"Error getting product {product_id}: {e}")
            return None

    def get_products(self) -> List[Dict]:
        """Obtiene todos los productos disponibles"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('SELECT * FROM products WHERE is_available = 1')
            rows = cursor.fetchall()
            
            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'price': row[3],
                    'image_url': row[4],
                    'category': row[5],
                    'ingredients': row[6],
                    'is_available': bool(row[7]),
                    'created_at': row[8]
                }
                for row in rows
            ]
        except sqlite3.Error as e:
            logger.error(f"Error getting products: {e}")
            return []

    def add_product(self, product: Dict) -> bool:
        """Añade un producto a la base de datos local"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                '''
                INSERT INTO products 
                (id, name, description, price, image_url, category, ingredients, is_available)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    product['id'],
                    product['name'],
                    product.get('description'),
                    product['price'],
                    product.get('image_url'),
                    product.get('category'),
                    product.get('ingredients'),
                    product.get('is_available', True)
                )
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error adding product {product['id']}: {e}")
            return False

    def close(self):
        """Cierra la conexión con la base de datos"""
        try:
            self.conn.close()
        except sqlite3.Error as e:
            logger.error(f"Error closing database: {e}")

    def __del__(self):
        """Destructor que asegura que la conexión se cierre"""
        self.close()
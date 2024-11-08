from flask import Flask, jsonify, request
import sqlite3
import threading
import os

app = Flask(__name__)


thread_local_storage = threading.local()

pathOrderDB = os.path.join(os.path.dirname(__file__), 'order.db')
pathCatalogDB = os.path.join(os.path.dirname(__file__), '../catalog/catalog.db')

@app.route('/')  
def home():  
    return "order service is running!" 

def openOrderDB():
    if not hasattr(thread_local_storage, 'order_db_connection'):
        thread_local_storage.order_db_connection = sqlite3.connect(pathOrderDB)
        thread_local_storage.order_db_connection.row_factory = sqlite3.Row
    return thread_local_storage.order_db_connection

def openCatalogDB():
    if not hasattr(thread_local_storage, 'catalog_db_connection'):
        thread_local_storage.catalog_db_connection = sqlite3.connect(pathCatalogDB)
        thread_local_storage.catalog_db_connection.row_factory = sqlite3.Row
    return thread_local_storage.catalog_db_connection

@app.teardown_appcontext
def close_connections(error):
    if hasattr(thread_local_storage, 'order_db_connection'):
        thread_local_storage.order_db_connection.close()
    if hasattr(thread_local_storage, 'catalog_db_connection'):
        thread_local_storage.catalog_db_connection.close()

#! work: done
@app.route('/purchase/<book_id>/', methods=['PUT'])
def process_purchase(book_id):
    
    try:
        book_id = int(book_id)
    except ValueError:
        return jsonify({"message": "Book ID must be a numeric value"}), 400

    order_db_connection = openOrderDB()
    catalog_db_connection = openCatalogDB()

    with catalog_db_connection:
        cursor = catalog_db_connection.cursor()
        cursor.execute("SELECT * FROM books WHERE id=?", (book_id,))
        book_info = cursor.fetchone()
        
        
        if book_info:
            if book_info['quantity'] > 0:
                updated_quantity = book_info['quantity'] - 1
                cursor.execute("UPDATE books SET quantity=? WHERE id=?", (updated_quantity, book_id))
            else:
                return jsonify({"message": "Book out of stock", "status": False}), 400
        else:
            return jsonify({"message": "Book not found", "status": False}), 404

    
    
    with order_db_connection:
        order_cursor = order_db_connection.cursor()
        order_cursor.execute("INSERT INTO orders (book_id, order_date, quantity) VALUES (?, ?, ?)", (book_id, "2020-10-13", 1))
    
    return jsonify({"message": "Book successfully purchased", "status": True}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5002)
"""
Простой тест ChromaDB
"""
import os
import chromadb

print("🧪 Простой тест ChromaDB...")

try:
    # Создаем клиент
    print("📡 Создаем ChromaDB клиент...")
    client = chromadb.PersistentClient(path="./vector_db")
    print("✅ ChromaDB клиент создан!")
    
    # Создаем коллекцию
    print("📋 Создаем коллекцию...")
    collection = client.get_or_create_collection(name="test_collection")
    print("✅ Коллекция создана!")
    
    # Добавляем тестовые данные
    print("📝 Добавляем тестовые данные...")
    collection.add(
        documents=["Тестовый документ для проверки"],
        ids=["test_1"]
    )
    print("✅ Данные добавлены!")
    
    # Проверяем содержимое
    print("🔍 Проверяем содержимое...")
    results = collection.get()
    print(f"📊 Найдено документов: {len(results['documents'])}")
    
    print("🎉 ChromaDB работает корректно!")
    print("📁 Папка vector_db должна была создаться!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

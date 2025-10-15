print("Начинаем тест...")

try:
    import chromadb
    print("✅ ChromaDB импортирован")
    
    client = chromadb.PersistentClient(path="./vector_db")
    print("✅ ChromaDB клиент создан")
    
    collection = client.get_or_create_collection(name="test")
    print("✅ Коллекция создана")
    
    print("🎉 Тест завершен успешно!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

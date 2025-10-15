"""
Скрипт для запуска LLM воркера
"""
import asyncio
import logging
from llm_worker import main

if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Запуск воркера
    asyncio.run(main())

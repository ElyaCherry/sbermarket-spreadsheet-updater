# sbermarket-spreadsheet-updater
A personal initiative to aid visually finding the best prices for products to sell in the dormitory (don't tell the government).
Written with Python Selenuim + BeautifulSoup. Utilises I/O multithreading.

<img width="1513" alt="image" src="https://github.com/ElyaCherry/sbermarket-spreadsheet-updater/assets/71253759/3909a26c-8c5f-4e1b-b4a3-a8d9614346d9">
На первой вкладке установлен кастомный макрос, который применяет к каждой строке правило, раскрашивая самые низкие цены (топ 19% промежутка значений) в зеленый, а самые высокие в красный. На вкладке `urls` в соответствующих клетках находятся постоянные ссылки на товары, которые открываются в общем браузере под Selenium. Каждая вкладка парсится через BeautifulSoup, и цены записываются на главной вкладке в отдельных потоках.

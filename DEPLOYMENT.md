# 🚀 Деплой "The LEGEND of ASHCHIME" на Vercel

Пошаговая инструкция по развертыванию игры на вашем домене через Vercel.

---

## 📋 Предварительные требования

- Аккаунт на [Vercel](https://vercel.com)
- Git установлен на компьютере
- Аккаунт на GitHub (рекомендуется)

---

## 🛠️ Шаг 1: Подготовка проекта

### 1.1 Установка Pygbag (локальное тестирование)

```powershell
pip install pygbag pygame-ce
```

### 1.2 Локальное тестирование

Проверьте, что игра работает с Pygbag:

```powershell
# Запуск локального сервера для тестирования
python -m pygbag main_web.py

# Откройте браузер на http://localhost:8000
```

> **Важно:** Если видите ошибки, проверьте, что все пути к ассетам правильные.

---

## 📦 Шаг 2: Загрузка на GitHub

### 2.1 Инициализация Git (если еще не сделано)

```powershell
# Перейдите в папку проекта
cd "C:\Users\Admin\OneDrive\Рабочий стол\mag_vs_ghosts"

# Инициализация репозитория
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: The LEGEND of ASHCHIME"
```

### 2.2 Создание репозитория на GitHub

1. Перейдите на [GitHub](https://github.com)
2. Нажмите **"New repository"**
3. Название: `mag_vs_ghosts` или `ashchime-game`
4. Выберите **Public** или **Private**
5. НЕ добавляйте README, .gitignore (уже есть)
6. Нажмите **"Create repository"**

### 2.3 Связывание с GitHub

```powershell
# Замените YOUR_USERNAME на ваш GitHub username
git remote add origin https://github.com/YOUR_USERNAME/mag_vs_ghosts.git

# Отправка кода
git branch -M main
git push -u origin main
```

---

## 🌐 Шаг 3: Деплой на Vercel

### 3.1 Подключение к Vercel

1. Перейдите на [vercel.com](https://vercel.com)
2. Нажмите **"New Project"**
3. Выберите **"Import Git Repository"**
4. Подключите ваш GitHub аккаунт (если еще не подключен)
5. Выберите репозиторий `mag_vs_ghosts`

### 3.2 Настройка сборки

**Vercel автоматически найдет `vercel.json`, но на всякий случай проверьте:**

- **Build Command:** `python -m pygbag --build main_web.py`
- **Output Directory:** `build/web`
- **Install Command:** `pip install pygbag pygame-ce`

### 3.3 Переменные окружения (опционально)

Если нужны переменные окружения, добавьте их в разделе **Environment Variables**.

### 3.4 Деплой

1. Нажмите **"Deploy"**
2. Дождитесь окончания сборки (может занять 2-5 минут)
3. Получите URL: `https://your-project.vercel.app`

---

## 🔗 Шаг 4: Подключение своего домена

### 4.1 В панели Vercel

1. Откройте ваш проект в Vercel
2. Перейдите в **"Settings"** → **"Domains"**
3. Нажмите **"Add Domain"**
4. Введите ваш домен, например: `ashchime.com` или `play.yourdomain.com`

### 4.2 Настройка DNS

В настройках вашего доменного провайдера (Cloudflare, Namecheap, и т.д.):

**Для корневого домена (ashchime.com):**
```
Type: A
Name: @
Value: 76.76.21.21 (Vercel IP)
```

**Для поддомена (play.yourdomain.com):**
```
Type: CNAME
Name: play
Value: cname.vercel-dns.com
```

### 4.3 Подтверждение

1. Вернитесь в Vercel
2. Дождитесь проверки DNS (может занять до 48 часов, обычно 10-30 минут)
3. После проверки Vercel автоматически выдаст SSL сертификат

---

## 🔄 Шаг 5: Обновление игры

Когда вы вносите изменения в код:

```powershell
# Добавить изменения
git add .

# Коммит
git commit -m "Update: описание изменений"

# Отправка на GitHub
git push

# Vercel автоматически пересоберет и задеплоит!
```

---

## ⚠️ Возможные проблемы

### Проблема 1: Pygbag не собирается

**Решение:**
```powershell
# Обновите Pygbag
pip install --upgrade pygbag pygame-ce

# Проверьте версию Python (нужна 3.10+)
python --version
```

### Проблема 2: Ассеты не загружаются

**Решение:**
- Убедитесь, что папка `assets/` в корне проекта
- Проверьте пути в коде (должны быть относительные: `assets/file.png`)

### Проблема 3: Игра тормозит в браузере

**Решение:**
- Оптимизируйте изображения (сжатие PNG)
- Уменьшите разрешение спрайтов
- Используйте меньше частиц/эффектов

### Проблема 4: Музыка не работает

**Решение:**
- Конвертируйте музыку в OGG формат (браузеры лучше поддерживают)
- Проверьте размер файлов (большие медиа долго загружаются)

---

## 📊 Оптимизация производительности

### Сжатие ассетов

```powershell
# Установите TinyPNG CLI или используйте онлайн сервисы
# Сожмите все PNG файлы в assets/
```

### Уменьшение размера билда

1. Удалите неиспользуемые ассеты
2. Сожмите аудио файлы (битрейт 128kbps для музыки)
3. Оптимизируйте спрайт-листы

---

## 📈 Мониторинг

### Vercel Analytics

В панели Vercel можете включить:
- **Analytics** - статистика посещений
- **Speed Insights** - производительность
- **Web Vitals** - метрики загрузки

---

## 🎉 Готово!

Ваша игра теперь доступна по адресу:
- **Vercel URL:** `https://your-project.vercel.app`
- **Ваш домен:** `https://yourdomain.com`

### Поделитесь игрой:

```markdown
🧙‍♂️ The LEGEND of ASHCHIME
Играйте онлайн: https://yourdomain.com
```

---

## 🆘 Поддержка

Если возникли проблемы:

1. **Проверьте логи сборки** в Vercel Dashboard
2. **Локальное тестирование:** `python -m pygbag main_web.py`
3. **GitHub Issues:** создайте issue в репозитории
4. **Vercel Support:** support.vercel.com

---

## 📚 Дополнительные ресурсы

- [Pygbag Documentation](https://pygame-web.github.io/)
- [Vercel Documentation](https://vercel.com/docs)
- [Pygame-ce Documentation](https://pyga.me/docs/)

---

**Удачи с вашим деплоем! 🚀✨**

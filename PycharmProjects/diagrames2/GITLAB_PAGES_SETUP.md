# Настройка GitLab Pages для диаграмм

## 1. Включите Pages в настройках проекта

Перейдите в ваш проект на GitLab:
- **Settings** → **General** → разверните секцию **Visibility, project features, permissions**
- Найдите **GitLab Pages** и включите его (чекбокс должен быть активен)
- Нажмите **Save changes**

## 2. Как работают ссылки на диаграммы

После успешного выполнения пайплайна:

### Главная страница со списком всех диаграмм:
```
https://username.gitlab.io/project-name/
```

### Прямые ссылки на каждую диаграмму:

Если у вас диаграммы называются `example.puml`, `login.puml`, `payment.puml`, то они будут доступны по ссылкам:

```
https://username.gitlab.io/project-name/example.png
https://username.gitlab.io/project-name/login.png
https://username.gitlab.io/project-name/payment.png
```

**Пример:**
Если ваш репозиторий: `git.melonfashion.ru/befree/qa/befree-diagrams`

То:
- Главная страница: `https://git.melonfashion.ru/befree/qa/befree-diagrams/`
- Диаграмма example: `https://git.melonfashion.ru/befree/qa/befree-diagrams/example.png`

## 3. Как проверить, что Pages работает

После того как пайплайн выполнился успешно:
- Перейдите в **Deploy** → **Pages** (если не видно сразу, обновите страницу)
- Увидите ссылку на опубликованный сайт

Или:
- Перейдите в **Settings** → **Pages**
- Там будет указан URL

## 4. Проверьте настройки приватности

- **Settings** → **General** → **Visibility** 
  - Если проект **Public** - диаграммы доступны всем по ссылке
  - Если проект **Private** - нужен доступ к проекту для просмотра

## 5. Структура файлов

После успешного пайплайна в артефактах будет:
```
public/
  ├── index.html       (список всех диаграмм)
  ├── example.png      (диаграмма 1)
  ├── login.png        (диаграмма 2)
  └── payment.png      (диаграмма 3)
```

## 6. Как добавить новую диаграмму

Просто добавьте новый `.puml` файл в папку `sequences/`:
- `sequences/new-diagram.puml`
- Запустите пайплайн (или он запустится автоматически при коммите)
- Новая диаграмма появится на главной странице и будет доступна по:
```
https://username.gitlab.io/project-name/new-diagram.png
```


# Где найти Settings в GitLab

В левом сайдбаре (боковое меню слева):

## Вариант 1:
1. Найдите секцию **"Manage"** в левом меню
2. Наведите на неё или кликните, чтобы развернуть
3. Там будет пункт **"Settings"**

## Вариант 2:
1. В самом низу левого сайдбара, под всеми секциями
2. Может быть **"Settings"** как отдельный пункт внизу меню

## Если Settings нет в меню:

### Способ через URL:
Откройте в браузере:
```
https://git.melonfashion.ru/befree/qa/befree-diagrams/edit
```

Или замен sedit на settings:
```
https://git.melonfashion.ru/befree/qa/befree-diagrams/-/settings/general
```

## Альтернативный способ - через Pipelines:

1. Если не находите Settings напрямую
2. Перейдите в **Pipelines** (в левом меню)
3. Найдите последний запуск пайплайна с джобой `pages`
4. Если она есть и успешна - Pages уже работает

## Проверить работает ли Pages:

Просто откройте:
```
https://git.melonfashion.ru/befree/qa/befree-diagrams/-/jobs
```

Или попробуйте прямой URL к Pages (если пайплайн завершился):
```
https://git.melonfashion.ru/befree/qa/befree-diagrams/
```


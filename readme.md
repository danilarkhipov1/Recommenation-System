# Проект "Рекомендательная система"

## Задача

:heavy_check_mark: Реализовать сервис, который для каждого юзера в любой момент времени возвращает посты, которые пользователю покажут в его ленте соцсети;

:heavy_check_mark: Подготовить сервис к проведению АВ - эксперимента.

## План реализации

:one: Загрузка данных из БД, EDA;

:two: Создание признаков и обучающей выборки;

:three: Выбор и обучение модели и оценка ее качества на валидационной выборке;

:four: Совершенствование модели благодаря глубокому обучению (embedding);

:five: Написание сервиса: загрузка модели -> получение признаков для модели по user_id -> предсказание постов, которые лайкнут -> возвращение ответа;

:six: Подготовка сервиса к проведению АВ-эксперимента: сервис разбивает пользователей на группы и в своём ответе указывает, какую из моделей он применил, чтобы далее по логам можно было бы посчитать метрики для каждой из групп.

## Описание данных
**Таблица user_data**

Cодержит информацию о всех пользователях соц.сети
| Field name	| Overview |
|:----------|:---------|
| age	| Возраст пользователя (в профиле) |
| city	| Город пользователя (в профиле) |
| country	| Страна пользователя (в профиле) |
| exp_group	| Экспериментальная группа: некоторая зашифрованная категория |
| gender	| Пол пользователя |
| id	| Уникальный идентификатор пользователя |
| os	| Операционная система устройства, с которого происходит пользование соц.сетью |
| source	| Пришел ли пользователь в приложение с органического трафика или с рекламы |

**Таблица post_text_df**

Содержит информацию о постах и уникальный ID каждой единицы с соответствующим ей текстом и топиком
| Field name	| Overview
|:----------|:---------|
| id	| Уникальный идентификатор поста |
| text	| Текстовое содержание поста |
| topic	| Основная тематика |

**Таблица feed_data**

Содержит историю о просмотренных постах для каждого юзера в изучаемый период.
| Field name	| Overview |
|:----------|:---------|
| timestamp	| Время, когда был произведен просмотр |
| user_id	| id пользователя, который совершил просмотр |
| post_id	| id просмотренного поста |
| action	| Тип действия: просмотр или лайк |
| target	| 1 у просмотров, если почти сразу после просмотра был совершен лайк, иначе 0. У действий like пропущенное значение. |

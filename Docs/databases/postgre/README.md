# Схема базы данных PostgreSQL

## 1. Схема `users` (Авторизация и Профили)

### Таблица `users.accounts` (Системные данные учетных записей)
| Колонка | Тип данных | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Primary Key | Уникальный идентификатор аккаунта. |
| `email` | VARCHAR | Unique, Indexed | Основной email пользователя для входа. |
| `is_active` | BOOLEAN | | Статус активности/блокировки аккаунта. |
| `created_at` | TIMESTAMP WITH TIME ZONE | | Дата и время регистрации. |

### Таблица `users.profiles` (Публичные профили пользователей)
| Колонка | Тип данных | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Primary Key, FK -> `users.accounts.id` ON DELETE CASCADE | Уникальный ID профиля (совпадает с ID аккаунта). |
| `username` | VARCHAR | Uniquely Indexed | Уникальный логин/никнейм пользователя для поиска. |
| `display_name` | VARCHAR | Nullable | Отображаемое имя (публичное). |
| `avatar_url` | VARCHAR | Nullable | Ссылка на аватар пользователя. |
| `bio` | VARCHAR(200) | Nullable | Краткое описание профиля (до 200 символов). |
| `updated_at` | TIMESTAMP WITH TIME ZONE | | Дата и время последнего изменения профиля. |

### Таблица `users.linked_emails` (Резервные email)
| Колонка | Тип данных | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Primary Key | Уникальный идентификатор записи. |
| `account_id` | UUID | FK -> `users.accounts.id` ON DELETE CASCADE | Связь с основным аккаунтом пользователя. |
| `email` | VARCHAR | Unique | Дополнительный привязанный резервный email. |

### Таблица `users.auth_links` (Временные ссылки авторизации)
| Колонка | Тип данных | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Primary Key | Уникальный ID ссылки быстрой авторизации. |
| `account_id` | UUID | FK -> `users.accounts.id` ON DELETE CASCADE | ID пользователя, для которого сгенерирована ссылка. |
| `token_hash` | VARCHAR | Unique, Indexed | Криптографический хэш токена ссылки. |
| `expires_at` | TIMESTAMP WITH TIME ZONE | Nullable, No Default | Срок действия ссылки быстрой авторизации (null = бессрочно, задается пользователем). |
| `created_at` | TIMESTAMP WITH TIME ZONE | | Дата и время генерации ссылки. |

### Таблица `users.sessions` (Активные сессии и устройства)
| Колонка | Тип данных | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Primary Key | Уникальный ID сессии (устройства). |
| `user_id` | UUID | FK -> `users.accounts.id` ON DELETE CASCADE | ID владельца сессии. |
| `refresh_token_hash` | VARCHAR | Unique, Indexed | Хэш Refresh-токена для безопасности. |
| `device_info` | VARCHAR | Nullable | Информация об устройстве (браузер, ОС, модель смартфона). |
| `ip_address` | VARCHAR | Nullable | IP-адрес последней активности. |
| `last_active_at` | TIMESTAMP WITH TIME ZONE | | Время последней активности пользователя. |
| `created_at` | TIMESTAMP WITH TIME ZONE | | Дата создания сессии (первичного входа). |
| `expires_at` | TIMESTAMP WITH TIME ZONE | | Дата истечения сессии (автоматически сдвигается на +18 месяцев). |

> [!NOTE]
> **Паттерн Скользящей Сессии (Sliding Session Expiration):**
> * Срок жизни сессии составляет 18 месяцев.
> * Для оптимизации производительности СУБД и снижения избыточной нагрузки на запись, дата последней активности `last_active_at` и продление `expires_at` (на +18 месяцев) должны обновляться в PostgreSQL **не чаще одного раза в сутки** при наличии активности пользователя на любом из устройств.

### Таблица `users.ui_settings` (Настройки интерфейса)
| Колонка | Тип данных | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | Primary Key, FK -> `users.accounts.id` ON DELETE CASCADE | ID пользователя, к которому относятся настройки. |
| `theme` | VARCHAR | Default: 'dark' | Выбранная тема оформления (Enum: `dark`, `light`). |
| `language` | VARCHAR | Default: 'ru' | Язык интерфейса (Enum: `ru`, `en`). |




## 2. Схема `chats` (Диалоги и Сообщения)

> [!NOTE]
> **Бизнес-логика удаления переписки (п. 2 и п. 34.2 `functional.md`):**
> * **Личные чаты (`type = 'personal'`):** При удалении чата одним из участников, весь чат и история сообщений каскадно удаляются для обоих пользователей (физическое удаление записи чата с каскадным `ON DELETE CASCADE`).
> * **Групповые чаты (`type = 'group'`):** При «удалении» чата обычным участником, он просто исключается из чата (удаляется его запись из `chats.chat_members`), но сам чат и история переписки сохраняются для других участников группы.

### Таблица `chats.chats` (Комнаты чатов)
| Колонка | Тип данных | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Primary Key | Уникальный идентификатор чата. |
| `type` | VARCHAR | Enum: `personal`, `group` | Тип чата (личный диалог или групповой чат). |
| `name` | VARCHAR | Nullable | Название чата (заполнено только для групповых). |
| `avatar_url` | VARCHAR | Nullable | Ссылка на аватар группы. |
| `created_at` | TIMESTAMP WITH TIME ZONE | | Дата и время создания чата. |

### Таблица `chats.chat_members` (Связи участников и чатов)
| Колонка | Тип данных | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| `chat_id` | UUID | Primary Key, FK -> `chats.chats.id` ON DELETE CASCADE | ID чата, к которому привязан участник. |
| `user_id` | UUID | Primary Key, FK -> `users.accounts.id` ON DELETE CASCADE | ID пользователя-участника. |
| `role` | VARCHAR | Enum: `owner`, `admin`, `member` | Роль и уровень прав пользователя в данном чате. |
| `joined_at` | TIMESTAMP WITH TIME ZONE | Default: NOW | Дата и время вступления пользователя в чат. |

### Таблица `chats.messages` (История сообщений)
| Колонка | Тип данных | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Primary Key | Уникальный идентификатор сообщения. |
| `chat_id` | UUID | FK -> `chats.chats.id` ON DELETE CASCADE, Indexed | ID чата, в который отправлено сообщение. |
| `sender_id` | UUID | Nullable, FK -> `users.accounts.id` ON DELETE SET NULL, Indexed | ID отправителя сообщения (становится null, если аккаунт удален). |
| `content` | JSONB | | Структурированное динамическое наполнение (текст, гео, файлы). |
| `created_at` | TIMESTAMP WITH TIME ZONE | Indexed | Дата и время отправки сообщения. |
| `updated_at` | TIMESTAMP WITH TIME ZONE | | Дата и время редактирования сообщения (null, если не редактировалось). |

### Таблица `chats.read_markers` (Маркеры прочтения сообщений)
| Колонка | Тип данных | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| `chat_id` | UUID | Primary Key, FK -> `chats.chats.id` ON DELETE CASCADE | ID чата. |
| `user_id` | UUID | Primary Key, FK -> `users.accounts.id` ON DELETE CASCADE | ID пользователя, для которого отслеживается прочтение. |
| `last_read_message_id` | UUID | Nullable, FK -> `chats.messages.id` | ID последнего прочитанного сообщения в этом чате. |

---

## 3. Схема `contacts` (Связи и Приватность)

### Таблица `contacts.friend_lists` (Списки контактов)
| Колонка | Тип данных | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | Primary Key, FK -> `users.accounts.id` ON DELETE CASCADE | ID владельца списка контактов. |
| `contact_id` | UUID | Primary Key, FK -> `users.accounts.id` ON DELETE CASCADE | ID контакта (пользователя, добавленного в друзья). |

### Таблица `contacts.block_lists` (Черный список)
| Колонка | Тип данных | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | Primary Key, FK -> `users.accounts.id` ON DELETE CASCADE | ID пользователя, который инициировал блокировку. |
| `blocked_id` | UUID | Primary Key, FK -> `users.accounts.id` ON DELETE CASCADE | ID заблокированного пользователя. |

### Таблица `contacts.privacy_settings` (Настройки приватности)
| Колонка | Тип данных | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | Primary Key, FK -> `users.accounts.id` ON DELETE CASCADE | ID владельца настроек приватности. |
| `show_online` | VARCHAR | Enum: `everyone`, `contacts`, `some_contacts`, `nobody` | Кому разрешено видеть текущий статус «онлайн». |
| `show_bio` | VARCHAR | Enum: `everyone`, `contacts`, `some_contacts`, `nobody` | Кому разрешено видеть био (описание профиля). |

### Таблица `contacts.privacy_exceptions` (Исключения приватности)
| Колонка | Тип данных | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | Primary Key, FK -> `users.accounts.id` ON DELETE CASCADE | ID пользователя, настроившего исключение. |
| `contact_id` | UUID | Primary Key, FK -> `users.accounts.id` ON DELETE CASCADE | ID контакта (пользователя), для которого применяется исключение. |
| `field` | VARCHAR | Primary Key, Enum: `online`, `bio` | К какому полю приватности относится это исключение. |
| `exception_type` | VARCHAR | Enum: `allow`, `block` | Тип действия: принудительно разрешить (`allow`) или принудительно запретить (`block`). |


## 4. Схема `read_models` (Денормализованные витрины чтения / CQRS)

### Таблица `read_models.user_chats_list` (Витрина списка чатов)
| Колонка | Тип данных | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | Primary Key, FK -> `users.accounts.id` ON DELETE CASCADE | ID пользователя, для которого сформирован элемент списка. |
| `chat_id` | UUID | Primary Key, FK -> `chats.chats.id` ON DELETE CASCADE | ID соответствующего чата. |
| `chat_name` | VARCHAR | Nullable | Отображаемое имя чата (динамически вычисляется). |
| `chat_avatar_url` | VARCHAR | Nullable | Ссылка на аватар чата/собеседника. |
| `last_message_text` | VARCHAR | Nullable | Текст последнего сообщения для быстрого предпросмотра. |
| `last_message_sender_name`| VARCHAR | Nullable | Имя отправителя последнего сообщения. |
| `last_message_time` | TIMESTAMP WITH TIME ZONE| Nullable, Indexed | Время отправки последнего сообщения (для сортировки списка). |
| `unread_count` | INTEGER | Default: 0 | Счетчик непрочитанных сообщений в этом чате. |
| `updated_at` | TIMESTAMP WITH TIME ZONE| Default: NOW | Время последнего обновления строки витрины. |


## Спецификация JSONB поля `content` в сообщениях

Использование типа `JSONB` для поля `content` позволяет расширять типы сообщений без изменения схемы БД. В зависимости от типа сообщения, поле имеет разную структуру:

### 1. Текстовое сообщение
```json
{
  "type": "text",
  "text": "Привет! Как дела?"
}
```

### 2. Гео-локация
```json
{
  "type": "location",
  "latitude": 55.7558,
  "longitude": 37.6173,
  "address": "Кремль, Москва, Россия"
}
```

### 3. Файловое вложение (Изображение, Видео, Документ)
```json
{
  "type": "file",
  "file_type": "image",
  "url": "https://storage.messenger.com/files/img_123.png",
  "file_name": "photo.png",
  "file_size": 2048576,
  "mime_type": "image/png"
}
```

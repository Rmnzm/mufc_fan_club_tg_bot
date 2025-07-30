BASE_ADMIN_LEXICON_RU = {
    "main_admin_menu": """🔐 Панель администратора\nДоступные функции:""",
    "fetched_places": (
        "🗺️ Фан-локации MU  \n\n"
        "✅ Проверенные места для просмотра матчей:  "
    ),
    "add_watching_place": (
        "➕ Добавление новой локации\n\n"
        "Шаг 1/3: Введите (название) места просмотра\n"  
        "(Например: Бар Red Devil, Паб United)\n\n"  
        "ℹ️ Можно использовать буквы, цифры и пробелы."
    ),
    "add_watching_place_step_2": (
        "✅ Принято: {place_name}\n\n"
        "Шаг 2/3: Введите полный адрес\n"
        "(Формат: ул. Советская, 15)\n\n" 
        "ℹ️ Укажите номер дома и этаж, если нужно."
    ),
    "add_watching_place_step_final": (
        "✅ Новая локация добавлена!\n\n"
        "Название: 🍺 {place_name}\n"  
        "Адрес: 🏠 {place_address}"
    ),
    "show_nearest_watching_days": (
        "🔴 Ближайшие фан-встречи MU  \n"
        "Выберите мероприятие для подробностей \n\n"
        "📍 Все встречи начинают сбор за 30 минут до матча"
    ),
    "edit_place_process": (
        "🛠 Управление локацией: «{place_name}» \n\n "
        "Выберите что хотите изменить:  "
    ),
    "edit_place_name_process": (
        "✏️ Переименование локации  \n\n"
        "Текущее название: «{old_place_name}»  \n"
        "Введите новое название (макс. 30 символов): "
    ),
    "edit_place_name": (
        "✏️ Название обновлено\n\n"
        "Старое: «{old_place_name}»\n"
        "Новое: «{new_place_name}»\n\n"    
        "✅ Изменения применены ко всем будущим встречам."
    ),
    "edit_address_place_process": (
        "📍 Новый адрес для «{place_name}»  \n\n"
        "Текущий адрес: {старый_адрес}  \n"
        "Введите новый адрес с указанием города: "
    ),
    "edit_place_address": (
        "🌍 Адрес обновлен\n\n"
        "Новый адрес: {new_place_address}"
    ),
    "delete_place": (
        "🗑 Локация удалена\n\n"
        "«{place_name}» больше не доступен для новых встреч.\n"
        "Все связанные будущие мероприятия переведены в статус 'Без локации'."
    ),
    "start_meeting_poll": (
        "📢 Опубликовано в чате!\n\n"
        "Участники сообщества уже выбирают:\n" 
        "✅ Приду\n" 
        "❌ Не смогу\n\n" 
        "Следите статистику в разделе «Участники»."  
    ),
    "process_change_watching_place": (
        "🔴 Переносим просмотр! \n\n "
        "Текущая локация: «{current_place}»  \n"
        "👇 Выберите новое место из списка:"
    ),
    "watching_place_changed": (
        "✅ Локация обновлена!\n\n " 
        "Теперь смотрим матч здесь:  \n"
        "📍 «{new_place}»  \n"
        "🏠 {address} \n\n" 
        "Участники получат уведомление об изменении."    
    ),
    # TODO: https://github.com/Rmnzm/kazan_reds/issues/28
    "process_cancel_meeting": (
        "❌ Встреча отменена  \n\n"
        "Матч: {localed_match_day_name}  \n"
        "Все участники ({count_registered_users} чел.) получили уведомление. "
    ),
    "process_show_visitors": (
        "👥 Состав на матч: {localed_match_day_name}  \n\n"
        "✅ Подтвердили участие ({confirmed_users_count}):\n  "
        "{confirmed_users}  \n\n"
        "❌ Не смогут прийти ({declined_users_count}):  \n"
        "{declined_users}  \n"
        "🔄 Ожидаем ответа от ({pending_users_count}):\n"
        "{pending_users}  "
    ),
}

ERROR_ADMIN_LEXICON_RU = {
    "error_show_users": "🔴 Не удалось загрузить список пользователей\nПопробуйте через 2-3 минуты",
    "error_show_places": "📍 Ошибка загрузки мест просмотра\nОбновите запрос или проверьте подключение",
    "error_adding_watching_place": "➕ Не удалось добавить новую локацию\nПроверьте формат данных и повторите",
    "error_show_nearest_watching_days": "📅 Ошибка получения расписания встреч\nСервер временно недоступен",
    "error_input_place_name": "✏️ Некорректное название места\nИспользуйте только буквы/цифры (макс. 30 символов)",
    "error_input_place_address": "📍 Ошибка в адресе\nУкажите в формате: Город, Улица, Дом",
    "failed_edit_place_process": "🛠 Ошибка изменения локации\nПопробуйте выбрать другое место",
    "failed_edit_place_name_process": "✏️ Сбой при переименовании\nПроверьте уникальность названия",
    "failed_edit_place_name": "⚠️ Название не изменено\nТакое имя уже существует или содержит ошибки",
    "failed_edit_address_place_process": "📍 Адрес не обновлен\nПроверьте правильность написания",
    "failed_edit_place_address": "🌍 Ошибка изменения адреса\nИспользуйте стандартный формат",
    "failed_delete_place": "🗑 Не удалось удалить локацию\nВозможно, она привязана к будущим встречам",
    "failed_process_scheduled_match_days_filter": "📅 Фильтр матчей не сработал\nПопробуйте другие параметры",
    "failed_start_meeting_poll": "📢 Ошибка создания опроса\nБот не имеет прав в целевом чате",
    "failed_process_change_watching_place": "🔄 Сбой при изменении локации\nПопробуйте выбрать снова",
    "failed_watching_place_changed": "⚠️ Место встречи не изменено\nПроверьте доступность локации",
    "failed_process_cancel_meeting": "❌ Не удалось отменить встречу\nУбедитесь, что она еще не началась",
    "failed_process_show_visitors": "👥 Ошибка загрузки участников\nДанные временно недоступны",
}

ADMIN_MATCH_INVITE_POLL_ANNOUCEMENT_LEXICON_RU = {
    "match_invitation": (
        "🔴⚪ *СБОР НА МАТЧ!* ⚪🔴\n\n"
        "🏆 *{tournament_name}*\n"
        "⚔️ *{located_match_day_name}*\n\n"
        "⏰ *{meeting_date}*\n"
        "📍 *{place_name}*\n"
        "🏠 {address}\n\n"
        "❗ *Сбор за 30 минут до начала*\n"
        "👇 Кто идёт? Отмечайтесь в комментариях!\n"
        "✅ Буду | ❌ Не смогу"
    )
}

ADMIN_MATCH_INVITE_POLL_OPTIONS = {
    "agree": "✅ Иду!",
    "cancel": "❌ Не смогу"
}

ADMIN_WATCH_DAY_HANDLER_LEXICON_RU = {
    "add_watch_day": "📅 Выберите матч для организации просмотра:",
    "choose_place": "📍 Где будем смотреть?\nДоступные локации:",
    "registrate_meeting": "🎉 Встреча создана!",
    "no_nearest_matches": "⏳ Ближайших матчей не найдено\nПопробуйте позже или добавьте вручную"
}

ADMIN_WATCH_DAY_HANDLER_ERROR_LEXICON_RU = {
    "add_watch_day_error": "⚠️ Не удалось загрузить список матчей\nПопробуйте через 5 минут",
    "choose_place_error": "🚫 Локация не выбрана\nПожалуйста, укажите место просмотра",
    "registrate_meeting_error": "❌ Встреча не создана\nПроверьте данные и повторите",
    "watch_day_register_error": "🔴 Ошибка регистрации встречи\nУбедитесь в корректности данных"
}

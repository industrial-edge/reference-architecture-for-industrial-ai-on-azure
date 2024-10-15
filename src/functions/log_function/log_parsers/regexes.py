class Regexes:

    # General regexes
    # Iso 8601 date format parser of the form [YYYY-MM-DDThh:mm:ss.dddZ]
    # Includes the []
    iso_datetime_regex = (
        r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}(?::?\d{2})?)\]"
    )

    # Severity string, one of
    # [C], [I], [D], [E] or [W]
    severity_regex = r"\[[CIDEW]?\]"

    # Thread id, looking for [thread xxx]
    thread_regex = r"\[thread \d+\]"

    # Message identifier, looking for message: or Message:
    message_regex = r"message: .*"

    # Model Distributor regexes
    # Created On - ISO Date format
    created_on_regex = (
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}(?::?\d{2})?)"
    )

    level_regex = r"\"level\":\"(.*?)\""

    # Message identifier, looking for "message": or "Message":
    model_distributor_message_regex = r'"message":"(.*?)"'

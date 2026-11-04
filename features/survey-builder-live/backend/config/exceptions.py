from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler


def flatten_errors(detail, prefix=""):
    if isinstance(detail, dict):
        messages = []
        for key, value in detail.items():
            label = f"{prefix}.{key}" if prefix else str(key)
            messages.extend(flatten_errors(value, label))
        return messages
    if isinstance(detail, (list, tuple)):
        messages = []
        for index, value in enumerate(detail):
            if isinstance(value, (dict, list, tuple)):
                label = f"{prefix}[{index}]" if prefix else f"[{index}]"
                messages.extend(flatten_errors(value, label))
            else:
                messages.append(f"{prefix}: {value}" if prefix else str(value))
        return messages
    return [f"{prefix}: {detail}" if prefix else str(detail)]


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None and isinstance(exc, ValidationError):
        response.data = {"detail": "; ".join(flatten_errors(exc.detail))}
    return response

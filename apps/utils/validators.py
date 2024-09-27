from django.conf import settings
from django.core.exceptions import ValidationError

def validate_file(file):
    # Validate file size
    if file.size > settings.MAX_FILE_SIZE:
        raise ValidationError("File size exceeds the limit of 5MB.")
    
    # Validate content type
    if file.content_type not in settings.UPLOAD_FILE_EXTENSIONS:
        raise ValidationError(f"Unsupported file type: {file.content_type}. Allowed types are JPEG, PNG, GIF, WebP.")
    
    # Validate file extension
    ext = file.name.split('.')[-1].lower()
    if f".{ext}" not in settings.UPLOAD_FILE_TYPES:
        raise ValidationError(f"Invalid file extension: .{ext}. Allowed extensions are: {', '.join(settings.UPLOAD_FILE_TYPES)}.")
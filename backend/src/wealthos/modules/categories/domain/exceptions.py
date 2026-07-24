"""Domain errors for the categories module."""


class CategoryError(Exception):
    """Base domain error for categories."""


class CategoryNameEmpty(CategoryError):
    """Raised when a category name is blank or too short."""


class CategoryNameTooLong(CategoryError):
    """Raised when a category name exceeds the allowed length."""


class InvalidCategoryType(CategoryError):
    """Raised when a category type is not supported."""


class CategoryNotFoundError(CategoryError):
    """Raised when the category cannot be found in the organization."""


class ParentCategoryNotFound(CategoryError):
    """Raised when the parent category does not exist."""


class ParentCategoryInactive(CategoryError):
    """Raised when the parent category is archived."""


class CategoryDepthExceeded(CategoryError):
    """Raised when attempting to nest beyond two levels."""


class CategoryTypeMismatch(CategoryError):
    """Raised when a child type differs from its parent."""


class DuplicateCategory(CategoryError):
    """Raised when a category already exists at the same level."""


class SystemCategoryCannotBeArchived(CategoryError):
    """Raised when archiving a system category."""


class CategoryHasActiveChildren(CategoryError):
    """Raised when archiving a category that still has active children."""


class CategoryAlreadyArchived(CategoryError):
    """Raised when archiving an already archived category."""

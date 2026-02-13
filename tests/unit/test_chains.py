import pytest
from unittest.mock import AsyncMock, patch
from src.services.linguistic.chains import analyze_word
from src.core.schemas import WordAssociation, AssociationType

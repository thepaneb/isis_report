"""
Status module router.
"""
from robyn import SubRouter

from constants import BASE_PATH


router = SubRouter(file_object=__file__, prefix=f"{BASE_PATH}/status")
